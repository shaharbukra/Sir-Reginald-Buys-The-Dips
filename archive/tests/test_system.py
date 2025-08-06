#!/usr/bin/env python3
"""
Comprehensive test suite for AI-Driven Trading System
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import system modules
from config import *
from intelligent_funnel import IntelligentMarketFunnel, MarketOpportunity, RateLimitTracker
from ai_market_intelligence import EnhancedAIAssistant, MarketIntelligence
from enhanced_momentum_strategy import EventDrivenMomentumStrategy, TradingSignal
from risk_manager import ConservativeRiskManager, RiskAssessment
from order_executor import SimpleTradeExecutor
from api_gateway import ResilientAlpacaGateway, ApiResponse

class TestConfiguration:
    """Test configuration validation and parameters"""
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        # Test with missing API keys (should fail)
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                validate_configuration()
                
    def test_market_regime_enum(self):
        """Test market regime enumeration"""
        assert MarketRegime.BULL_TRENDING.value == "bull_trending"
        assert MarketRegime.BEAR_TRENDING.value == "bear_trending"
        assert MarketRegime.VOLATILE_RANGE.value == "volatile_range"
        
    def test_risk_parameters(self):
        """Test risk parameter bounds"""
        assert RISK_CONFIG['max_position_risk_pct'] <= 5.0
        assert RISK_CONFIG['max_daily_drawdown_pct'] <= 10.0
        assert RISK_CONFIG['stop_loss_pct'] > 0
        assert RISK_CONFIG['take_profit_multiple'] >= 2.0

class TestMarketOpportunity:
    """Test MarketOpportunity data structure"""
    
    def test_opportunity_creation(self):
        """Test creating market opportunity"""
        opp = MarketOpportunity(
            symbol="AAPL",
            discovery_source="market_gainers",
            discovery_timestamp=datetime.now(),
            current_price=150.0,
            daily_change_pct=5.0,
            volume=50000000,
            avg_volume=25000000,
            volume_ratio=2.0,
            market_cap=2500000000000,
            sector="TECHNOLOGY"
        )
        
        assert opp.symbol == "AAPL"
        assert opp.volume_ratio == 2.0
        assert opp.opportunity_score == 0.0  # Default value
        
    def test_opportunity_scoring(self):
        """Test opportunity scoring logic"""
        opp = MarketOpportunity(
            symbol="NVDA",
            discovery_source="unusual_volume",
            discovery_timestamp=datetime.now(),
            current_price=400.0,
            daily_change_pct=8.0,
            volume=75000000,
            avg_volume=25000000,
            volume_ratio=3.0,
            market_cap=1000000000000,
            sector="TECHNOLOGY"
        )
        
        # High volume ratio and price change should score well
        assert opp.volume_ratio > 2.0
        assert opp.daily_change_pct > 5.0

class TestRateLimitTracker:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def rate_tracker(self):
        return RateLimitTracker()
        
    def test_rate_limit_initialization(self, rate_tracker):
        """Test rate limiter initialization"""
        assert len(rate_tracker.request_history) == 0
        assert rate_tracker.used_budget['discovery'] == 0
        
    def test_can_make_request(self, rate_tracker):
        """Test rate limit checking"""
        # Should be able to make request initially
        assert rate_tracker.can_make_request('discovery', priority=4)
        
        # Record requests up to budget
        budget = rate_tracker.budget_allocation.get('discovery', 30)
        for _ in range(budget):
            rate_tracker.record_request('discovery')
            
        # Should not be able to make more requests
        assert not rate_tracker.can_make_request('discovery', priority=4)
        
    def test_budget_reset(self, rate_tracker):
        """Test budget reset functionality"""
        rate_tracker.record_request('discovery')
        assert rate_tracker.used_budget['discovery'] == 1
        
        rate_tracker.reset_budgets()
        assert rate_tracker.used_budget['discovery'] == 0

class TestIntelligentFunnel:
    """Test intelligent market funnel"""
    
    @pytest.fixture
    def mock_gateway(self):
        gateway = Mock()
        gateway.get_bars = AsyncMock(return_value=[])
        return gateway
        
    @pytest.fixture
    def mock_ai_assistant(self):
        ai = Mock()
        ai.generate_daily_market_intelligence = AsyncMock()
        return ai
        
    @pytest.fixture
    def funnel(self, mock_gateway, mock_ai_assistant):
        return IntelligentMarketFunnel(mock_gateway, mock_ai_assistant)
        
    def test_funnel_initialization(self, funnel):
        """Test funnel initialization"""
        assert funnel.scanning_active == False
        assert len(funnel.current_watchlist) == 0
        assert funnel.market_regime == MarketRegime.BULL_TRENDING
        
    def test_deduplicate_candidates(self, funnel):
        """Test candidate deduplication"""
        candidates = [
            MarketOpportunity("AAPL", "market_gainers", datetime.now(), 150.0, 5.0, 1000, 500, 2.0, 1e12, "TECH"),
            MarketOpportunity("AAPL", "most_active", datetime.now(), 150.0, 5.0, 1000, 500, 2.0, 1e12, "TECH"),
            MarketOpportunity("MSFT", "market_gainers", datetime.now(), 300.0, 3.0, 800, 400, 2.0, 2e12, "TECH")
        ]
        
        unique = funnel._deduplicate_candidates(candidates)
        assert len(unique) == 2  # AAPL and MSFT
        
        # Should keep higher priority source (market_gainers over most_active)
        aapl_candidate = next(c for c in unique if c.symbol == "AAPL")
        assert aapl_candidate.discovery_source == "market_gainers"
        
    def test_basic_filters(self, funnel):
        """Test basic screening filters"""
        candidates = [
            MarketOpportunity("GOOD", "test", datetime.now(), 50.0, 5.0, 1000000, 500000, 2.0, 1e9, "TECH"),
            MarketOpportunity("LOW_PRICE", "test", datetime.now(), 2.0, 5.0, 1000000, 500000, 2.0, 1e9, "TECH"),
            MarketOpportunity("LOW_VOLUME", "test", datetime.now(), 50.0, 5.0, 100000, 50000, 2.0, 1e9, "TECH"),
            MarketOpportunity("LOW_CAP", "test", datetime.now(), 50.0, 5.0, 1000000, 500000, 2.0, 100e6, "TECH")
        ]
        
        filtered = funnel._apply_basic_filters(candidates)
        assert len(filtered) == 1  # Only "GOOD" should pass
        assert filtered[0].symbol == "GOOD"

class TestAIAssistant:
    """Test AI assistant functionality"""
    
    @pytest.fixture
    def ai_assistant(self):
        return EnhancedAIAssistant()
        
    def test_ai_initialization(self, ai_assistant):
        """Test AI assistant initialization"""
        assert ai_assistant.api_url == AI_CONFIG['ollama_url']
        assert ai_assistant.model == AI_CONFIG['model_name']
        assert ai_assistant.daily_intelligence is None
        
    def test_json_parsing_robust(self, ai_assistant):
        """Test robust JSON parsing"""
        # Test valid JSON
        response = {"response": '{"test": "value"}'}
        result = ai_assistant._parse_json_response_robust(response)
        assert result == {"test": "value"}
        
        # Test JSON with extra text
        response = {"response": 'Some text before {"test": "value"} some text after'}
        result = ai_assistant._parse_json_response_robust(response)
        assert result == {"test": "value"}
        
        # Test invalid JSON
        response = {"response": 'invalid json'}
        result = ai_assistant._parse_json_response_robust(response)
        assert result == {}
        
    def test_fallback_intelligence(self, ai_assistant):
        """Test fallback market intelligence"""
        intelligence = ai_assistant._get_fallback_intelligence()
        
        assert isinstance(intelligence, MarketIntelligence)
        assert intelligence.market_regime == "BULL_TRENDING"
        assert intelligence.volatility_environment == "NORMAL"
        assert intelligence.confidence == 0.5

class TestMomentumStrategy:
    """Test momentum trading strategy"""
    
    @pytest.fixture
    def strategy(self):
        return EventDrivenMomentumStrategy()
        
    def test_strategy_initialization(self, strategy):
        """Test strategy initialization"""
        assert strategy.signals_generated == 0
        assert strategy.strategy_config == STRATEGY_CONFIG['momentum_strategy']
        
    def test_bars_to_dataframe(self, strategy):
        """Test bar data conversion"""
        bars = [
            {'t': '2024-01-01T09:30:00Z', 'o': 100, 'h': 105, 'l': 99, 'c': 103, 'v': 1000000},
            {'t': '2024-01-02T09:30:00Z', 'o': 103, 'h': 108, 'l': 102, 'c': 106, 'v': 1200000}
        ]
        
        df = strategy._bars_to_dataframe(bars)
        
        assert len(df) == 2
        assert 'close' in df.columns
        assert df.iloc[0]['close'] == 103.0
        assert df.iloc[1]['close'] == 106.0
        
    def test_rsi_calculation(self, strategy):
        """Test RSI calculation"""
        import pandas as pd
        
        # Create test price series
        prices = pd.Series([100, 102, 101, 105, 104, 108, 107, 110, 109, 112, 
                           111, 115, 114, 116, 115, 118, 117, 120, 119, 122])
        
        rsi = strategy._calculate_rsi(prices, period=14)
        
        # RSI should be between 0 and 100
        assert all(0 <= r <= 100 for r in rsi.dropna())
        # Should have some valid values
        assert len(rsi.dropna()) > 0

class TestRiskManager:
    """Test risk management system"""
    
    @pytest.fixture
    def risk_manager(self):
        rm = ConservativeRiskManager()
        asyncio.run(rm.initialize(10000.0))
        return rm
        
    @pytest.fixture
    def sample_signal(self):
        return TradingSignal(
            symbol="AAPL",
            action="BUY",
            signal_type="MOMENTUM",
            entry_price=150.0,
            stop_loss_price=140.0,
            take_profit_price=165.0,
            position_size_pct=2.0,
            confidence=0.8,
            reasoning="Test signal",
            timestamp=datetime.now(),
            risk_reward_ratio=1.5
        )
        
    def test_risk_manager_initialization(self, risk_manager):
        """Test risk manager initialization"""
        assert risk_manager.initial_account_value == 10000.0
        assert risk_manager.daily_trades == 0
        
    @pytest.mark.asyncio
    async def test_position_risk_assessment(self, risk_manager, sample_signal):
        """Test position risk assessment"""
        assessment = await risk_manager.assess_position_risk(
            sample_signal, 10000.0, []
        )
        
        assert isinstance(assessment, RiskAssessment)
        assert assessment.risk_score >= 0.0
        assert assessment.max_position_size >= 0.0
        
    @pytest.mark.asyncio
    async def test_daily_drawdown_check(self, risk_manager):
        """Test daily drawdown monitoring"""
        # Test normal case
        exceeded = await risk_manager.check_daily_drawdown(9800.0)  # 2% down
        assert not exceeded
        
        # Test drawdown limit exceeded
        exceeded = await risk_manager.check_daily_drawdown(9300.0)  # 7% down
        assert exceeded  # Should exceed 6% limit
        
    @pytest.mark.asyncio 
    async def test_trade_validation(self, risk_manager, sample_signal):
        """Test trade execution validation"""
        valid = await risk_manager.validate_trade_execution(sample_signal, 10000.0)
        assert isinstance(valid, bool)

class TestOrderExecutor:
    """Test order execution system"""
    
    @pytest.fixture
    def mock_gateway(self):
        gateway = Mock()
        gateway.submit_order = AsyncMock()
        gateway.get_all_positions = AsyncMock(return_value=[])
        gateway.cancel_all_orders = AsyncMock(return_value=True)
        return gateway
        
    @pytest.fixture
    def mock_risk_manager(self):
        rm = Mock()
        rm.validate_trade_execution = AsyncMock(return_value=True)
        rm.record_trade_execution = AsyncMock()
        return rm
        
    @pytest.fixture
    def executor(self, mock_gateway, mock_risk_manager):
        return SimpleTradeExecutor(mock_gateway, mock_risk_manager)
        
    @pytest.fixture
    def sample_signal(self):
        return TradingSignal(
            symbol="AAPL",
            action="BUY",
            signal_type="MOMENTUM",
            entry_price=150.0,
            stop_loss_price=140.0,
            take_profit_price=165.0,
            position_size_pct=2.0,
            confidence=0.8,
            reasoning="Test signal",
            timestamp=datetime.now(),
            risk_reward_ratio=1.5
        )
        
    def test_executor_initialization(self, executor):
        """Test executor initialization"""
        assert len(executor.active_orders) == 0
        assert len(executor.executed_trades) == 0
        
    @pytest.mark.asyncio
    async def test_position_monitoring(self, executor):
        """Test position monitoring"""
        summary = await executor.monitor_positions()
        
        assert 'active_positions' in summary
        assert 'open_orders' in summary
        assert 'total_unrealized_pnl' in summary

class TestApiGateway:
    """Test API gateway functionality"""
    
    @pytest.fixture
    def gateway(self):
        return ResilientAlpacaGateway()
        
    def test_gateway_initialization(self, gateway):
        """Test gateway initialization"""
        assert gateway.session is None
        assert gateway.consecutive_failures == 0
        
    def test_api_response_creation(self):
        """Test API response wrapper"""
        response = ApiResponse(success=True, data={"test": "data"})
        assert response.success
        assert response.data == {"test": "data"}
        assert response.error is None
        
    def test_parse_account_data(self, gateway):
        """Test account data parsing"""
        test_data = {
            'equity': '10000.50',
            'cash': '5000.25',
            'buying_power': '20000.00',
            'day_trade_count': 2
        }
        
        account = gateway._parse_account_data(test_data)
        assert account.equity == '10000.50'
        assert account.cash == '5000.25'
        assert account.day_trade_count == 2

@pytest.mark.asyncio
async def test_system_integration():
    """Integration test for core system components"""
    
    # Test that all components can be imported and initialized
    try:
        # Mock environment variables
        with patch.dict(os.environ, {
            'APCA_API_KEY_ID': 'test_key',
            'APCA_API_SECRET_KEY': 'test_secret'
        }):
            
            # Test configuration
            validate_configuration()
            
            # Test component initialization
            gateway = ResilientAlpacaGateway()
            ai_assistant = EnhancedAIAssistant()
            funnel = IntelligentMarketFunnel(gateway, ai_assistant)
            strategy = EventDrivenMomentumStrategy()
            risk_manager = ConservativeRiskManager()
            
            # Test risk manager initialization
            await risk_manager.initialize(10000.0)
            
            # Test component interactions
            assert funnel.gateway == gateway
            assert funnel.ai_assistant == ai_assistant
            assert risk_manager.initial_account_value == 10000.0
            
    except Exception as e:
        pytest.fail(f"System integration test failed: {e}")

def run_tests():
    """Run all tests"""
    print("🧪 Running AI-Driven Trading System Tests...")
    
    # Run pytest with verbose output
    pytest_args = [
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        "-x",  # Stop on first failure
    ]
    
    result = pytest.main(pytest_args)
    
    if result == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        
    return result

if __name__ == "__main__":
    run_tests()