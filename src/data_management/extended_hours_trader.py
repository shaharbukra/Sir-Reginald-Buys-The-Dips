"""
Extended Hours Trading Module
Handles pre-market and after-hours trading with enhanced risk management
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, time
from ..core.config import EXTENDED_HOURS_CONFIG
from .market_status_manager import MarketStatusManager

logger = logging.getLogger(__name__)

class ExtendedHoursTrader:
    """
    Specialized trader for extended hours sessions
    Implements conservative strategies with enhanced risk management
    """
    
    def __init__(self, gateway, risk_manager, market_status):
        self.gateway = gateway
        self.risk_manager = risk_manager
        self.market_status = market_status
        self.active_extended_hours_positions = {}
        self.extended_hours_signals = []
        
    async def should_trade_extended_hours(self) -> bool:
        """Check if extended hours trading should be active"""
        return self.market_status.should_trade_extended_hours()
    
    async def get_extended_hours_opportunities(self) -> List[Dict]:
        """Scan for extended hours trading opportunities"""
        try:
            if not await self.should_trade_extended_hours():
                return []
                
            current_period = self.market_status.is_extended_hours()[1]
            logger.info(f"🔍 Scanning for {current_period} opportunities...")
            
            # Get strategy adjustments for current period
            adjustments = self.market_status.get_extended_hours_strategy_adjustments()
            
            # Enhanced scanning criteria for extended hours
            opportunities = []
            
            # Pre-market specific opportunities
            if "Pre-market" in current_period:
                opportunities.extend(await self._scan_pre_market_opportunities(adjustments))
            
            # After-hours specific opportunities  
            elif "After-hours" in current_period:
                opportunities.extend(await self._scan_after_hours_opportunities(adjustments))
            
            # Filter opportunities based on extended hours criteria
            filtered_opportunities = await self._filter_extended_hours_opportunities(opportunities, adjustments)
            
            logger.info(f"📊 Found {len(filtered_opportunities)} extended hours opportunities")
            return filtered_opportunities
            
        except Exception as e:
            logger.error(f"Extended hours opportunity scan failed: {e}")
            return []
    
    async def _scan_pre_market_opportunities(self, adjustments: Dict) -> List[Dict]:
        """Scan for pre-market specific opportunities"""
        try:
            opportunities = []
            
            # Look for stocks with significant pre-market moves
            # Focus on news catalysts, earnings, and volume surges
            
            # Get top pre-market movers
            movers = await self.gateway.get_top_movers(limit=50)
            if not movers or not movers.success:
                return opportunities
            
            for stock in movers.data:
                symbol = stock.get('symbol')
                change_pct = stock.get('change_percent', 0)
                volume = stock.get('volume', 0)
                
                # Apply pre-market filters
                if self._meets_pre_market_criteria(symbol, change_pct, volume, adjustments):
                    opportunities.append({
                        'symbol': symbol,
                        'change_pct': change_pct,
                        'volume': volume,
                        'opportunity_type': 'pre_market_mover',
                        'score': self._calculate_pre_market_score(change_pct, volume)
                    })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Pre-market opportunity scan failed: {e}")
            return []
    
    async def _scan_after_hours_opportunities(self, adjustments: Dict) -> List[Dict]:
        """Scan for after-hours specific opportunities"""
        try:
            opportunities = []
            
            # Look for stocks with significant after-hours moves
            # Focus on earnings releases, news, and volume patterns
            
            # Get top after-hours movers
            movers = await self.gateway.get_top_movers(limit=50)
            if not movers or not movers.success:
                return opportunities
            
            for stock in movers.data:
                symbol = stock.get('symbol')
                change_pct = stock.get('change_percent', 0)
                volume = stock.get('volume', 0)
                
                # Apply after-hours filters
                if self._meets_after_hours_criteria(symbol, change_pct, volume, adjustments):
                    opportunities.append({
                        'symbol': symbol,
                        'change_pct': change_pct,
                        'volume': volume,
                        'opportunity_type': 'after_hours_mover',
                        'score': self._calculate_after_hours_score(change_pct, volume)
                    })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"After-hours opportunity scan failed: {e}")
            return []
    
    def _meets_pre_market_criteria(self, symbol: str, change_pct: float, volume: int, adjustments: Dict) -> bool:
        """Check if stock meets pre-market trading criteria"""
        try:
            # Basic filters
            if not symbol or volume == 0:
                return False
            
            # Price change threshold
            min_change = adjustments.get('min_price_change_pct', 0.5)
            if abs(change_pct) < min_change:
                return False
            
            # Volume requirements
            min_volume_ratio = adjustments.get('min_volume_ratio', 2.0)
            # This would need actual volume data comparison
            
            # Spread requirements
            max_spread = adjustments.get('max_spread_pct', 1.5)
            # This would need actual spread data
            
            return True
            
        except Exception as e:
            logger.error(f"Pre-market criteria check failed for {symbol}: {e}")
            return False
    
    def _meets_after_hours_criteria(self, symbol: str, change_pct: float, volume: int, adjustments: Dict) -> bool:
        """Check if stock meets after-hours trading criteria"""
        try:
            # Basic filters
            if not symbol or volume == 0:
                return False
            
            # Price change threshold
            min_change = adjustments.get('min_price_change_pct', 0.5)
            if abs(change_pct) < min_change:
                return False
            
            # Volume requirements
            min_volume_ratio = adjustments.get('min_volume_ratio', 2.0)
            # This would need actual volume data comparison
            
            # Spread requirements
            max_spread = adjustments.get('max_spread_pct', 1.5)
            # This would need actual spread data
            
            return True
            
        except Exception as e:
            logger.error(f"After-hours criteria check failed for {symbol}: {e}")
            return False
    
    def _calculate_pre_market_score(self, change_pct: float, volume: int) -> float:
        """Calculate opportunity score for pre-market moves"""
        try:
            # Base score on price movement and volume
            price_score = min(abs(change_pct) * 10, 50)  # Cap at 50
            volume_score = min(volume / 1000000, 30)     # Cap at 30
            
            return price_score + volume_score
            
        except Exception as e:
            logger.error(f"Pre-market score calculation failed: {e}")
            return 0.0
    
    def _calculate_after_hours_score(self, change_pct: float, volume: int) -> float:
        """Calculate opportunity score for after-hours moves"""
        try:
            # Base score on price movement and volume
            price_score = min(abs(change_pct) * 10, 50)  # Cap at 50
            volume_score = min(volume / 1000000, 30)     # Cap at 30
            
            return price_score + volume_score
            
        except Exception as e:
            logger.error(f"After-hours score calculation failed: {e}")
            return 0.0
    
    async def _filter_extended_hours_opportunities(self, opportunities: List[Dict], adjustments: Dict) -> List[Dict]:
        """Filter opportunities based on extended hours criteria"""
        try:
            filtered = []
            
            for opp in opportunities:
                # Apply risk filters
                if await self._passes_extended_hours_risk_check(opp, adjustments):
                    filtered.append(opp)
            
            # Sort by score (highest first)
            filtered.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Limit to top opportunities
            max_opportunities = EXTENDED_HOURS_CONFIG['risk_management']['max_overnight_positions']
            return filtered[:max_opportunities]
            
        except Exception as e:
            logger.error(f"Extended hours opportunity filtering failed: {e}")
            return []
    
    async def _passes_extended_hours_risk_check(self, opportunity: Dict, adjustments: Dict) -> bool:
        """Check if opportunity passes extended hours risk criteria"""
        try:
            symbol = opportunity.get('symbol')
            
            # Check if we already have a position in this symbol
            if symbol in self.active_extended_hours_positions:
                return False
            
            # Check current position count
            if len(self.active_extended_hours_positions) >= EXTENDED_HOURS_CONFIG['risk_management']['max_overnight_positions']:
                return False
            
            # Additional risk checks would go here
            # - News sentiment analysis
            # - Earnings calendar check
            # - Technical analysis
            # - Volume pattern analysis
            
            return True
            
        except Exception as e:
            logger.error(f"Extended hours risk check failed for {opportunity.get('symbol', 'Unknown')}: {e}")
            return False
    
    async def execute_extended_hours_trade(self, opportunity: Dict) -> bool:
        """Execute an extended hours trade with enhanced risk management"""
        try:
            symbol = opportunity.get('symbol')
            logger.info(f"🎯 Executing extended hours trade: {symbol}")
            
            # Get current quote
            quote = await self.gateway.get_quote(symbol)
            if not quote or not quote.success:
                logger.error(f"❌ Could not get quote for {symbol}")
                return False
            
            # Calculate position size based on extended hours limits
            account = await self.gateway.get_account_safe()
            if not account:
                logger.error(f"❌ Could not get account info for {symbol}")
                return False
            
            account_value = float(account.equity)
            max_position_pct = EXTENDED_HOURS_CONFIG['risk_management']['overnight_position_size_pct']
            max_position_value = account_value * max_position_pct
            
            # Get current price
            current_price = float(quote.data.ask_price or quote.data.bid_price)
            if not current_price:
                logger.error(f"❌ Invalid price for {symbol}")
                return False
            
            # Calculate quantity
            quantity = int(max_position_value / current_price)
            if quantity == 0:
                logger.warning(f"⚠️ {symbol}: Position too small to trade")
                return False
            
            # Create extended hours order
            order_data = {
                'symbol': symbol,
                'qty': str(quantity),
                'side': 'buy',
                'type': 'limit',
                'limit_price': str(round(current_price * 1.005, 2)),  # 0.5% above current price
                'time_in_force': 'day',
                'stop_loss': {
                    'stop_price': str(round(current_price * 0.95, 2))  # 5% stop loss
                },
                'take_profit': {
                    'limit_price': str(round(current_price * 1.10, 2))  # 10% take profit
                }
            }
            
            # Submit order
            order_response = await self.gateway.submit_order(order_data)
            if order_response and order_response.success:
                logger.info(f"✅ Extended hours order submitted for {symbol}: {quantity} shares @ ${current_price:.2f}")
                
                # Track the position
                self.active_extended_hours_positions[symbol] = {
                    'order_id': order_response.data.id,
                    'quantity': quantity,
                    'entry_price': current_price,
                    'timestamp': datetime.now()
                }
                
                return True
            else:
                logger.error(f"❌ Extended hours order failed for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Extended hours trade execution failed for {opportunity.get('symbol', 'Unknown')}: {e}")
            return False
    
    async def monitor_extended_hours_positions(self):
        """Monitor and manage extended hours positions"""
        try:
            if not self.active_extended_hours_positions:
                return
            
            logger.info(f"🔍 Monitoring {len(self.active_extended_hours_positions)} extended hours positions")
            
            for symbol, position in list(self.active_extended_hours_positions.items()):
                try:
                    # Check current quote
                    quote = await self.gateway.get_quote(symbol)
                    if not quote or not quote.success:
                        continue
                    
                    current_price = float(quote.data.ask_price or quote.data.bid_price)
                    if not current_price:
                        continue
                    
                    # Calculate P&L
                    entry_price = position['entry_price']
                    pnl_pct = (current_price - entry_price) / entry_price
                    
                    # Check for stop loss or take profit
                    if pnl_pct <= -0.05:  # 5% stop loss
                        logger.warning(f"⚠️ Extended hours stop loss triggered for {symbol}: {pnl_pct:.1%}")
                        await self._close_extended_hours_position(symbol, 'stop_loss')
                    elif pnl_pct >= 0.10:  # 10% take profit
                        logger.info(f"🎯 Extended hours take profit triggered for {symbol}: {pnl_pct:.1%}")
                        await self._close_extended_hours_position(symbol, 'take_profit')
                    
                except Exception as e:
                    logger.error(f"Position monitoring failed for {symbol}: {e}")
                    
        except Exception as e:
            logger.error(f"Extended hours position monitoring failed: {e}")
    
    async def _close_extended_hours_position(self, symbol: str, reason: str):
        """Close an extended hours position"""
        try:
            position = self.active_extended_hours_positions.get(symbol)
            if not position:
                return
            
            # Create sell order
            order_data = {
                'symbol': symbol,
                'qty': str(position['quantity']),
                'side': 'sell',
                'type': 'limit',
                'limit_price': str(round(position['entry_price'] * 0.995, 2)),  # 0.5% below entry
                'time_in_force': 'day'
            }
            
            # Submit sell order
            order_response = await self.gateway.submit_order(order_data)
            if order_response and order_response.success:
                logger.info(f"✅ Extended hours position closed for {symbol}: {reason}")
                del self.active_extended_hours_positions[symbol]
            else:
                logger.error(f"❌ Failed to close extended hours position for {symbol}")
                
        except Exception as e:
            logger.error(f"Extended hours position close failed for {symbol}: {e}")
    
    async def cleanup_overnight_positions(self):
        """Clean up positions before market close to avoid overnight risk"""
        try:
            if not self.active_extended_hours_positions:
                return
            
            logger.info(f"🧹 Cleaning up {len(self.active_extended_hours_positions)} extended hours positions before market close")
            
            for symbol in list(self.active_extended_hours_positions.keys()):
                await self._close_extended_hours_position(symbol, 'market_close_cleanup')
                
        except Exception as e:
            logger.error(f"Extended hours position cleanup failed: {e}")
