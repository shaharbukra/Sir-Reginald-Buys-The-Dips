# -*- coding: utf-8 -*-
"""
Complete configuration for intelligent market-wide trading system
Optimized for API efficiency and maximum market coverage
"""

import os
from typing import List, Dict, Optional
from enum import Enum
from datetime import time

class TradingPhase(Enum):
    FOUNDATION = 1
    BACKTESTING = 1.5
    PAPER_TRADING = 2
    AI_ENHANCEMENT = 3
    LIVE_TRADING = 4

class MarketRegime(Enum):
    BULL_TRENDING = "bull_trending"
    BEAR_TRENDING = "bear_trending" 
    VOLATILE_RANGE = "volatile_range"
    SECTOR_ROTATION = "sector_rotation"
    LOW_VOLATILITY = "low_volatility"

# === SYSTEM CONFIGURATION ===
SYSTEM_CONFIG = {
    'current_phase': TradingPhase.FOUNDATION,
    'paper_trading_mandatory': True,
    'min_paper_trading_days': 30,
    'min_profitable_trades': 50,
    'required_win_rate': 0.55,
    'required_profit_factor': 1.3,
    'max_daily_trades': 8,
    'enable_intelligent_funnel': True
}

# === API CONFIGURATION ===
API_CONFIG = {
    'alpaca_key_id': os.getenv('APCA_API_KEY_ID'),
    'alpaca_secret_key': os.getenv('APCA_API_SECRET_KEY'),
    'paper_trading': True,
    'request_timeout': 15,
    'max_retries': 3,
    'retry_backoff_factor': 2,
    'websocket_heartbeat_interval': 30,
    'enable_extended_hours_trading': True,  # Enable pre-market and after-hours trading
    'extended_hours_start': '04:00',        # 4:00 AM ET
    'extended_hours_end': '20:00',          # 8:00 PM ET
    # Stale data thresholds (in minutes)
    'stale_data_warning_minutes': 5,        # Warning threshold for regular hours
    'stale_data_rejection_minutes': 15,     # Rejection threshold for regular hours
    'extended_hours_warning_minutes': 30,   # Warning threshold for extended hours
    'extended_hours_rejection_minutes': 60  # Rejection threshold for extended hours
}

# === INTELLIGENT FUNNEL CONFIGURATION ===
FUNNEL_CONFIG = {
    # Step 1: Broad Scan (2-5 API calls total)
    'broad_scan_apis': {
        'market_movers': True,          # Top gainers/losers
        'most_active': True,            # Volume leaders
        'unusual_volume': True,         # Volume anomalies
        'sector_movers': True,          # Sector rotation
        'news_movers': True,            # News-driven moves
        'comprehensive_scan': False     # Full market scan - temporarily disabled for speed testing
    },
    
    # Broad scan parameters
    'max_broad_scan_results': 500,     # Max candidates from Step 1 - increased for comprehensive scanning
    'broad_scan_frequency_minutes': 15, # Full scan every 15 minutes
    'broad_scan_api_budget': 5,        # Max API calls for broad scan
    
    # Step 2: AI Filtering (0 API calls - pure logic)
    'ai_filtering': {
        'market_regime_analysis': True,
        'sector_preference_filtering': True,
        'technical_pre_screening': True,
        'news_sentiment_filtering': True
    },
    
    # Step 3: Deep Dive (expanded for comprehensive analysis)
    'deep_dive_candidates': 100,       # Max stocks for deep analysis - increased significantly
    'deep_dive_api_budget': 20,        # API calls for detailed analysis
    'deep_dive_components': {
        'detailed_technicals': True,
        'news_analysis': True,
        'options_flow': True,
        'insider_activity': False,      # Future enhancement
        'analyst_ratings': False        # Future enhancement
    },
    
    # Final selection
    'max_watchlist_size': 25,          # Dynamic watchlist size
    'max_active_positions': 8,         # Concurrent positions
    'opportunity_refresh_minutes': 5   # Update rankings every 5 min
}

