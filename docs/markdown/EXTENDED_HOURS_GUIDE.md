# Extended Hours Trading Guide

## Overview

Your trading system now supports **full extended hours trading** during pre-market (4:00 AM - 9:30 AM ET) and after-hours (4:00 PM - 8:00 PM ET) sessions. This guide explains how to enable, configure, and use this functionality.

## What's New

### ✅ Extended Hours Trading Features

- **Pre-market trading**: 4:00 AM - 9:30 AM ET
- **After-hours trading**: 4:00 PM - 8:00 PM ET
- **Conservative position sizing**: 3% max per position (vs 5% during regular hours)
- **Limit orders only**: Enhanced safety during low-liquidity periods
- **Enhanced risk management**: Tighter stops and position limits
- **Automatic cleanup**: Positions closed before market close to avoid overnight risk

### 🔒 Safety Features

- **Smaller position sizes**: Reduced from 5% to 3% of account
- **Limit orders only**: No market orders during extended hours
- **Tighter spreads**: Maximum 1.5% bid-ask spread requirement
- **Volume requirements**: Higher volume thresholds for extended hours
- **Overnight position limits**: Maximum 3 positions held overnight

## Configuration

### 1. Enable Extended Hours Trading

The system is already configured with extended hours trading enabled. Check your `config.py`:

```python
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
    }
}
```

### 2. Risk Management Settings

```python
'risk_management': {
    'max_overnight_positions': 3,       # Limit overnight exposure
    'overnight_position_size_pct': 0.02, # Max 2% per overnight position
    'gap_risk_threshold': -0.05,        # Alert at -5% gap risk
    'emergency_sell_threshold': -0.08,   # Emergency sell at -8%
    'pre_market_earnings_filter': True,  # Filter out earnings during pre-market
    'news_impact_assessment': True       # Assess news impact before trading
}
```

## How It Works

### 1. Market Hours Detection

The system automatically detects current market hours:

- **4:00 AM - 9:30 AM ET**: Pre-market session
- **9:30 AM - 4:00 PM ET**: Regular market hours
- **4:00 PM - 8:00 PM ET**: After-hours session
- **8:00 PM - 4:00 AM ET**: Overnight (no trading)

### 2. Extended Hours Trading Logic

During extended hours, the system:

1. **Scans for opportunities** with enhanced criteria
2. **Applies conservative filters** (smaller positions, limit orders only)
3. **Monitors positions** with tighter risk controls
4. **Automatically cleans up** before market close

### 3. Position Management

- **Entry**: Limit orders with 0.5% buffer above current price
- **Stop Loss**: 5% below entry price
- **Take Profit**: 10% above entry price
- **Monitoring**: Continuous P&L tracking with automatic exit triggers

## Usage Examples

### Running the System

```bash
# Start the trading system (will automatically handle extended hours)
python main.py

# Or use the start script
./start_trading.sh
```

### Testing Extended Hours Functionality

```bash
# Run the extended hours test suite
python test_extended_hours.py
```

### Manual Extended Hours Trading

```python
from extended_hours_trader import ExtendedHoursTrader

# Create trader instance
trader = ExtendedHoursTrader(gateway, risk_manager, market_status)

# Check if extended hours trading is active
if await trader.should_trade_extended_hours():
    # Get opportunities
    opportunities = await trader.get_extended_hours_opportunities()

    # Execute trades
    for opportunity in opportunities[:3]:
        success = await trader.execute_extended_hours_trade(opportunity)
```

## Trading Strategies

### Pre-Market Strategy (4:00 AM - 9:30 AM ET)

**Focus**: News catalysts, earnings releases, overnight developments

**Criteria**:

- Minimum 0.5% price movement
- Volume surge (2x normal)
- Tight spreads (< 1.5%)
- News sentiment analysis

**Risk Management**:

- 3% max position size
- Limit orders only
- 5% stop loss
- 10% take profit

### After-Hours Strategy (4:00 PM - 8:00 PM ET)

**Focus**: Earnings releases, news events, market reactions

**Criteria**:

- Significant price movement
- High volume activity
- Earnings calendar check
- Technical confirmation

**Risk Management**:

- 3% max position size
- Limit orders only
- Tighter stops (5%)
- Quick profit taking (10%)

## Risk Considerations

### ⚠️ Extended Hours Risks

1. **Low Liquidity**: Wider spreads, fewer participants
2. **Gap Risk**: Overnight price gaps can be significant
3. **News Impact**: Earnings and news can cause large moves
4. **Limited Exit Options**: Fewer buyers/sellers available

