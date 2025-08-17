#!/usr/bin/env python3
"""
Simple command-line tool to check market status and timezone information
"""

import asyncio
import logging
from ..data_management.market_status_manager import MarketStatusManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class MockGateway:
    """Mock gateway for testing"""
    pass

async def check_market_status():
    """Check current market status"""
    print("🕐 Market Status Checker")
    print("=" * 50)
    
    # Create market status manager
    market_status = MarketStatusManager(MockGateway())
    
    # Get current time information
    time_info = market_status.get_current_time_info()
    print("\n📅 Current Time Information:")
    print(f"   UTC Time: {time_info.get('utc_time', 'N/A')}")
    print(f"   Eastern Time: {time_info.get('eastern_time', 'N/A')}")
    print(f"   Local Time: {time_info.get('local_time', 'N/A')}")
    print(f"   Eastern Weekday: {time_info.get('eastern_weekday', 'N/A')}")
    print(f"   Eastern Hour: {time_info.get('eastern_hour', 'N/A')}")
    print(f"   Eastern Minute: {time_info.get('eastern_minute', 'N/A')}")
    
    # Check market status
    should_trade, reason = await market_status.should_start_trading()
    print(f"\n📈 Market Status:")
    print(f"   Should Start Trading: {should_trade}")
    print(f"   Reason: {reason}")
    
    # Check extended hours
    is_extended, period = market_status.is_extended_hours()
    print(f"\n🌙 Extended Hours:")
    print(f"   Is Extended Hours: {is_extended}")
    print(f"   Period: {period}")
    
    # Check extended hours trading
    should_trade_extended = market_status.should_trade_extended_hours()
    print(f"   Should Trade Extended Hours: {should_trade_extended}")
    
    # Check extended hours trading permission
    should_trade_extended_active = await market_status.should_trade_extended_hours()
    print(f"   Should Trade Extended Hours (Active): {should_trade_extended_active}")
    
    # Get strategy adjustments
    adjustments = market_status.get_extended_hours_strategy_adjustments()
    print(f"\n📊 Strategy Adjustments:")
    if adjustments:
        for key, value in adjustments.items():
            print(f"   {key}: {value}")
    else:
        print("   No adjustments (regular market hours)")
    
    # Get allowed order types
    order_types = market_status.get_allowed_order_types()
    print(f"\n📋 Allowed Order Types:")
    print(f"   {', '.join(order_types)}")
    
    # Summary
    print(f"\n🎯 Summary:")
    if should_trade:
        print("   ✅ MARKET IS OPEN - Ready to trade!")
    elif should_trade_extended_active:
        print("   🌙 EXTENDED HOURS - Trading with restrictions")
    else:
        print("   ⏰ MARKET CLOSED - Waiting for open")
    
    print(f"\n💡 Tip: If times seem wrong, check your system timezone and ensure pytz is installed")

async def main():
    """Main function"""
    try:
        await check_market_status()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure pytz is installed: pip install pytz")
        print("   2. Check your system timezone")
        print("   3. Verify internet connection for timezone data")
        raise

if __name__ == "__main__":
    asyncio.run(main())
