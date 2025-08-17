#!/usr/bin/env python3
"""
Emergency Position Protection Check
Directly queries Alpaca API to verify position protection status
"""

import asyncio
import os
import sys
from ..core.api_gateway import ResilientAlpacaGateway

async def check_position_protection():
    """Check if positions have stop loss protection"""
    
    # Initialize API gateway
    gateway = ResilientAlpacaGateway()
    
    try:
        print("🔍 Checking position protection status...")
        
        # Get current positions
        positions = await gateway.get_all_positions()
        active_positions = [pos for pos in positions if float(pos.qty) != 0]
        
        print(f"\n📊 Found {len(active_positions)} active positions:")
        for pos in active_positions:
            qty = float(pos.qty)
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl)
            unrealized_pct = float(pos.unrealized_plpc) * 100
            
            print(f"   {pos.symbol}: {qty} shares, ${market_value:,.2f} value, {unrealized_pct:+.1f}% P&L")
        
        if not active_positions:
            print("✅ No active positions found")
            return
            
        # Get all open orders
        print(f"\n🔍 Checking for protective orders...")
        open_orders = await gateway.get_orders('open')
        
        print(f"📋 Found {len(open_orders)} open orders:")
        
        # Check protection for each position
        unprotected_positions = []
        
        for position in active_positions:
            symbol = position.symbol
            qty = float(position.qty)
            position_side = 'long' if qty > 0 else 'short'
            
            # Find orders for this symbol
            symbol_orders = [order for order in open_orders if hasattr(order, 'symbol') and order.symbol == symbol]
            
            protective_orders = []
            for order in symbol_orders:
                order_type = getattr(order, 'type', '').lower()
                order_side = getattr(order, 'side', '').lower()
                stop_price = getattr(order, 'stop_price', None)
                limit_price = getattr(order, 'limit_price', None)
                order_id = getattr(order, 'id', 'unknown')
                
                # Check if this is a protective order
                is_stop = 'stop' in order_type or stop_price is not None
                is_protective_limit = (order_type == 'limit' and 
                                     ((position_side == 'long' and order_side == 'sell') or
                                      (position_side == 'short' and order_side == 'buy')))
                
                if is_stop or is_protective_limit:
                    price = stop_price if stop_price else limit_price
                    order_desc = f"{order_type} {order_side} @ ${price} (ID: {order_id})"
                    protective_orders.append(order_desc)
            
            if protective_orders:
                print(f"   ✅ {symbol}: PROTECTED by {len(protective_orders)} orders")
                for order_desc in protective_orders:
                    print(f"      - {order_desc}")
            else:
                print(f"   🚨 {symbol}: NO PROTECTION FOUND")
                unprotected_positions.append({
                    'symbol': symbol,
                    'qty': qty,
                    'market_value': float(position.market_value)
                })
        
        # Summary
        if unprotected_positions:
            print(f"\n🚨 CRITICAL: {len(unprotected_positions)} positions are UNPROTECTED:")
            total_unprotected_value = sum(pos['market_value'] for pos in unprotected_positions)
            
            for pos in unprotected_positions:
                print(f"   ❌ {pos['symbol']}: {pos['qty']} shares, ${pos['market_value']:,.2f}")
            
            print(f"\n💰 Total unprotected value: ${total_unprotected_value:,.2f}")
            print(f"🚨 These positions are exposed to unlimited risk!")
            
            return unprotected_positions
        else:
            print(f"\n✅ All {len(active_positions)} positions are protected")
            return []
    
    except Exception as e:
        print(f"❌ Error checking positions: {e}")
        return None
    
    finally:
        # Cleanup
        try:
            await gateway.close()
        except:
            pass

async def create_emergency_stops(unprotected_positions, gateway):
    """Create emergency stop orders for unprotected positions"""
    if not unprotected_positions:
        return
        
    print(f"\n🆘 Creating emergency stops for {len(unprotected_positions)} unprotected positions...")
    
    stops_created = 0
    
    for pos in unprotected_positions:
        try:
            symbol = pos['symbol']
            qty = abs(pos['qty'])
            current_price = pos['market_value'] / abs(pos['qty'])
            
            # 8% stop loss
            stop_price = round(current_price * 0.92, 2)
            
            emergency_stop_data = {
                'symbol': symbol,
                'qty': str(int(qty)),
                'side': 'sell',  # Assuming long positions
                'type': 'stop',
                'stop_price': str(stop_price),
                'time_in_force': 'day'
            }
            
            print(f"   📤 Creating stop for {symbol}: {qty} shares @ ${stop_price}")
            
            stop_response = await gateway.submit_order(emergency_stop_data)
            
            if stop_response:
                order_id = getattr(stop_response, 'id', 'unknown')
                print(f"   ✅ Emergency stop created for {symbol} (ID: {order_id})")
                stops_created += 1
            else:
                print(f"   ❌ Failed to create emergency stop for {symbol}")
                # Check account status for diagnostics
                try:
                    account = await gateway.get_account()
                    if account:
                        print(f"      Account status: Cash ${float(account.cash):.2f}, Buying Power ${float(account.buying_power):.2f}")
                    
                    clock = await gateway.get_clock()
                    if clock:
                        market_status = "OPEN" if clock.is_open else "CLOSED"
                        print(f"      Market status: {market_status}")
                        
                except Exception as diag_error:
                    print(f"      Could not get diagnostic info: {diag_error}")
                
        except Exception as e:
            print(f"   ❌ Error creating stop for {pos['symbol']}: {e}")
    
    print(f"\n📊 Emergency stop creation summary: {stops_created}/{len(unprotected_positions)} successful")
    
    if stops_created == 0:
        print("🚨 CRITICAL: NO emergency stops could be created!")
        print("   This indicates serious API/connectivity/authorization issues")
        print("   Manual intervention required immediately!")
    
    return stops_created

async def main():
    """Main function"""
    print("🚨 EMERGENCY POSITION PROTECTION CHECK")
    print("=" * 50)
    
    # Initialize API gateway
    gateway = ResilientAlpacaGateway()
    
    try:
        # Check current protection status
        unprotected_positions = await check_position_protection()
        
        if unprotected_positions is None:
            print("❌ Could not check position protection due to API error")
            return 1
        
        if unprotected_positions:
            print(f"\n🚨 ACTION REQUIRED: Creating emergency stops...")
            stops_created = await create_emergency_stops(unprotected_positions, gateway)
            
            if stops_created > 0:
                print(f"\n✅ Created {stops_created} emergency stops")
                # Verify protection again
                print(f"\n🔍 Re-checking protection status...")
                await asyncio.sleep(2)  # Wait for orders to be processed
                final_unprotected = await check_position_protection()
                
                if final_unprotected:
                    print(f"\n⚠️ {len(final_unprotected)} positions still unprotected after stop creation")
                    return 1
                else:
                    print(f"\n✅ All positions now protected!")
                    return 0
            else:
                print(f"\n🚨 CRITICAL: Could not create any emergency stops!")
                return 1
        else:
            print(f"\n✅ All positions are properly protected")
            return 0
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1
    
    finally:
        try:
            await gateway.close()
        except:
            pass

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)