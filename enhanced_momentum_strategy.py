"""
Enhanced event-driven momentum strategy with AI integration
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import pandas as pd
from config import *

logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    """Complete trading signal with all execution parameters"""
    symbol: str
    action: str  # 'BUY' or 'SELL'
    signal_type: str  # 'MOMENTUM', 'BREAKOUT', 'MEAN_REVERSION'
    entry_price: float
    stop_loss_price: float
    take_profit_price: float
    position_size_pct: float
    confidence: float
    reasoning: str
    timestamp: datetime
    
    # Risk parameters
    risk_reward_ratio: float = 0.0
    max_hold_days: int = 15
    
    # Market context
    market_regime: str = "UNKNOWN"
    volatility_environment: str = "NORMAL"

class EventDrivenMomentumStrategy:
    """
    Advanced momentum strategy that adapts to market conditions
    Integrates technical analysis with AI insights and dynamic strategy selection
    """
    
    def __init__(self):
        self.strategy_config = STRATEGY_CONFIG['momentum_strategy']
        self.signals_generated = 0
        self.current_market_regime = "UNKNOWN"
        self.current_volatility_env = "NORMAL"
        self.active_strategy_mode = "MOMENTUM"  # Default strategy
        
    def update_market_context(self, market_regime: str = None, volatility_env: str = None):
        """
        Update market context and dynamically select strategy based on regime
        """
        try:
            if market_regime:
                self.current_market_regime = market_regime
            if volatility_env:
                self.current_volatility_env = volatility_env
            
            # Dynamic strategy selection based on market regime
            previous_strategy = self.active_strategy_mode
            self.active_strategy_mode = self._select_optimal_strategy(market_regime, volatility_env)
            
            if self.active_strategy_mode != previous_strategy:
                logger.info(f"🔄 STRATEGY CHANGE: {previous_strategy} → {self.active_strategy_mode}")
                logger.info(f"   Market Regime: {self.current_market_regime}")
                logger.info(f"   Volatility: {self.current_volatility_env}")
            
        except Exception as e:
            logger.error(f"Market context update failed: {e}")
    
    def _select_optimal_strategy(self, market_regime: str = None, volatility_env: str = None) -> str:
        """
        Select optimal strategy based on current market conditions
        """
        regime = market_regime or self.current_market_regime
        volatility = volatility_env or self.current_volatility_env
        
        # Strategy selection logic based on market regime
        if regime == "BULL_TRENDING":
            if volatility in ["LOW", "NORMAL"]:
                return "MOMENTUM"  # Strong momentum in trending bull market
            else:  # HIGH or EXTREME volatility
                return "BREAKOUT"  # Wait for clear breakouts in high volatility
        
        elif regime == "BEAR_TRENDING":
            if volatility in ["LOW", "NORMAL"]:
                return "MEAN_REVERSION"  # Counter-trend plays in bear market
            else:  # HIGH or EXTREME volatility
                return "DEFENSIVE"  # Avoid trading in volatile bear markets
        
        elif regime == "VOLATILE_RANGE":
            if volatility == "HIGH":
                return "MEAN_REVERSION"  # Range-bound mean reversion
            else:
                return "BREAKOUT"  # Wait for breakouts from range
        
        elif regime == "LOW_VOLATILITY":
            return "BREAKOUT"  # Look for breakouts in low vol environment
        
        elif regime == "SECTOR_ROTATION":
            return "MOMENTUM"  # Follow sector momentum
        
        else:  # UNKNOWN or other regimes
            return "MOMENTUM"  # Default to momentum strategy
    
    async def analyze_symbol(self, symbol: str, bars: List[Dict], 
                           quote_data: Dict = None, data_sources: List[str] = None,
                           market_intelligence = None) -> Optional[TradingSignal]:
        """
        Comprehensive symbol analysis with dynamic strategy selection
        """
        try:
            # Update market context if provided
            if market_intelligence:
                self.update_market_context(
                    market_intelligence.market_regime,
                    market_intelligence.volatility_environment
                )
            
            # Log data sources for transparency
            if data_sources:
                logger.info(f"📊 {symbol} data sources: {', '.join(data_sources)}")
            
            if not bars:
                logger.info(f"📊 No data for {symbol}")
                return None
            
            # CRITICAL: Check for stale data before any analysis
            if not self._validate_data_freshness(symbol, bars, quote_data):
                logger.warning(f"🚫 REJECTING {symbol}: Stale data detected - unsafe for trading")
                return None
            elif len(bars) < 5:  # Further reduced due to Alpaca free tier limitations
                # CRITICAL: Insufficient data for analysis - reject trade
                logger.warning(f"📊 INSUFFICIENT DATA for {symbol}: got {len(bars)} bars, need minimum 5 - REJECTING TRADE")
                return None
            elif len(bars) < 15:  # Reduced from 20
                # Use enhanced simplified analysis for limited data
                logger.info(f"📊 LIMITED DATA for {symbol}: got {len(bars)} bars, using enhanced simplified analysis")
                return self._generate_enhanced_simple_signal(symbol, bars, quote_data)
                
            # Convert to DataFrame for analysis
            df = self._bars_to_dataframe(bars)
            
            # Calculate technical indicators
            indicators = self._calculate_indicators(df)
            
            # Dynamic strategy application based on current market regime
            signal = None
            
            if self.active_strategy_mode == "MOMENTUM":
                signal = self._check_momentum_setup(symbol, df, indicators)
            elif self.active_strategy_mode == "MEAN_REVERSION":
                signal = self._check_mean_reversion_setup(symbol, df, indicators)
            elif self.active_strategy_mode == "BREAKOUT":
                signal = self._check_breakout_setup(symbol, df, indicators)
            elif self.active_strategy_mode == "DEFENSIVE":
                # In defensive mode, only trade very high-confidence setups
                signal = self._check_defensive_setup(symbol, df, indicators)
            else:
                # Fallback to momentum
                signal = self._check_momentum_setup(symbol, df, indicators)
            
            if signal:
                # Update signal with market context
                signal.market_regime = self.current_market_regime
                signal.volatility_environment = self.current_volatility_env
                signal.signal_type = f"{self.active_strategy_mode}_{signal.signal_type}"
                
                logger.info(f"📈 {self.active_strategy_mode} signal generated for {symbol}")
                logger.info(f"   Market context: {self.current_market_regime} regime, {self.current_volatility_env} volatility")
                self.signals_generated += 1
                return signal
            else:
                logger.info(f"📊 No {self.active_strategy_mode.lower()} setup detected for {symbol}")
                
            return None
            
        except Exception as e:
            logger.error(f"Signal analysis failed for {symbol}: {e}")
            return None
    
    def _generate_enhanced_simple_signal(self, symbol: str, bars: List[Dict], 
                                        quote_data: Dict = None) -> Optional[TradingSignal]:
        """Generate enhanced signal with limited historical data + real-time quotes"""
        try:
            if not bars or len(bars) < 5:  # Reduced for free tier limitations
                logger.warning(f"📊 {symbol}: Insufficient data for enhanced analysis ({len(bars)} bars)")
                return None
                
            # Enhanced data analysis with 8-15 bars
            prices = [float(bar.get('c', 0)) for bar in bars if float(bar.get('c', 0)) > 0]
            volumes = [int(bar.get('v', 0)) for bar in bars if int(bar.get('v', 0)) > 0]
            highs = [float(bar.get('h', 0)) for bar in bars if float(bar.get('h', 0)) > 0]
            lows = [float(bar.get('l', 0)) for bar in bars if float(bar.get('l', 0)) > 0]
            
            if len(prices) < 5:  # Reduced requirement
                logger.warning(f"📊 {symbol}: Not enough valid price data")
                return None
                
            current_price = prices[-1]
            
            # Use real-time quote if available for more accurate current price
            if quote_data and quote_data.get('current_price', 0) > 0:
                current_price = quote_data['current_price']
                logger.info(f"📊 {symbol}: Using real-time price ${current_price:.2f}")
            
            # Enhanced technical analysis with limited data
            
            # 1. Multi-period momentum analysis (adapted for limited data)
            momentum_1 = ((current_price - prices[-2]) / prices[-2]) * 100 if len(prices) >= 2 else 0
            momentum_3 = ((current_price - prices[-4]) / prices[-4]) * 100 if len(prices) >= 4 else 0
            momentum_5 = ((current_price - prices[-5]) / prices[-5]) * 100 if len(prices) >= 5 else 0
            momentum_all = ((current_price - prices[0]) / prices[0]) * 100 if len(prices) >= 2 else 0
            
            # 2. Volume trend analysis
            recent_vol = volumes[-1] if volumes else 0
            avg_vol = sum(volumes) / len(volumes) if volumes else 1
            vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
            
            # 3. Price range analysis (volatility) - adapted for limited data
            if len(highs) >= 5 and len(lows) >= 5:
                recent_high = max(highs)
                recent_low = min(lows)
                price_range_pct = ((recent_high - recent_low) / recent_low) * 100 if recent_low > 0 else 0
            else:
                price_range_pct = 10  # Default moderate volatility
                
            # 4. Simple moving averages - adapted for limited data
            n_short = min(3, len(prices))
            n_long = min(5, len(prices))
            ma_short = sum(prices[-n_short:]) / n_short if n_short > 0 else current_price
            ma_long = sum(prices[-n_long:]) / n_long if n_long > 0 else current_price
            ma_trend = "UP" if ma_short > ma_long else "DOWN"
            
            # 5. Support/Resistance levels - use all available data
            support_level = min(lows) if lows else current_price * 0.95
            resistance_level = max(highs) if highs else current_price * 1.05
            
            # ADAPTIVE SIGNAL CRITERIA (based on market regime and trade analysis)
            # Avoid buying near daily highs - check position within daily range
            daily_high = max(highs) if highs else current_price * 1.05
            daily_low = min(lows) if lows else current_price * 0.95
            daily_range_position = (current_price - daily_low) / (daily_high - daily_low) if daily_high > daily_low else 0.5
            
            # ADAPTIVE CRITERIA based on market conditions (single strategy, multiple modes)
            base_criteria = [
                vol_ratio > 1.3,                # Above average volume
                price_range_pct < 25,           # Not too volatile
                current_price > 5.0,            # Avoid penny stocks
                recent_vol > 50000,             # Minimum liquidity
                current_price > support_level * 1.01,  # Above support
                daily_range_position < 0.85,    # Avoid buying too close to daily high
            ]
            
            # MOMENTUM MODE (for trending markets)
            momentum_criteria = [
                momentum_1 > 0.8,               # Recent momentum
                momentum_all > 2.0,             # Strong overall trend
                ma_trend == "UP",               # Moving average uptrend
            ]
            
            # MEAN REVERSION MODE (for volatile/oversold conditions)
            mean_reversion_criteria = [
                momentum_1 < -1.0,              # Recent pullback
                momentum_all > -5.0,            # Not in free fall
                current_price < ma_short * 0.98, # Below short MA (oversold)
            ]
            
            # Choose mode based on market conditions
            if price_range_pct > 15 and momentum_all < 1.0:
                # High volatility, low momentum = Mean reversion opportunity
                signal_criteria = base_criteria + mean_reversion_criteria
                signal_mode = "MEAN_REVERSION"
            else:
                # Default to momentum mode
                signal_criteria = base_criteria + momentum_criteria  
                signal_mode = "MOMENTUM"
            
            # Add real-time criteria if quote data available
            if quote_data:
                bid_ask_spread = quote_data.get('bid_ask_spread', 0)
                if bid_ask_spread < current_price * 0.01:  # Spread < 1%
                    signal_criteria.append(True)  # Good liquidity
                else:
                    signal_criteria.append(False)  # Wide spread
            
            criteria_met = sum(signal_criteria)
            total_criteria = len(signal_criteria)
            
            # Require 65% of criteria to be met (lowered due to data limitations)
            if criteria_met >= (total_criteria * 0.65):
                
                # Calculate confidence based on data quality and criteria
                base_confidence = criteria_met / total_criteria
                
                # Bonus for real-time data
                if quote_data:
                    base_confidence += 0.05
                    
                # Bonus for strong momentum
                if momentum_1 > 2.0:
                    base_confidence += 0.05
                    
                confidence = min(0.85, base_confidence)
                
                # Dynamic position sizing based on signal strength
                if criteria_met >= total_criteria * 0.9:  # 90%+ criteria
                    position_size = 0.02  # 2%
                elif criteria_met >= total_criteria * 0.8:  # 80%+ criteria  
                    position_size = 0.015  # 1.5%
                else:
                    position_size = 0.01  # 1%
                
                logger.info(f"📈 {signal_mode} BUY signal for {symbol}: {criteria_met}/{total_criteria} criteria met")
                logger.info(f"   - Recent momentum: {momentum_1:+.2f}%")
                logger.info(f"   - Overall momentum: {momentum_all:+.2f}%") 
                logger.info(f"   - Volume ratio: {vol_ratio:.1f}x")
                logger.info(f"   - MA trend: {ma_trend}")
                logger.info(f"   - Daily range position: {daily_range_position:.2f}")
                logger.info(f"   - Mode: {signal_mode}")
                logger.info(f"   - Confidence: {confidence:.2f}")
                
                # Estimate ATR for position sizing (simple volatility measure)
                price_volatility = (max(highs) - min(lows)) / len(highs) if highs and lows else current_price * 0.02
                estimated_atr = price_volatility * 0.8  # Conservative ATR estimate
                
                # Apply regime-specific adjustments to signal parameters
                adjusted_stop, adjusted_target, adjusted_size = self._apply_regime_adjustments(
                    current_price, max(support_level, current_price * 0.95),
                    min(resistance_level, current_price * 1.08), position_size
                )
                
                return TradingSignal(
                    symbol=symbol,
                    action='BUY',
                    signal_type=f'ENHANCED_{signal_mode}',
                    entry_price=current_price,
                    stop_loss_price=adjusted_stop,
                    take_profit_price=adjusted_target,
                    position_size_pct=adjusted_size,
                    confidence=confidence,
                    reasoning=f"{signal_mode} ({self.active_strategy_mode}): {momentum_1:+.1f}% recent, {momentum_all:+.1f}% overall, {vol_ratio:.1f}x volume",
                    timestamp=datetime.now(),
                    risk_reward_ratio=1.6,
                    max_hold_days=self._get_regime_hold_days(),
                    market_regime=self.current_market_regime,
                    volatility_environment=self.current_volatility_env,
                    atr=estimated_atr  # Add ATR for position sizing
                )
            else:
                logger.info(f"📊 {symbol}: Enhanced criteria not met ({criteria_met}/{total_criteria})")
                return None
                
        except Exception as e:
            logger.error(f"Enhanced signal generation failed for {symbol}: {e}")
            return None
    
    def _generate_simple_signal(self, symbol: str, bars: List[Dict]) -> Optional[TradingSignal]:
        """Generate simple signal with limited data (for weekends/holidays)"""
        try:
            if not bars or len(bars) < 5:
                logger.warning(f"📊 {symbol}: Insufficient data for ANY analysis ({len(bars)} bars)")
                return None
                
            # Get the latest bar
            latest_bar = bars[-1]
            current_price = float(latest_bar.get('c', 0))
            volume = int(latest_bar.get('v', 0))
            
            if current_price <= 0 or volume <= 0:
                logger.warning(f"📊 {symbol}: Invalid price/volume data")
                return None
                
            # Calculate basic statistics from available data
            prices = [float(bar.get('c', 0)) for bar in bars if float(bar.get('c', 0)) > 0]
            volumes = [int(bar.get('v', 0)) for bar in bars if int(bar.get('v', 0)) > 0]
            
            if len(prices) < 5 or len(volumes) < 5:
                logger.warning(f"📊 {symbol}: Not enough valid price/volume data")
                return None
                
            # Basic trend analysis
            recent_trend = sum(1 for i in range(1, min(5, len(prices))) if prices[-i] < prices[-i-1])
            avg_volume = sum(volumes[:-1]) / len(volumes[:-1]) if len(volumes) > 1 else volume
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
            
            # VERY STRINGENT requirements for limited data scenarios
            prev_bar = bars[-2]
            prev_price = float(prev_bar.get('c', current_price))
            price_change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
            
            # Calculate price volatility from available data
            price_std = 0
            if len(prices) >= 5:
                price_avg = sum(prices) / len(prices)
                price_variance = sum((p - price_avg) ** 2 for p in prices) / len(prices)
                price_std = price_variance ** 0.5
                volatility_pct = (price_std / price_avg) * 100 if price_avg > 0 else 100
            else:
                volatility_pct = 100  # Assume high volatility with insufficient data
            
            # STRICT criteria for limited data trading
            signal_criteria = [
                price_change_pct > 2.0,  # Strong momentum (raised from 1%)
                volume_ratio > 2.0,      # Strong volume (raised from 1.5x)
                recent_trend >= 2,       # Upward trend in recent bars
                volatility_pct < 15.0,   # Not too volatile
                volume > 500000,         # Minimum liquidity
                current_price > 5.0,     # Avoid penny stocks
                len(bars) >= 5           # Minimum data requirement
            ]
            
            criteria_met = sum(signal_criteria)
            
            # Require ALL criteria to be met for limited data scenario
            if criteria_met >= 6:  # At least 6 of 7 criteria
                logger.info(f"📈 CAUTIOUS BUY signal for {symbol}: {criteria_met}/7 criteria met")
                logger.info(f"   - Price momentum: +{price_change_pct:.2f}%")
                logger.info(f"   - Volume ratio: {volume_ratio:.1f}x")
                logger.info(f"   - Trend strength: {recent_trend}/4")
                logger.info(f"   - Volatility: {volatility_pct:.1f}%")
                
                return TradingSignal(
                    symbol=symbol,
                    action='BUY',
                    signal_type='MOMENTUM',
                    entry_price=current_price,
                    stop_loss_price=current_price * 0.95,  # 5% stop loss
                    take_profit_price=current_price * 1.08,  # 8% take profit (reduced)
                    position_size_pct=0.01,  # 1% position size (reduced for safety)
                    confidence=0.65,  # Moderate confidence
                    reasoning=f"Limited data signal: +{price_change_pct:.2f}% momentum, {volume_ratio:.1f}x volume, {criteria_met}/7 criteria",
                    timestamp=datetime.now(),
                    risk_reward_ratio=1.6,
                    max_hold_days=3  # Shorter hold time
                )
            else:
                logger.info(f"📊 {symbol}: Limited data criteria not met ({criteria_met}/7)")
                return None
                
            return None
            
        except Exception as e:
            logger.error(f"Simple signal generation failed for {symbol}: {e}")
            return None
            
    def _bars_to_dataframe(self, bars: List[Dict]) -> pd.DataFrame:
        """Convert bar data to pandas DataFrame"""
        df_data = []
        
        for bar in bars:
            df_data.append({
                'timestamp': bar.get('t'),
                'open': float(bar.get('o', 0)),
                'high': float(bar.get('h', 0)),
                'low': float(bar.get('l', 0)),
                'close': float(bar.get('c', 0)),
                'volume': int(bar.get('v', 0))
            })
            
        df = pd.DataFrame(df_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
        
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive technical indicators"""
        try:
            indicators = {}
            
            # Moving averages
            indicators['ma_10'] = df['close'].rolling(window=10).mean()
            indicators['ma_20'] = df['close'].rolling(window=20).mean()
            indicators['ma_50'] = df['close'].rolling(window=50).mean()
            
            # RSI
            indicators['rsi'] = self._calculate_rsi(df['close'], 14)
            
            # ATR
            indicators['atr'] = self._calculate_atr(df, 14)
            
            # Volume analysis
            indicators['volume_ma'] = df['volume'].rolling(window=20).mean()
            indicators['volume_ratio'] = df['volume'] / indicators['volume_ma']
            
            # Bollinger Bands
            bb_period = 20
            bb_std = 2.0
            bb_ma = df['close'].rolling(window=bb_period).mean()
            bb_std_dev = df['close'].rolling(window=bb_period).std()
            indicators['bb_upper'] = bb_ma + (bb_std_dev * bb_std)
            indicators['bb_lower'] = bb_ma - (bb_std_dev * bb_std)
            indicators['bb_middle'] = bb_ma
            
            # MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            indicators['macd'] = ema_12 - ema_26
            indicators['macd_signal'] = indicators['macd'].ewm(span=9).mean()
            indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
            
            return indicators
            
        except Exception as e:
            logger.error(f"Indicator calculation failed: {e}")
            return {}
            
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
        
    def _check_momentum_setup(self, symbol: str, df: pd.DataFrame, indicators: Dict) -> Optional[TradingSignal]:
        """Check for momentum trading setup"""
        try:
            latest_idx = len(df) - 1
            current_price = df.iloc[latest_idx]['close']
            
            # Get latest indicator values
            latest_rsi = indicators['rsi'].iloc[latest_idx]
            latest_ma_10 = indicators['ma_10'].iloc[latest_idx]
            latest_ma_20 = indicators['ma_20'].iloc[latest_idx]
            latest_volume_ratio = indicators['volume_ratio'].iloc[latest_idx]
            latest_atr = indicators['atr'].iloc[latest_idx]
            latest_macd = indicators['macd'].iloc[latest_idx]
            latest_macd_signal = indicators['macd_signal'].iloc[latest_idx]
            
            # Skip if indicators are NaN
            if pd.isna([latest_rsi, latest_ma_10, latest_ma_20, latest_volume_ratio]).any():
                return None
                
            # === MOMENTUM BUY SETUP ===
            momentum_conditions = [
                latest_ma_10 > latest_ma_20,  # Short MA above long MA
                latest_rsi > 30 and latest_rsi < 75,  # RSI in momentum range
                latest_volume_ratio > 1.5,  # Above average volume
                latest_macd > latest_macd_signal,  # MACD bullish
                current_price > latest_ma_10  # Price above short MA
            ]
            
            if sum(momentum_conditions) >= 4:  # At least 4 of 5 conditions
                
                # Calculate position size and risk parameters
                atr_pct = (latest_atr / current_price) * 100
                
                if atr_pct < self.strategy_config['min_atr']:
                    logger.debug(f"{symbol} ATR too low: {atr_pct:.2f}%")
                    return None
                    
                # Stop loss using ATR
                stop_loss_price = current_price - (latest_atr * self.strategy_config['atr_stop_multiple'])
                
                # Take profit target
                risk_amount = current_price - stop_loss_price
                take_profit_price = current_price + (risk_amount * RISK_CONFIG['take_profit_multiple'])
                
                # Risk/reward validation
                risk_reward_ratio = (take_profit_price - current_price) / (current_price - stop_loss_price)
                
                if risk_reward_ratio < RISK_CONFIG['min_risk_reward_ratio']:
                    logger.debug(f"{symbol} R/R too low: {risk_reward_ratio:.2f}")
                    return None
                    
                # Calculate confidence based on conditions met
                confidence = sum(momentum_conditions) / len(momentum_conditions)
                
                # Boost confidence for strong setups
                if latest_volume_ratio > 3.0:
                    confidence += 0.1
                if latest_rsi > 50 and latest_rsi < 65:  # Sweet spot RSI
                    confidence += 0.1
                    
                confidence = min(0.95, confidence)
                
                # Generate signal
                signal = TradingSignal(
                    symbol=symbol,
                    action='BUY',
                    signal_type='MOMENTUM',
                    entry_price=current_price,
                    stop_loss_price=stop_loss_price,
                    take_profit_price=take_profit_price,
                    position_size_pct=RISK_CONFIG['max_position_risk_pct'],
                    confidence=confidence,
                    reasoning=f"Momentum setup: MA bullish, RSI={latest_rsi:.1f}, Vol={latest_volume_ratio:.1f}x",
                    timestamp=datetime.now(),
                    risk_reward_ratio=risk_reward_ratio,
                    max_hold_days=RISK_CONFIG['max_position_hold_days']
                )
                
                return signal
                
            # === MEAN REVERSION SETUP (for volatile markets) ===
            if latest_rsi < 30 and latest_volume_ratio > 2.0:
                
                # Oversold bounce setup
                stop_loss_price = current_price - (latest_atr * 1.5)  # Tighter stop
                take_profit_price = current_price + (latest_atr * 2.0)  # Quick profit target
                
                risk_reward_ratio = (take_profit_price - current_price) / (current_price - stop_loss_price)
                
                if risk_reward_ratio >= 1.5:  # Lower R/R for mean reversion
                    
                    signal = TradingSignal(
                        symbol=symbol,
                        action='BUY',
                        signal_type='MEAN_REVERSION',
                        entry_price=current_price,
                        stop_loss_price=stop_loss_price,
                        take_profit_price=take_profit_price,
                        position_size_pct=RISK_CONFIG['max_position_risk_pct'] * 0.5,  # Smaller size
                        confidence=0.7,
                        reasoning=f"Oversold bounce: RSI={latest_rsi:.1f}, Vol={latest_volume_ratio:.1f}x",
                        timestamp=datetime.now(),
                        risk_reward_ratio=risk_reward_ratio,
                        max_hold_days=3  # Shorter hold time
                    )
                    
                    return signal
                    
            return None
            
        except Exception as e:
            logger.error(f"Momentum setup check failed for {symbol}: {e}")
            return None
    
    def _validate_data_freshness(self, symbol: str, bars: List[Dict], quote_data: Dict = None) -> bool:
        """
        CRITICAL: Validate data freshness to prevent trading on stale data
        Gemini's top priority edge case protection - Enhanced for different data types
        """
        try:
            # Use UTC for consistent timestamp comparison
            now = datetime.utcnow()
            
            # If we have real-time quote data, use it for freshness validation
            if quote_data and quote_data.get('timestamp'):
                try:
                    quote_timestamp = datetime.fromtimestamp(float(quote_data['timestamp']))
                    quote_age_seconds = (now - quote_timestamp).total_seconds()
                    
                    # Real-time quotes should be very fresh
                    if quote_age_seconds > 300:  # 5 minutes
                        logger.warning(f"🚫 {symbol}: Stale quote data - {quote_age_seconds:.0f}s old")
                        return False
                    else:
                        logger.debug(f"✅ {symbol}: Fresh quote data - {quote_age_seconds:.0f}s old")
                        return True  # Quote data is fresh, bars can be older
                except Exception as e:
                    logger.debug(f"Quote timestamp parsing failed for {symbol}: {e}")
            
            # For daily bars, be more lenient - check if it's today's data
            max_data_age_seconds = 86400  # 24 hours for daily data
            
            # Check latest bar timestamp
            if bars:
                latest_bar = bars[-1]
                bar_timestamp_str = latest_bar.get('t', '')
                
                if bar_timestamp_str:
                    try:
                        # Parse timestamp (format may vary by data source)
                        if isinstance(bar_timestamp_str, str):
                            # Try common timestamp formats  
                            for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                                try:
                                    bar_timestamp = datetime.strptime(bar_timestamp_str, fmt)
                                    # Convert to UTC if timezone info missing (assume market data is UTC/EST)
                                    if fmt.endswith('Z'):
                                        # Already UTC
                                        pass
                                    else:
                                        # Assume Eastern Time (market hours) - convert to UTC
                                        # This is a simplification - in production you'd use proper timezone handling
                                        pass
                                    break
                                except ValueError:
                                    continue
                            else:
                                # If all formats fail, try parsing as Unix timestamp
                                try:
                                    bar_timestamp = datetime.fromtimestamp(float(bar_timestamp_str))
                                except (ValueError, TypeError):
                                    logger.warning(f"⚠️ {symbol}: Could not parse bar timestamp: {bar_timestamp_str}")
                                    return True  # Assume fresh to avoid blocking valid trades
                        else:
                            # Assume it's already a datetime or timestamp
                            bar_timestamp = datetime.fromtimestamp(float(bar_timestamp_str))
                        
                        # Check if data is too old
                        data_age_seconds = (now - bar_timestamp).total_seconds()
                        
                        # Smart freshness validation based on data type
                        if data_age_seconds > max_data_age_seconds:
                            # For daily bars during market hours, check if it's today's data
                            if max_data_age_seconds > 3600:  # Daily data mode
                                # Check if bar is from today (more lenient for daily data)
                                today = now.date()
                                bar_date = bar_timestamp.date()
                                
                                # Allow today's data or yesterday's data if market just opened
                                days_old = (today - bar_date).days
                                
                                if days_old <= 1:  # Today or yesterday
                                    logger.debug(f"✅ {symbol}: Daily bar acceptable - {days_old} day(s) old")
                                    return True
                                else:
                                    logger.warning(f"🚫 {symbol}: Daily bar too old - {days_old} day(s) old")
                                    return False
                            else:
                                logger.warning(f"🚫 {symbol}: Stale intraday data - {data_age_seconds:.0f}s old (max {max_data_age_seconds}s)")
                                return False
                        else:
                            logger.debug(f"✅ {symbol}: Data fresh - {data_age_seconds:.0f}s old")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ {symbol}: Error parsing bar timestamp: {e}")
                        return True  # Assume fresh to avoid blocking valid trades
            
            # Check quote data freshness if available
            if quote_data:
                quote_timestamp = quote_data.get('timestamp')
                if quote_timestamp:
                    try:
                        if isinstance(quote_timestamp, str):
                            quote_ts = datetime.fromisoformat(quote_timestamp.replace('Z', '+00:00'))
                        else:
                            quote_ts = datetime.fromtimestamp(float(quote_timestamp))
                        
                        quote_age_seconds = (now - quote_ts).total_seconds()
                        
                        if quote_age_seconds > max_data_age_seconds:
                            logger.warning(f"🚫 {symbol}: Stale quote data - {quote_age_seconds:.0f}s old")
                            return False
                        else:
                            logger.debug(f"✅ {symbol}: Quote data fresh - {quote_age_seconds:.0f}s old")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ {symbol}: Error parsing quote timestamp: {e}")
            
            return True  # Data is fresh or could not be validated (assume fresh)
            
        except Exception as e:
            logger.error(f"Data freshness validation failed for {symbol}: {e}")
            return True  # Assume fresh to avoid blocking system on validation errors
            
    def get_strategy_statistics(self) -> Dict:
        """Get strategy performance statistics"""
        return {
            'signals_generated': self.signals_generated,
            'strategy_type': 'DYNAMIC_MULTI_STRATEGY',
            'active_strategy_mode': self.active_strategy_mode,
            'current_market_regime': self.current_market_regime,
            'current_volatility_env': self.current_volatility_env,
            'parameters': self.strategy_config
        }
    
    def _check_mean_reversion_setup(self, symbol: str, df: pd.DataFrame, indicators: Dict) -> Optional[TradingSignal]:
        """Check for mean reversion trading setup"""
        try:
            current_price = df['close'].iloc[-1]
            
            # Mean reversion criteria: oversold conditions with support
            rsi = indicators.get('rsi')
            bollinger_position = indicators.get('bb_position', 0.5)
            ma_20 = indicators.get('ma_20', current_price)
            
            # Look for oversold bounce opportunities
            oversold_criteria = [
                rsi < 35 if rsi else False,  # Oversold RSI
                bollinger_position < 0.2,    # Near lower Bollinger Band
                current_price < ma_20 * 0.98, # Below 20-day MA
                df['volume'].iloc[-1] > df['volume'].iloc[-5:-1].mean() * 1.2  # Volume confirmation
            ]
            
            criteria_met = sum(oversold_criteria)
            if criteria_met >= 3:  # Need strong mean reversion setup
                return TradingSignal(
                    symbol=symbol,
                    action='BUY',
                    signal_type='MEAN_REVERSION',
                    entry_price=current_price,
                    stop_loss_price=current_price * 0.96,  # Tight stop for mean reversion
                    take_profit_price=min(ma_20, current_price * 1.04),  # Conservative target
                    position_size_pct=0.01,  # Smaller position for mean reversion
                    confidence=0.65,
                    reasoning=f"Mean reversion: RSI {rsi:.1f}, BB pos {bollinger_position:.2f}",
                    timestamp=datetime.now(),
                    risk_reward_ratio=1.0,
                    max_hold_days=3  # Short hold for mean reversion
                )
            return None
        except Exception as e:
            logger.error(f"Mean reversion setup check failed for {symbol}: {e}")
            return None
    
    def _check_breakout_setup(self, symbol: str, df: pd.DataFrame, indicators: Dict) -> Optional[TradingSignal]:
        """Check for breakout trading setup"""
        try:
            current_price = df['close'].iloc[-1]
            recent_high = df['high'].iloc[-20:].max()  # 20-day high
            recent_low = df['low'].iloc[-20:].min()    # 20-day low
            
            # Breakout criteria: breaking above resistance with volume
            breakout_criteria = [
                current_price > recent_high * 1.005,  # Breaking recent high
                df['volume'].iloc[-1] > df['volume'].iloc[-10:].mean() * 1.5,  # High volume
                indicators.get('rsi', 50) > 55,  # Momentum confirmation
                current_price > indicators.get('ma_20', current_price)  # Above trend
            ]
            
            criteria_met = sum(breakout_criteria)
            if criteria_met >= 3:  # Need strong breakout setup
                return TradingSignal(
                    symbol=symbol,
                    action='BUY',
                    signal_type='BREAKOUT',
                    entry_price=current_price,
                    stop_loss_price=max(recent_low, current_price * 0.94),  # Stop below recent low
                    take_profit_price=current_price * 1.10,  # Higher target for breakouts
                    position_size_pct=0.015,  # Moderate position for breakouts
                    confidence=0.7,
                    reasoning=f"Breakout: Price {current_price:.2f} > high {recent_high:.2f}",
                    timestamp=datetime.now(),
                    risk_reward_ratio=1.8,
                    max_hold_days=7
                )
            return None
        except Exception as e:
            logger.error(f"Breakout setup check failed for {symbol}: {e}")
            return None
    
    def _check_defensive_setup(self, symbol: str, df: pd.DataFrame, indicators: Dict) -> Optional[TradingSignal]:
        """Check for very high-confidence defensive setups only"""
        try:
            # In defensive mode, only trade extremely high-probability setups
            current_price = df['close'].iloc[-1]
            
            # Very strict criteria for defensive trading
            defensive_criteria = [
                indicators.get('rsi', 50) > 60 and indicators.get('rsi', 50) < 75,  # Strong but not overbought
                current_price > indicators.get('ma_20', 0) * 1.02,  # Well above trend
                df['volume'].iloc[-1] > df['volume'].iloc[-10:].mean() * 2.0,  # Very high volume
                df['close'].iloc[-3:].is_monotonic_increasing,  # 3 consecutive up days
                indicators.get('bb_position', 0.5) > 0.6  # Upper part of Bollinger Bands
            ]
            
            criteria_met = sum(defensive_criteria)
            if criteria_met >= 4:  # Need almost all criteria for defensive mode
                return TradingSignal(
                    symbol=symbol,
                    action='BUY',
                    signal_type='DEFENSIVE',
                    entry_price=current_price,
                    stop_loss_price=current_price * 0.97,  # Tight stop in defensive mode
                    take_profit_price=current_price * 1.06,  # Conservative target
                    position_size_pct=0.008,  # Very small position in defensive mode
                    confidence=0.8,  # High confidence required
                    reasoning=f"Defensive: High-probability setup, {criteria_met}/5 criteria",
                    timestamp=datetime.now(),
                    risk_reward_ratio=2.0,
                    max_hold_days=3  # Quick exit in defensive mode
                )
            return None
        except Exception as e:
            logger.error(f"Defensive setup check failed for {symbol}: {e}")
            return None
    
    def _apply_regime_adjustments(self, entry_price: float, stop_price: float, 
                                target_price: float, position_size: float) -> Tuple[float, float, float]:
        """Apply market regime-specific adjustments to signal parameters"""
        try:
            adjusted_stop = stop_price
            adjusted_target = target_price
            adjusted_size = position_size
            
            # Regime-specific adjustments
            if self.current_market_regime == "BEAR_TRENDING":
                # Tighter stops and smaller positions in bear market
                adjusted_stop = max(adjusted_stop, entry_price * 0.97)  # Max 3% stop
                adjusted_size *= 0.7  # Reduce position size by 30%
            
            elif self.current_market_regime == "VOLATILE_RANGE":
                # Wider stops for volatile conditions
                stop_distance = entry_price - adjusted_stop
                adjusted_stop = entry_price - (stop_distance * 1.2)  # 20% wider stops
                adjusted_size *= 0.8  # Slightly smaller positions
            
            elif self.current_volatility_env == "HIGH":
                # Adjust for high volatility
                adjusted_size *= 0.6  # Significantly smaller positions
                # Wider stops to avoid getting stopped out
                stop_distance = entry_price - adjusted_stop
                adjusted_stop = entry_price - (stop_distance * 1.3)
            
            elif self.current_volatility_env == "LOW":
                # Tighter management in low volatility
                adjusted_target = entry_price + ((adjusted_target - entry_price) * 0.8)  # Closer targets
            
            return adjusted_stop, adjusted_target, adjusted_size
            
        except Exception as e:
            logger.error(f"Regime adjustments failed: {e}")
            return stop_price, target_price, position_size
    
    def _get_regime_hold_days(self) -> int:
        """Get appropriate holding period based on market regime"""
        if self.current_market_regime == "VOLATILE_RANGE":
            return 3  # Quick exits in volatile range
        elif self.current_market_regime == "BEAR_TRENDING":
            return 2  # Very quick exits in bear market
        elif self.current_volatility_env == "HIGH":
            return 4  # Shorter holds in high volatility
        else:
            return 7  # Standard holding period