# === MARKET-WIDE SCREENING CRITERIA ===
SCREENING_CRITERIA = {
    # Base filters (applied to all scans)
    'min_price': 5.0,
    'max_price': 1000.0,
    'min_market_cap': 500000000,       # $500M minimum
    'min_avg_volume': 500000,          # 500K shares minimum
    'max_spread_pct': 2.0,             # 2% max bid-ask spread
    'exclude_penny_stocks': True,
    
    # Dynamic criteria by market regime
    'regime_criteria': {
        MarketRegime.BULL_TRENDING: {
            'focus_on': 'gainers',
            'min_daily_change': -0.5,  # Allow small dips for better entries
            'min_volume_ratio': 1.1,   # Further lowered for more opportunities
            'preferred_sectors': ['TECHNOLOGY', 'GROWTH', 'CONSUMER_DISCRETIONARY', 'EQUITY'],
            'avoid_sectors': ['UTILITIES', 'DEFENSIVE'],
            'max_position_size_pct': 8.0  # Reduce max position size to 8%
        },
        
        MarketRegime.BEAR_TRENDING: {
            'focus_on': 'oversold_bounces',
            'max_daily_change': -3.0,
            'min_volume_ratio': 2.0,
            'preferred_sectors': ['DEFENSIVE', 'HEALTHCARE', 'UTILITIES'],
            'avoid_sectors': ['GROWTH', 'HIGH_BETA']
        },
        
        MarketRegime.VOLATILE_RANGE: {
            'focus_on': 'both_directions',
            'min_volatility_rank': 70,
            'min_volume_ratio': 2.0,
            'preferred_sectors': ['ALL'],
            'strategy_bias': 'mean_reversion'
        },
        
        MarketRegime.SECTOR_ROTATION: {
            'focus_on': 'sector_leaders',
            'min_relative_strength': 1.2,
            'sector_momentum_required': True,
            'cross_sector_analysis': True
        },
        
        MarketRegime.LOW_VOLATILITY: {
            'focus_on': 'breakouts',
            'min_consolidation_days': 3,        # Reduced for more opportunities
            'volume_expansion_required': True,
            'technical_breakout_required': True,
            'max_position_size_pct': 8.0,      # Consistent position sizing
            'min_volume_ratio': 1.3             # Lower threshold for more signals
        }
    }
}

# === RATE LIMIT MANAGEMENT ===
RATE_LIMIT_CONFIG = {
    'max_requests_per_minute': 200,
    'rate_limit_buffer': 0.85,         # Use 85% of limit
    
    # API budget allocation
    'budget_allocation': {
        'broad_scan': 25,               # 25 calls for market scanning
        'deep_dive': 50,               # 50 calls for detailed analysis
        'trade_execution': 35,          # 35 calls for order management
        'position_monitoring': 40,      # 40 calls for position tracking
        'emergency_reserve': 20         # 20 calls for emergencies
    },
    
    # Rate limiting strategy
    'priority_system': {
        'EMERGENCY': 1,                 # Emergency stops, liquidations
        'EXECUTION': 2,                 # Trade execution
        'MONITORING': 3,                # Position monitoring
        'DISCOVERY': 4,                 # Opportunity discovery
        'ANALYSIS': 5                   # Deep analysis
    }
}

# === DYNAMIC WATCHLIST MANAGEMENT ===
WATCHLIST_CONFIG = {
    'max_size': 25,
    'pruning_criteria': {
        'momentum_decay_threshold': 0.5,    # Remove if momentum drops
        'volume_decline_threshold': 0.7,     # Remove if volume fades
        'technical_breakdown': True,         # Remove on technical failure
        'max_age_hours': 2                   # Auto-remove after 2 hours for fresh discovery
    },
    
    'addition_criteria': {
        'min_opportunity_score': 0.6,       # Lower threshold for more variety
        'volume_surge_threshold': 3.0,      # 3x volume for immediate add
        'news_catalyst_weight': 0.3,        # News-driven opportunity boost
        'technical_confirmation': True       # Require technical setup
    }
}

# === STRATEGY CONFIGURATION ===
STRATEGY_CONFIG = {
    # Event-driven momentum strategy
    'momentum_strategy': {
        'fast_ma_period': 8,                # Reduced for faster signals
        'slow_ma_period': 16,               # Reduced for faster signals  
        'volume_confirmation': True,
        'rsi_filter': True,
        'rsi_overbought': 70,               # Less restrictive (was 75)
        'rsi_oversold': 30,                 # Less restrictive (was 25)
        'atr_stop_multiple': 1.8,           # Tighter stops (was 2.0)
        'min_atr': 0.015,                   # Lower threshold (was 0.02)
        'trailing_stop_enabled': True,      # Add trailing stop feature
        'trailing_stop_pct': 0.08           # 8% trailing stop
    },
    
    # Breakout strategy for low volatility regimes
    'breakout_strategy': {
        'consolidation_periods': [5, 10, 20],
        'volume_expansion_ratio': 2.0,
        'breakout_threshold': 0.02,         # 2% breakout
        'false_breakout_filter': True
    },
    
    # Mean reversion for volatile markets
    'mean_reversion_strategy': {
        'bollinger_period': 20,
        'bollinger_std': 2.0,
        'rsi_extreme_threshold': 20,        # RSI < 20 or > 80
        'volume_confirmation': True,
        'max_position_hold_days': 3
    }
}

