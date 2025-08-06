#!/usr/bin/env python3
"""
Test script to verify the performance tracking fix
This will show REAL vs FAKE performance data
"""

import asyncio
import sys
from api_gateway import ResilientAlpacaGateway
from performance_tracker import PerformanceTracker

async def test_real_performance():
    """Test the new performance tracking with real Alpaca data"""
    
    print("🔍 Testing REAL Performance Tracking Fix...")
    print("=" * 50)
    
    # Initialize gateway
    gateway = ResilientAlpacaGateway()
    success = await gateway.initialize()
    
    if not success:
        print("❌ Failed to connect to Alpaca API")
        return
    
    print("✅ Connected to Alpaca API")
    
    # Get actual account data
    account = await gateway.get_account_safe()
    if not account:
        print("❌ Could not get account data")
        return
        
    print(f"📊 REAL Account Data from Alpaca:")
    print(f"   Current Equity: ${float(account.equity):,.2f}")
    print(f"   Last Equity: ${float(account.last_equity):,.2f}")
    print(f"   Buying Power: ${float(account.buying_power):,.2f}")
    print(f"   Cash: ${float(account.cash):,.2f}")
    print()
    
    # Test new performance tracker
    performance_tracker = PerformanceTracker(gateway)
    success = await performance_tracker.initialize()
    
    if not success:
        print("❌ Performance tracker initialization failed")
        return
        
    print("✅ Performance tracker initialized")
    
    # Get real performance summary
    summary = await performance_tracker.get_daily_summary()
    
    print(f"💰 REAL Performance Summary:")
    if 'error' in summary:
        print(f"   ❌ Error: {summary['error']}")
    else:
        print(f"   Current Equity: ${summary['current_equity']:,.2f}")
        print(f"   Daily P&L: ${summary['daily_pnl']:+.2f} ({summary['daily_pnl_pct']:+.2f}%)")
        print(f"   Total P&L: ${summary['total_pnl']:+.2f} ({summary['total_pnl_pct']:+.2f}%)")
    print()
    
    # Get positions summary
    positions = await performance_tracker.get_positions_summary()
    
    print(f"📍 Current Positions (Real Data):")
    if 'error' in positions:
        print(f"   ❌ Error: {positions['error']}")
    else:
        print(f"   Total Positions: {positions['total_positions']}")
        print(f"   Total Market Value: ${positions['total_market_value']:,.2f}")
        print(f"   Total Unrealized P&L: ${positions['total_unrealized_pnl']:+.2f}")
        
        for pos in positions['positions']:
            color = "🟢" if pos['unrealized_pnl'] >= 0 else "🔴"
            print(f"   {color} {pos['symbol']}: {pos['quantity']} shares, "
                  f"${pos['unrealized_pnl']:+.2f} ({pos['unrealized_pnl_pct']:+.1f}%)")
    
    await gateway.shutdown()
    print("\n✅ Test completed!")

if __name__ == "__main__":
    try:
        asyncio.run(test_real_performance())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")