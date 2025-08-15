"""
Market status manager for trading hours and market conditions
"""

import logging
from typing import Dict, Tuple, List
from datetime import datetime, time, timedelta
import asyncio
import pytz

logger = logging.getLogger(__name__)

class MarketStatusManager:
    """
    Manages market hours, holidays, and trading conditions
    """
    
    def __init__(self, trading_client):
        self.trading_client = trading_client
        self.market_status = None
        self.last_status_check = None
        self.extended_hours_monitoring = True  # Monitor positions outside market hours
        
        # Timezone setup
        self.utc_tz = pytz.UTC
        self.eastern_tz = pytz.timezone('US/Eastern')
        
    def _get_eastern_time(self) -> datetime:
        """Get current time in Eastern Timezone"""
        try:
            # Get current UTC time
            utc_now = datetime.now(self.utc_tz)
            
            # Convert to Eastern Time
            eastern_now = utc_now.astimezone(self.eastern_tz)
            
            return eastern_now
        except Exception as e:
            logger.error(f"Primary timezone conversion failed: {e}")
            logger.info("🔄 Attempting fallback timezone calculation...")
            return self._get_eastern_time_fallback()
    
    def _get_eastern_time_fallback(self) -> datetime:
        """Fallback method for getting Eastern time using manual offset calculation"""
        try:
            # Get current UTC time
            utc_now = datetime.utcnow()
            
            # Manual offset calculation (simplified)
            # This is a basic fallback - not as accurate as pytz but better than nothing
            import time
            local_offset = time.timezone if time.daylight == 0 else time.altzone
            eastern_offset = -5 * 3600  # EST is UTC-5, EDT is UTC-4 (simplified)
            
            # Calculate time difference
            offset_diff = local_offset - eastern_offset
            
            # Apply offset
            eastern_time = utc_now.replace(tzinfo=None) + timedelta(seconds=offset_diff)
            
            logger.warning("⚠️ Using fallback timezone calculation - less accurate than pytz")
            return eastern_time
            
        except Exception as e:
            logger.error(f"Fallback timezone calculation failed: {e}")
            # Last resort - return local time
            return datetime.now()
    
    async def should_start_trading(self) -> Tuple[bool, str]:
        """Determine if trading should start"""
        try:
            # Get current time in Eastern Timezone
            current_time = self._get_eastern_time()
            
            # Check if it's a weekday
            if current_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False, "Weekend - market closed"
                
            # Check market hours (Eastern Time)
            market_open = time(9, 30)  # 9:30 AM ET
            market_close = time(16, 0)  # 4:00 PM ET
            current_time_only = current_time.time()
            
            logger.debug(f"🕐 Current Eastern Time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            logger.debug(f"🕐 Market Open: {market_open}, Market Close: {market_close}")
            logger.debug(f"🕐 Current Time: {current_time_only}")
            
            if current_time_only < market_open:
                minutes_until_open = (datetime.combine(current_time.date(), market_open) - 
                                    datetime.combine(current_time.date(), current_time_only)).total_seconds() / 60
                return False, f"Market opens in {minutes_until_open:.0f} minutes"
                
            if current_time_only > market_close:
                return False, "Market closed for the day"
                
            # Market is open
            return True, "Market is open for trading"
            
        except Exception as e:
            logger.error(f"Market status check failed: {e}")
            return False, f"Error checking market status: {e}"
            
    async def wait_for_market_open(self):
        """Wait for market to open"""
        try:
            while True:
                should_trade, reason = await self.should_start_trading()
                
                if should_trade:
                    logger.info("📈 Market is open - ready to trade")
                    break
                    
                logger.info(f"⏰ {reason} - waiting...")
                await asyncio.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Market open wait cancelled")
            raise
        except Exception as e:
            logger.error(f"Error waiting for market open: {e}")
            
    async def is_market_open(self) -> bool:
        """Quick check if market is currently open"""
        should_trade, _ = await self.should_start_trading()
        return should_trade
    
    def is_extended_hours(self) -> Tuple[bool, str]:
        """Check if we're in pre-market or after-hours period"""
        try:
            # Get current time in Eastern Timezone
            current_time = self._get_eastern_time()
            
            # Skip weekends entirely
            if current_time.weekday() >= 5:
                return False, "Weekend"
            
            current_time_only = current_time.time()
            
            # Extended hours periods
            premarket_start = time(4, 0)   # 4:00 AM ET
            market_open = time(9, 30)      # 9:30 AM ET  
            market_close = time(16, 0)     # 4:00 PM ET
            afterhours_end = time(20, 0)   # 8:00 PM ET
            
            logger.debug(f"🕐 Extended hours check - Current ET: {current_time.strftime('%H:%M:%S %Z')}")
            logger.debug(f"🕐 Pre-market: {premarket_start} - {market_open}")
            logger.debug(f"🕐 Market: {market_open} - {market_close}")
            logger.debug(f"🕐 After-hours: {market_close} - {afterhours_end}")
            
            if premarket_start <= current_time_only < market_open:
                return True, "Pre-market (4:00 AM - 9:30 AM ET)"
            elif market_close < current_time_only <= afterhours_end:
                return True, "After-hours (4:00 PM - 8:00 PM ET)"
            elif current_time_only > afterhours_end or current_time_only < premarket_start:
                return True, "Overnight (8:00 PM - 4:00 AM ET)"
            else:
                return False, "Regular market hours"
                
        except Exception as e:
            logger.error(f"Extended hours check failed: {e}")
            return False, "Error"
    
    def should_monitor_positions_extended_hours(self) -> bool:
        """Determine if we should monitor positions during extended hours"""
        is_extended, period = self.is_extended_hours()
        if is_extended and period != "Weekend":
            return True
        return False
    
    def get_current_time_info(self) -> Dict[str, str]:
        """Get current time information for debugging"""
        try:
            utc_now = datetime.now(self.utc_tz)
            eastern_now = self._get_eastern_time()
            local_now = datetime.now()
            
            return {
                'utc_time': utc_now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'eastern_time': eastern_now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'local_time': local_now.strftime('%Y-%m-%d %H:%M:%S'),
                'eastern_weekday': eastern_now.strftime('%A'),
                'eastern_hour': str(eastern_now.hour),
                'eastern_minute': str(eastern_now.minute)
            }
        except Exception as e:
            logger.error(f"Time info retrieval failed: {e}")
            return {'error': str(e)}
    
    def should_trade_extended_hours(self) -> bool:
        """Determine if we should actively trade during extended hours"""
        try:
            from config import EXTENDED_HOURS_CONFIG
            
            # Check if extended hours trading is enabled in config
            if not EXTENDED_HOURS_CONFIG.get('enable_trading', False):
                return False
                
            is_extended, period = self.is_extended_hours()
            
            if not is_extended or period == "Weekend":
                return False
                
            # Check specific trading hours
            if period == "Pre-market (4:00 AM - 9:30 AM ET)":
                return EXTENDED_HOURS_CONFIG['trading_hours']['pre_market']['enabled']
            elif period == "After-hours (4:00 PM - 8:00 PM ET)":
                return EXTENDED_HOURS_CONFIG['trading_hours']['after_hours']['enabled']
            elif period == "Overnight (8:00 PM - 4:00 AM ET)":
                # Overnight trading is generally not recommended
                return False
                
            return False
            
        except Exception as e:
            logger.error(f"Extended hours trading check failed: {e}")
            return False
    
    def get_extended_hours_strategy_adjustments(self) -> Dict:
        """Get strategy adjustments for extended hours trading"""
        try:
            from config import EXTENDED_HOURS_CONFIG
            
            is_extended, period = self.is_extended_hours()
            
            if not is_extended:
                return {}
                
            if period == "Pre-market (4:00 AM - 9:30 AM ET)":
                return EXTENDED_HOURS_CONFIG['trading_hours']['pre_market']['strategy_adjustments']
            elif period == "After-hours (4:00 PM - 8:00 PM ET)":
                return EXTENDED_HOURS_CONFIG['trading_hours']['after_hours']['strategy_adjustments']
                
            return {}
            
        except Exception as e:
            logger.error(f"Strategy adjustments check failed: {e}")
            return {}
    
    def get_allowed_order_types(self) -> List[str]:
        """Get allowed order types based on current market hours"""
        try:
            from config import EXTENDED_HOURS_CONFIG
            
            is_extended, period = self.is_extended_hours()
            
            if not is_extended:
                return EXTENDED_HOURS_CONFIG['order_types']['regular_hours']
                
            if period == "Pre-market (4:00 AM - 9:30 AM ET)":
                return EXTENDED_HOURS_CONFIG['order_types']['pre_market']
            elif period == "After-hours (4:00 PM - 8:00 PM ET)":
                return EXTENDED_HOURS_CONFIG['order_types']['after_hours']
                
            return EXTENDED_HOURS_CONFIG['order_types']['regular_hours']
            
        except Exception as e:
            logger.error(f"Order types check failed: {e}")
            return ['limit']  # Default to safest option