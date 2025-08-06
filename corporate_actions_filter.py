"""
Corporate Actions Filter
Detects stock splits, mergers, symbol changes and other corporate actions
to prevent erroneous trading signals on affected stocks
"""

import logging
from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
from config import *

logger = logging.getLogger(__name__)

class CorporateActionsFilter:
    """
    Filter to detect and handle corporate actions that could affect trading
    """
    
    def __init__(self):
        self.blocked_symbols = {}  # symbol -> block_until_timestamp
        self.corporate_actions_cache = {}  # Cache recent checks
        self.alpha_vantage_key = "demo"  # Will use demo key or get dynamic key
        
    async def check_pre_market_corporate_actions(self, symbols: List[str]) -> Set[str]:
        """
        Check for corporate actions before market opens
        Returns set of symbols to temporarily block from trading
        """
        try:
            logger.info(f"🔍 Checking corporate actions for {len(symbols)} symbols")
            
            blocked_symbols = set()
            
            # Check each symbol for corporate actions
            for symbol in symbols:
                try:
                    # Check cache first
                    cache_key = f"{symbol}_{datetime.now().date()}"
                    if cache_key in self.corporate_actions_cache:
                        logger.debug(f"Using cached corporate actions data for {symbol}")
                        cached_data = self.corporate_actions_cache[cache_key]
                        if cached_data.get('block', False):
                            blocked_symbols.add(symbol)
                        continue
                    
                    # Check for corporate actions
                    has_corporate_action = await self._check_symbol_corporate_actions(symbol)
                    
                    # Cache the result
                    self.corporate_actions_cache[cache_key] = {
                        'block': has_corporate_action,
                        'checked_at': datetime.now()
                    }
                    
                    if has_corporate_action:
                        blocked_symbols.add(symbol)
                        # Block for 3 days to allow indicators to normalize
                        block_until = datetime.now() + timedelta(days=3)
                        self.blocked_symbols[symbol] = block_until
                        logger.warning(f"🚫 {symbol} blocked due to corporate action until {block_until.date()}")
                    
                    # Rate limiting - don't overwhelm APIs
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error checking corporate actions for {symbol}: {e}")
                    continue
            
            # Clean up old blocked symbols
            self._cleanup_expired_blocks()
            
            if blocked_symbols:
                logger.warning(f"🚫 Corporate actions detected - blocking {len(blocked_symbols)} symbols: {blocked_symbols}")
            else:
                logger.info("✅ No corporate actions detected for current watchlist")
            
            return blocked_symbols
            
        except Exception as e:
            logger.error(f"Corporate actions check failed: {e}")
            return set()  # Return empty set on error - don't block trading
    
    async def _check_symbol_corporate_actions(self, symbol: str) -> bool:
        """
        Check individual symbol for corporate actions using multiple methods
        """
        try:
            # Method 1: Check recent price movements for split indicators
            split_detected = await self._detect_potential_split(symbol)
            if split_detected:
                logger.warning(f"🚫 {symbol} potential stock split detected")
                return True
            
            # Method 2: Alpha Vantage corporate actions (if available)
            if await self._has_alpha_vantage_access():
                corporate_action = await self._check_alpha_vantage_corporate_actions(symbol)
                if corporate_action:
                    logger.warning(f"🚫 {symbol} corporate action from Alpha Vantage: {corporate_action}")
                    return True
            
            # Method 3: Check for unusual overnight price gaps
            gap_detected = await self._detect_overnight_gap(symbol)
            if gap_detected:
                logger.warning(f"🚫 {symbol} unusual overnight gap detected")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking corporate actions for {symbol}: {e}")
            return False  # Don't block on error
    
    async def _detect_potential_split(self, symbol: str) -> bool:
        """
        Detect potential stock splits by examining recent price history
        """
        try:
            # Import here to avoid circular imports
            from supplemental_data_provider import SupplementalDataProvider
            
            # Create data provider instance
            data_provider = SupplementalDataProvider()
            
            # Get last 2 days of data to check for split patterns
            recent_bars = await data_provider.get_historical_data(symbol, days=2, min_bars=2)
            
            if recent_bars and len(recent_bars) >= 2:
                yesterday_close = float(recent_bars[-2]['c'])
                today_open = float(recent_bars[-1]['o'])
                
                if yesterday_close > 0 and today_open > 0:
                    price_drop_pct = (yesterday_close - today_open) / yesterday_close
                    
                    # Check for common split ratios
                    if 0.45 < price_drop_pct < 0.55:  # ~50% drop = 2:1 split
                        logger.warning(f"🚫 {symbol}: Potential 2:1 stock split detected ({price_drop_pct:.1%} drop)")
                        return True
                    elif 0.62 < price_drop_pct < 0.72:  # ~67% drop = 3:1 split  
                        logger.warning(f"🚫 {symbol}: Potential 3:1 stock split detected ({price_drop_pct:.1%} drop)")
                        return True
                    elif 0.74 < price_drop_pct < 0.82:  # ~75% drop = 4:1 split
                        logger.warning(f"🚫 {symbol}: Potential 4:1 stock split detected ({price_drop_pct:.1%} drop)")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting split for {symbol}: {e}")
            return False
    
    async def _has_alpha_vantage_access(self) -> bool:
        """Check if we have Alpha Vantage API access"""
        try:
            # Simple check - we'd need a real API key for corporate actions
            return False  # Disabled for now as demo key won't work for this
            
        except Exception as e:
            logger.error(f"Error checking Alpha Vantage access: {e}")
            return False
    
    async def _check_alpha_vantage_corporate_actions(self, symbol: str) -> Optional[str]:
        """
        Check Alpha Vantage for corporate actions
        Note: Requires paid API key for this endpoint
        """
        try:
            # This would use the CORPORATE_ACTIONS endpoint
            # For now, return None as it requires paid access
            
            # url = f"https://www.alphavantage.co/query"
            # params = {
            #     'function': 'CORPORATE_ACTIONS',
            #     'symbol': symbol,
            #     'apikey': self.alpha_vantage_key
            # }
            
            # async with aiohttp.ClientSession() as session:
            #     async with session.get(url, params=params) as response:
            #         data = await response.json()
            #         
            #         if 'Corporate Actions' in data:
            #             # Check for recent actions
            #             actions = data['Corporate Actions']
            #             recent_actions = [a for a in actions if self._is_recent_action(a)]
            #             
            #             if recent_actions:
            #                 return f"Recent corporate actions: {len(recent_actions)}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking Alpha Vantage corporate actions for {symbol}: {e}")
            return None
    
    async def _detect_overnight_gap(self, symbol: str) -> bool:
        """
        Detect unusual overnight price gaps that might indicate corporate actions
        """
        try:
            # Import here to avoid circular imports
            from supplemental_data_provider import SupplementalDataProvider
            
            # Create data provider instance  
            data_provider = SupplementalDataProvider()
            
            # Get last 2 days of data to check for unusual gaps
            recent_bars = await data_provider.get_historical_data(symbol, days=2, min_bars=2)
            
            if recent_bars and len(recent_bars) >= 2:
                yesterday_close = float(recent_bars[-2]['c'])
                today_open = float(recent_bars[-1]['o'])
                
                if yesterday_close > 0 and today_open > 0:
                    gap_pct = abs(today_open - yesterday_close) / yesterday_close
                    
                    # Flag gaps > 15% as potentially suspicious for corporate actions
                    # (Lower threshold than splits since gaps can indicate mergers, spinoffs, etc.)
                    if gap_pct > 0.15:
                        logger.warning(f"🚫 {symbol}: Unusual overnight gap detected ({gap_pct:.1%})")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting overnight gap for {symbol}: {e}")
            return False
    
    def is_symbol_blocked(self, symbol: str) -> bool:
        """
        Check if a symbol is currently blocked due to corporate actions
        """
        if symbol not in self.blocked_symbols:
            return False
        
        block_until = self.blocked_symbols[symbol]
        if datetime.now() > block_until:
            # Block has expired
            del self.blocked_symbols[symbol]
            logger.info(f"✅ {symbol} corporate action block expired")
            return False
        
        return True
    
    def _cleanup_expired_blocks(self):
        """Clean up expired symbol blocks"""
        try:
            expired_symbols = []
            now = datetime.now()
            
            for symbol, block_until in self.blocked_symbols.items():
                if now > block_until:
                    expired_symbols.append(symbol)
            
            for symbol in expired_symbols:
                del self.blocked_symbols[symbol]
                logger.info(f"✅ {symbol} corporate action block expired and removed")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired blocks: {e}")
    
    def get_blocked_symbols_info(self) -> Dict:
        """Get information about currently blocked symbols"""
        return {
            'blocked_symbols': list(self.blocked_symbols.keys()),
            'block_details': {
                symbol: {
                    'blocked_until': block_until.isoformat(),
                    'days_remaining': (block_until - datetime.now()).days
                }
                for symbol, block_until in self.blocked_symbols.items()
            },
            'total_blocked': len(self.blocked_symbols)
        }
    
    async def force_unblock_symbol(self, symbol: str) -> bool:
        """Force unblock a symbol (for manual intervention)"""
        try:
            if symbol in self.blocked_symbols:
                del self.blocked_symbols[symbol]
                logger.info(f"🔓 {symbol} manually unblocked")
                return True
            else:
                logger.info(f"ℹ️ {symbol} was not blocked")
                return False
                
        except Exception as e:
            logger.error(f"Error force unblocking {symbol}: {e}")
            return False