# === EXTENDED HOURS TRADING CONFIGURATION ===
EXTENDED_HOURS_CONFIG = {
    'enable_trading': True,                 # Enable actual trading during extended hours
    'trading_hours': {
        'pre_market': {
            'start': '04:00',               # 4:00 AM ET
            'end': '09:30',                 # 9:30 AM ET
            'enabled': True,
            'strategy_adjustments': {
                'max_position_size_pct': 0.03,  # Smaller positions (3% vs 5%)
                'min_volume_ratio': 2.0,        # Higher volume requirements
                'max_spread_pct': 1.5,          # Tighter spread requirements
                'use_limit_orders_only': True,   # Limit orders only for safety
                'min_price_change_pct': 0.5     # Minimum move to consider
            }
        },
        'after_hours': {
            'start': '16:00',               # 4:00 PM ET
            'end': '20:00',                 # 8:00 PM ET
            'enabled': True,
            'strategy_adjustments': {
                'max_position_size_pct': 0.03,  # Smaller positions (3% vs 5%)
                'min_volume_ratio': 2.0,        # Higher volume requirements
                'max_spread_pct': 1.5,          # Tighter spread requirements
                'use_limit_orders_only': True,   # Limit orders only for safety
                'min_price_change_pct': 0.5     # Minimum move to consider
            }
        }
    },
    'risk_management': {
        'max_overnight_positions': 3,       # Limit overnight exposure
        'overnight_position_size_pct': 0.02, # Max 2% per overnight position
        'gap_risk_threshold': -0.05,        # Alert at -5% gap risk
        'emergency_sell_threshold': -0.08,   # Emergency sell at -8%
        'pre_market_earnings_filter': True,  # Filter out earnings during pre-market
        'news_impact_assessment': True       # Assess news impact before trading
    },
    'order_types': {
        'pre_market': ['limit', 'stop_limit'],    # Only limit orders pre-market
        'after_hours': ['limit', 'stop_limit'],   # Only limit orders after-hours
        'regular_hours': ['market', 'limit', 'stop', 'stop_limit']  # All order types during regular hours
    }
}

# === RISK MANAGEMENT ===
RISK_CONFIG = {
    # Position sizing
    'max_position_risk_pct': 2.0,          # 2% max risk per trade
    'max_portfolio_risk_pct': 12.0,        # 12% max total risk
    'max_correlation_exposure': 0.6,       # Max 60% in correlated positions
    'max_sector_concentration': 0.4,       # Max 40% in single sector
    
    # Drawdown controls
    'max_daily_drawdown_pct': 6.0,         # 6% daily emergency stop
    'max_weekly_drawdown_pct': 12.0,       # 12% weekly review
    'max_monthly_drawdown_pct': 20.0,      # 20% monthly strategy review
    
    # Trade parameters
    'stop_loss_pct': 8.0,                  # 8% stop loss
    'take_profit_multiple': 2.5,           # 2.5:1 reward/risk
    'min_risk_reward_ratio': 2.0,          # Never <2:1
    'max_position_hold_days': 15,          # Force exit after 15 days
    
    # PDT compliance
    'min_holding_period_hours': 24,        # Minimum hold time
    'pdt_day_trade_buffer': 1,             # Stay 1 trade under limit
    'account_size_threshold': 25000,       # PDT rule threshold
    
    # Enhanced Position Management - OPTIMIZED FOR PROFITABILITY
    'max_position_loss_pct': -4.0,         # Cut losses at -4% (keep conservative)
    'profit_taking_levels': [5.0, 10.0, 15.0],  # More granular: +5% (15%), +10% (35%), +15% (50%)
    'profit_taking_percentages': [0.15, 0.35, 0.50],  # How much to sell at each level
    'position_review_frequency_minutes': 15, # Review positions every 15min
    'trailing_stop_activation_pct': 3.0,   # Activate trailing stop at +3%
    'max_position_age_days': 4,            # Faster turnover - review after 4 days
    'concentration_limit_pct': 8.0,        # Keep safe concentration limit
    'extended_hours_emergency_loss_pct': -6.0  # Emergency extended hours threshold
}

