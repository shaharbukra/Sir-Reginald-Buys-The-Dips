#!/usr/bin/env python3
"""
Test script to verify P&L calculation fix
"""

import asyncio
import json
from performance_tracker import PerformanceTracker
from api_gateway import ResilientAlpacaGateway

async def test_pnl_fix():
    """Test the P&L calculation fix"""
    print("🧪 Testing P&L Calculation Fix")
    print("=" * 50)
    
    try:
        # Initialize API gateway
        gateway = ResilientAlpacaGateway()
        if not await gateway.initialize():
            print("❌ Failed to initialize API gateway")
            return
        
        # Initialize performance tracker
        tracker = PerformanceTracker(gateway)
        await tracker.initialize()
        
        print(f"📊 Current Performance Data:")
        print(f"   Initial Value: ${tracker.initial_value:,.2f}")
        
        # Get current performance
        daily_summary = await tracker.get_daily_summary()
        
        print(f"   Current Equity: ${daily_summary.get('current_equity', 0):,.2f}")
        print(f"   Total P&L: ${daily_summary.get('total_pnl', 0):+.2f}")
        print(f"   Total P&L %: {daily_summary.get('total_pnl_pct', 0):+.2f}%")
        
        # Test the reset functionality
        print(f"\n🔄 Testing Reset Functionality:")
        print(f"   Resetting initial value to $35,000.00...")
        
        success = tracker.reset_initial_value(35000.00)
        if success:
            print(f"   ✅ Reset successful!")
            
            # Get updated performance
            updated_summary = await tracker.get_daily_summary()
            
            print(f"\n📊 Updated Performance Data:")
            print(f"   Initial Value: ${tracker.initial_value:,.2f}")
            print(f"   Current Equity: ${updated_summary.get('current_equity', 0):,.2f}")
            print(f"   Total P&L: ${updated_summary.get('total_pnl', 0):+.2f}")
            print(f"   Total P&L %: {updated_summary.get('total_pnl_pct', 0):+.2f}%")
            
            # Verify the calculation makes sense now
            expected_pnl = updated_summary.get('current_equity', 0) - 35000.00
            expected_pnl_pct = (expected_pnl / 35000.00) * 100
            
            print(f"\n✅ Verification:")
            print(f"   Expected P&L: ${expected_pnl:+.2f}")
            print(f"   Expected P&L %: {expected_pnl_pct:+.2f}%")
            print(f"   Actual P&L: ${updated_summary.get('total_pnl', 0):+.2f}")
            print(f"   Actual P&L %: {updated_summary.get('total_pnl_pct', 0):+.2f}%")
            
            if abs(expected_pnl - updated_summary.get('total_pnl', 0)) < 0.01:
                print(f"   🎯 P&L calculation is now correct!")
            else:
                print(f"   ⚠️ P&L calculation still has issues")
        else:
            print(f"   ❌ Reset failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Cleanup
        if 'gateway' in locals():
            await gateway.shutdown()

if __name__ == "__main__":
    asyncio.run(test_pnl_fix())