### 🛡️ Risk Mitigation

1. **Smaller Positions**: 3% vs 5% during regular hours
2. **Limit Orders Only**: No market order slippage
3. **Tighter Stops**: 5% vs 8% during regular hours
4. **Position Limits**: Max 3 overnight positions
5. **Automatic Cleanup**: Close positions before market close

## Monitoring and Alerts

### Position Monitoring

The system continuously monitors extended hours positions:

```python
# Monitor positions every 5 minutes
await trader.monitor_extended_hours_positions()

# Automatic stop loss at -5%
# Automatic take profit at +10%
# Emergency exit at -8%
```

### Alert System

- **Gap Risk Alerts**: When positions move >5% against you
- **Emergency Alerts**: When positions hit -8% loss threshold
- **Cleanup Alerts**: When positions are closed before market close

## Best Practices

### 1. Start Small

- Begin with 1-2 extended hours positions
- Monitor performance before scaling up
- Focus on high-volume, liquid stocks

### 2. News Awareness

- Check earnings calendar before pre-market trading
- Monitor news feeds for catalysts
- Avoid trading during major news events

### 3. Position Sizing

- Never exceed 3% per position during extended hours
- Consider reducing position sizes further in volatile conditions
- Maintain adequate cash reserves

### 4. Exit Strategy

- Set clear profit targets (10%)
- Use tight stop losses (5%)
- Don't hold extended hours positions overnight unless necessary

## Troubleshooting

### Common Issues

1. **No Extended Hours Trading**

   - Check `EXTENDED_HOURS_CONFIG['enable_trading']` is `True`
   - Verify current time is within extended hours
   - Check Alpaca account permissions

2. **Orders Not Filling**

   - Extended hours have lower liquidity
   - Use limit orders with reasonable prices
   - Consider widening limit price buffers

3. **High Slippage**
   - Extended hours spreads are wider
   - Use limit orders instead of market orders
   - Trade only high-volume stocks

### Debug Mode

Enable debug logging to see extended hours activity:

```python
import logging
logging.getLogger('extended_hours_trader').setLevel(logging.DEBUG)
```

## Performance Tracking

### Extended Hours Metrics

The system tracks extended hours performance separately:

- **Pre-market P&L**: Performance during 4:00 AM - 9:30 AM
- **After-hours P&L**: Performance during 4:00 PM - 8:00 PM
- **Overnight Risk**: Gap risk exposure
- **Fill Quality**: Order execution quality during extended hours

### Performance Analysis

Monitor these key metrics:

1. **Win Rate**: Percentage of profitable extended hours trades
2. **Average P&L**: Average profit/loss per trade
3. **Fill Rate**: Percentage of orders that get filled
4. **Slippage**: Average price slippage during execution

## Advanced Configuration

### Customizing Extended Hours Strategy

You can modify the extended hours strategy in `config.py`:

```python
# Customize pre-market strategy
'pre_market': {
    'enabled': True,
    'strategy_adjustments': {
        'max_position_size_pct': 0.025,  # Even smaller positions (2.5%)
        'min_volume_ratio': 3.0,         # Higher volume requirements
        'max_spread_pct': 1.0,           # Tighter spreads
        'use_limit_orders_only': True,
        'min_price_change_pct': 1.0      # Higher movement threshold
    }
}
```

### Adding Custom Filters

Extend the opportunity filtering in `extended_hours_trader.py`:

```python
async def _passes_extended_hours_risk_check(self, opportunity: Dict, adjustments: Dict) -> bool:
    # Add your custom risk checks here
    symbol = opportunity.get('symbol')

    # Example: Avoid stocks with earnings today
    if self._has_earnings_today(symbol):
        return False

    # Example: Check news sentiment
    if self._negative_news_sentiment(symbol):
        return False

    return True
```

## Conclusion

Extended hours trading provides additional opportunities but comes with increased risks. The system is designed with conservative defaults to protect your capital while capturing profitable moves during these sessions.

**Key Takeaways**:

- ✅ Extended hours trading is now fully enabled
- 🔒 Conservative risk management is built-in
- 📊 Automatic opportunity scanning and execution
- 🛡️ Enhanced safety features for low-liquidity periods
- 🧹 Automatic position cleanup before market close

Start with small positions and gradually increase as you become comfortable with the extended hours environment. Always monitor your positions and be prepared for wider price swings and lower liquidity.