# === AI CONFIGURATION ===
AI_CONFIG = {
    # Ollama settings
    'ollama_url': 'http://localhost:11434',
    'model_name': 'llama3:latest',
    'request_timeout': 30,
    'temperature': 0.1,
    'max_tokens': 2500,
    
    # Market analysis
    'market_regime_analysis_frequency': 30,  # Every 30 minutes
    'daily_report_time': time(8, 0),        # 8:00 AM daily report
    'confidence_threshold': 0.65,           # 65% AI confidence minimum
    
    # Prompt templates
    'few_shot_examples': True,              # Use few-shot prompting
    'structured_output_required': True,     # Enforce JSON output
    'context_window_management': True       # Manage prompt length
}

# === NEWS AND CATALYST DETECTION ===
NEWS_CONFIG = {
    'enable_news_analysis': True,
    'news_sources': ['ALPACA', 'BENZINGA'],
    'max_news_age_hours': 6,               # Only recent news
    'catalyst_keywords': [
        'earnings beat', 'guidance raise', 'acquisition', 'merger',
        'fda approval', 'contract win', 'partnership', 'upgrade',
        'buyback', 'dividend increase', 'expansion', 'launch'
    ],
    'negative_keywords': [
        'earnings miss', 'guidance cut', 'downgrade', 'lawsuit',
        'investigation', 'recall', 'bankruptcy', 'layoffs'
    ],
    'sentiment_analysis': True,
    'news_impact_scoring': True
}

# === PERFORMANCE MONITORING ===
PERFORMANCE_CONFIG = {
    'real_time_tracking': True,
    'benchmark_symbol': 'SPY',
    'performance_metrics': [
        'total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate',
        'profit_factor', 'calmar_ratio', 'sortino_ratio', 'alpha', 'beta'
    ],
    'target_metrics': {
        'monthly_return_target': 0.20,      # 20% monthly
        'annual_return_target': 3.0,        # 300% annual
        'max_acceptable_drawdown': 0.15,    # 15% max drawdown
        'min_sharpe_ratio': 1.5,            # 1.5 Sharpe minimum
        'min_win_rate': 0.55                # 55% win rate minimum
    }
}

# === LOGGING CONFIGURATION ===
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'log_file': 'intelligent_trading_system.log',
    'max_file_size_mb': 100,
    'backup_count': 14,
    'json_format': True,
    'structured_logging': True,
    
    # Log categories
    'log_categories': {
        'DISCOVERY': True,          # Opportunity discovery
        'SCREENING': True,          # Market screening
        'AI_ANALYSIS': True,        # AI decision making
        'EXECUTION': True,          # Trade execution
        'RISK': True,              # Risk management
        'PERFORMANCE': True,        # Performance tracking
        'SYSTEM': True             # System health
    }
}

# Configuration validation
def validate_configuration():
    """Comprehensive configuration validation"""
    errors = []
    
    # API credentials
    if not API_CONFIG['alpaca_key_id']:
        errors.append("APCA_API_KEY_ID environment variable not set")
    if not API_CONFIG['alpaca_secret_key']:
        errors.append("APCA_API_SECRET_KEY environment variable not set")
    
    # Rate limit validation
    total_budget = sum(RATE_LIMIT_CONFIG['budget_allocation'].values())
    max_budget = int(RATE_LIMIT_CONFIG['max_requests_per_minute'] * 
                    RATE_LIMIT_CONFIG['rate_limit_buffer'])
    if total_budget > max_budget:
        errors.append("API budget allocation ({}) exceeds limit ({})".format(total_budget, max_budget))
    
    # Risk parameter validation
    if RISK_CONFIG['max_position_risk_pct'] > 5.0:
        errors.append("Position risk too high (>5%)")
    if RISK_CONFIG['max_daily_drawdown_pct'] > 10.0:
        errors.append("Daily drawdown limit too high (>10%)")
    
    # Watchlist size validation
    if WATCHLIST_CONFIG['max_size'] > 50:
        errors.append("Watchlist size too large for efficient monitoring")
    
    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(errors))
    
    return True

if __name__ == "__main__":
    try:
        validate_configuration()
        print("✅ Configuration validated successfully")
        print("📊 API Budget: {}/minute".format(sum(RATE_LIMIT_CONFIG['budget_allocation'].values())))
        print("🎯 Max Watchlist: {} opportunities".format(WATCHLIST_CONFIG['max_size']))
        print("⚡ Scan Frequency: {} minutes".format(FUNNEL_CONFIG['broad_scan_frequency_minutes']))
    except ValueError as e:
        print("❌ Configuration Error: {}".format(e))