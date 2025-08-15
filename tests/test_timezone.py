#!/usr/bin/env python3
"""
Test script for timezone handling in market status manager
"""

import asyncio
import logging
from market_status_manager import MarketStatusManager

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MockGateway:
    """Mock gateway for testing"""
    pass

async def test_timezone_handling():
    """Test timezone handling and market hours detection"""
    logger.info("🧪 Testing Timezone Handling...")
    
    # Create market status manager
    market_status = MarketStatusManager(MockGateway())
    
    # Get current time information
    time_info = market_status.get_current_time_info()
    logger.info("🕐 Current Time Information:")
    for key, value in time_info.items():
        logger.info(f"   {key}: {value}")
    
    # Test market status
    should_trade, reason = await market_status.should_start_trading()
    logger.info(f"📈 Should Start Trading: {should_trade}")
    logger.info(f"📈 Reason: {reason}")
    
    # Test extended hours detection
    is_extended, period = market_status.is_extended_hours()
    logger.info(f"🌙 Extended Hours: {is_extended}")
    logger.info(f"🌙 Period: {period}")
    
    # Test extended hours trading
    should_trade_extended = market_status.should_trade_extended_hours()
    logger.info(f"🌙 Should Trade Extended Hours: {should_trade_extended}")
    
    # Test extended hours trading permission
    should_trade_extended_active = await market_status.should_trade_extended_hours()
    logger.info(f"🌙 Should Trade Extended Hours (Active): {should_trade_extended_active}")
    
    # Get strategy adjustments
    adjustments = market_status.get_extended_hours_strategy_adjustments()
    logger.info(f"📊 Strategy Adjustments: {adjustments}")
    
    # Get allowed order types
    order_types = market_status.get_allowed_order_types()
    logger.info(f"📋 Allowed Order Types: {order_types}")

async def main():
    """Run the test"""
    try:
        await test_timezone_handling()
        logger.info("✅ Timezone test completed successfully!")
    except Exception as e:
        logger.error(f"❌ Timezone test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
