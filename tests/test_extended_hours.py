#!/usr/bin/env python3
"""
Test script for Extended Hours Trading functionality
"""

import asyncio
import logging
from datetime import datetime, time
from market_status_manager import MarketStatusManager
from extended_hours_trader import ExtendedHoursTrader

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockGateway:
    """Mock gateway for testing"""
    async def get_top_movers(self, limit=50):
        return type('MockResponse', (), {
            'success': True,
            'data': [
                {'symbol': 'AAPL', 'change_percent': 2.5, 'volume': 1500000},
                {'symbol': 'TSLA', 'change_percent': -1.8, 'volume': 800000},
                {'symbol': 'NVDA', 'change_percent': 3.2, 'volume': 2000000},
                {'symbol': 'AMD', 'change_percent': 1.5, 'volume': 1200000},
                {'symbol': 'META', 'change_percent': -0.8, 'volume': 900000}
            ]
        })()
    
    async def get_quote(self, symbol):
        return type('MockQuote', (), {
            'success': True,
            'data': type('MockQuoteData', (), {
                'ask_price': 150.0,
                'bid_price': 149.5
            })()
        })()
    
    async def get_account_safe(self):
        return type('MockAccount', (), {
            'equity': 10000.0
        })()
    
    async def submit_order(self, order_data):
        return type('MockOrder', (), {
            'success': True,
            'data': type('MockOrderData', (), {
                'id': 'mock_order_123'
            })()
        })()

class MockRiskManager:
    """Mock risk manager for testing"""
    async def initialize(self, account_value):
        pass

async def test_extended_hours_detection():
    """Test extended hours detection"""
    logger.info("🧪 Testing Extended Hours Detection...")
    
    # Create mock components
    mock_gateway = MockGateway()
    mock_risk_manager = MockRiskManager()
    
    # Test market status manager
    market_status = MarketStatusManager(mock_gateway)
    
    # Test different times
    test_times = [
        (time(4, 30), "Pre-market"),
        (time(9, 0), "Pre-market"),
        (time(10, 0), "Regular hours"),
        (time(16, 30), "After-hours"),
        (time(19, 0), "After-hours"),
        (time(22, 0), "Overnight"),
        (time(2, 0), "Overnight")
    ]
    
    for test_time, expected_period in test_times:
        # Mock current time
        original_now = datetime.now
        datetime.now = lambda: datetime.combine(datetime.today().date(), test_time)
        
        try:
            is_extended, period = market_status.is_extended_hours()
            should_trade = market_status.should_trade_extended_hours()
            
            logger.info(f"⏰ {test_time.strftime('%H:%M')} - {period}")
            logger.info(f"   Extended hours: {is_extended}")
            logger.info(f"   Should trade: {should_trade}")
            
            # Verify expected behavior
            if "Pre-market" in expected_period or "After-hours" in expected_period:
                assert is_extended, f"Expected extended hours for {test_time}"
                assert should_trade, f"Expected trading enabled for {test_time}"
            elif "Regular" in expected_period:
                assert not is_extended, f"Expected regular hours for {test_time}"
                assert not should_trade, f"Expected trading disabled for {test_time}"
                
        finally:
            # Restore original datetime.now
            datetime.now = original_now
    
    logger.info("✅ Extended hours detection tests passed!")

async def test_extended_hours_trader():
    """Test extended hours trader functionality"""
    logger.info("🧪 Testing Extended Hours Trader...")
    
    # Create mock components
    mock_gateway = MockGateway()
    mock_risk_manager = MockRiskManager()
    market_status = MarketStatusManager(mock_gateway)
    
    # Create extended hours trader
    trader = ExtendedHoursTrader(mock_gateway, mock_risk_manager, market_status)
    
    # Mock pre-market time
    original_now = datetime.now
    datetime.now = lambda: datetime.combine(datetime.today().date(), time(5, 0))
    
    try:
        # Test opportunity scanning
        opportunities = await trader.get_extended_hours_opportunities()
        logger.info(f"📊 Found {len(opportunities)} opportunities")
        
        assert len(opportunities) > 0, "Expected to find opportunities"
        
        # Test opportunity filtering
        for opp in opportunities:
            logger.info(f"   {opp['symbol']}: {opp['change_pct']:.1f}% change, Score: {opp['score']:.1f}")
            assert 'symbol' in opp, "Opportunity missing symbol"
            assert 'score' in opp, "Opportunity missing score"
        
        # Test trade execution
        if opportunities:
            success = await trader.execute_extended_hours_trade(opportunities[0])
            logger.info(f"🎯 Trade execution: {'✅ Success' if success else '❌ Failed'}")
            
            # Test position monitoring
            await trader.monitor_extended_hours_positions()
            
            # Test cleanup
            await trader.cleanup_overnight_positions()
            
    finally:
        # Restore original datetime.now
        datetime.now = original_now
    
    logger.info("✅ Extended hours trader tests passed!")

async def test_strategy_adjustments():
    """Test strategy adjustments for extended hours"""
    logger.info("🧪 Testing Strategy Adjustments...")
    
    mock_gateway = MockGateway()
    market_status = MarketStatusManager(mock_gateway)
    
    # Test pre-market adjustments
    original_now = datetime.now
    datetime.now = lambda: datetime.combine(datetime.today().date(), time(5, 0))
    
    try:
        adjustments = market_status.get_extended_hours_strategy_adjustments()
        logger.info(f"📊 Pre-market strategy adjustments: {adjustments}")
        
        assert 'max_position_size_pct' in adjustments, "Missing position size adjustment"
        assert 'use_limit_orders_only' in adjustments, "Missing order type adjustment"
        assert adjustments['max_position_size_pct'] == 0.03, "Expected 3% position size"
        assert adjustments['use_limit_orders_only'] == True, "Expected limit orders only"
        
    finally:
        datetime.now = original_now
    
    # Test after-hours adjustments
    datetime.now = lambda: datetime.combine(datetime.today().date(), time(17, 0))
    
    try:
        adjustments = market_status.get_extended_hours_strategy_adjustments()
        logger.info(f"📊 After-hours strategy adjustments: {adjustments}")
        
        assert 'max_position_size_pct' in adjustments, "Missing position size adjustment"
        assert adjustments['max_position_size_pct'] == 0.03, "Expected 3% position size"
        
    finally:
        datetime.now = original_now
    
    logger.info("✅ Strategy adjustments tests passed!")

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Extended Hours Trading Tests...")
    
    try:
        await test_extended_hours_detection()
        await test_extended_hours_trader()
        await test_strategy_adjustments()
        
        logger.info("🎉 All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
