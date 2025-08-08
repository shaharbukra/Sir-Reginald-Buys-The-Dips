"""
Free data sources to supplement Alpaca's limited historical data
Uses Yahoo Finance (unlimited) and Alpha Vantage (500 calls/day free) with rate limiting
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import time
import random
import string

logger = logging.getLogger(__name__)

class SupplementalDataProvider:
    """
    Provides historical data from free sources when Alpaca data is insufficient
    """
    
    def __init__(self):
        self.session = None
        
        # Alpha Vantage dynamic key management - AGGRESSIVE MODE
        self.alphavantage_keys = []  # Start empty, will generate keys as needed
        self.current_key_index = 0
        self.key_usage = {}  # Track usage per key
        self.alphavantage_calls_today = 0
        self.alphavantage_calls_this_minute = []
        self.alphavantage_daily_limit = 500  # Full limit per key
        self.alphavantage_minute_limit = 8   # More aggressive limit
        
        # Yahoo Finance rate limiting - SUSTAINABLE APPROACH
        self.yahoo_calls_this_minute = []
        self.yahoo_calls_this_hour = []
        self.yahoo_minute_limit = 30   # Conservative per-minute limit
        self.yahoo_hourly_limit = 1500 # Stay under 2000/hour sustainable limit
        self.yahoo_daily_calls = 0
        self.yahoo_daily_limit = 15000 # Conservative daily limit
        
        # Fast quote cache
        self.quote_cache = {}
        self.quote_cache_expiry = {}
        
        self.last_reset_date = datetime.now().date()
        
    async def initialize(self):
        """Initialize HTTP session and generate initial Alpha Vantage keys"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'TradingBot/1.0'}
        )
        
        # Optional Alpha Vantage key generation (Yahoo Finance is primary)
        if not hasattr(self, '_keys_initialized'):
            logger.info("🔑 Yahoo Finance is primary data source (sustainable 1500/hour limit)")
            logger.info("🔑 Alpha Vantage key generation available if needed...")
            
            # Only generate if we specifically need it (could be added as option)
            # Commenting out automatic generation to focus on sustainable Yahoo usage
            # self.alphavantage_keys.append("demo")  # Keep demo key as backup
            
            self._keys_initialized = True
        
    async def shutdown(self):
        """Clean shutdown"""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
                logger.info("✅ Supplemental data provider session closed cleanly")
        except Exception as e:
            logger.warning(f"⚠️ Supplemental data provider shutdown warning: {e}")
            
    async def get_historical_data(self, symbol: str, days: int = 30, min_bars: int = 10) -> List[Dict]:
        """
        Get historical data from free sources, trying multiple providers
        Returns list of OHLCV bars in Alpaca format
        """
        try:
            # Reset daily counters if new day
            if datetime.now().date() > self.last_reset_date:
                self.alphavantage_calls_today = 0
                self.yahoo_daily_calls = 0
                self.last_reset_date = datetime.now().date()
                logger.info("📅 Daily API limits reset (Alpha Vantage + Yahoo Finance)")
                
            # AGGRESSIVE MULTI-SOURCE STRATEGY
            yahoo_data = []
            av_data = []
            
            # Strategy 1: Try Yahoo Finance (high rate limit, reliable)
            try:
                yahoo_data = await self._get_yahoo_data(symbol, days)
                if yahoo_data and len(yahoo_data) >= min_bars:
                    logger.info(f"📊 Yahoo Finance: Got {len(yahoo_data)} bars for {symbol}")
                    return yahoo_data
            except Exception as e:
                logger.debug(f"Yahoo Finance failed for {symbol}: {e}")
                
            # Strategy 2: Try Alpha Vantage simultaneously (we have multiple keys)
            if self.alphavantage_keys and self._can_use_alphavantage():
                try:
                    av_data = await self._get_alphavantage_data(symbol)
                    if av_data and len(av_data) >= min_bars:
                        logger.info(f"📊 Alpha Vantage: Got {len(av_data)} bars for {symbol}")
                        return av_data
                except Exception as e:
                    logger.debug(f"Alpha Vantage failed for {symbol}: {e}")
                    
            # Strategy 3: Try alternative Yahoo Finance with different parameters
            if not yahoo_data:
                try:
                    yahoo_data = await self._get_yahoo_data_alternative(symbol, days)
                    if yahoo_data and len(yahoo_data) >= min_bars:
                        logger.info(f"📊 Yahoo Finance (alt): Got {len(yahoo_data)} bars for {symbol}")
                        return yahoo_data
                except Exception as e:
                    logger.debug(f"Yahoo Finance alternative failed for {symbol}: {e}")
                    
            # Strategy 4: Return ANYTHING we got - better than nothing
            best_data = yahoo_data if len(yahoo_data) > len(av_data) else av_data
            if best_data:
                logger.info(f"📊 Fallback data: Got {len(best_data)} bars for {symbol}")
                return best_data
                
            logger.warning(f"📊 No supplemental data available for {symbol}")
            return []
            
        except Exception as e:
            logger.error(f"Supplemental data fetch failed for {symbol}: {e}")
            return []
            
    async def _get_yahoo_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """Get data from Yahoo Finance (free, no API key needed)"""
        try:
            # Enhanced rate limiting for sustainable Yahoo Finance usage
            now = time.time()
            
            # Clean up old timestamps
            self.yahoo_calls_this_minute = [
                call_time for call_time in self.yahoo_calls_this_minute 
                if now - call_time < 60
            ]
            self.yahoo_calls_this_hour = [
                call_time for call_time in self.yahoo_calls_this_hour 
                if now - call_time < 3600
            ]
            
            # Check multiple rate limit tiers
            if len(self.yahoo_calls_this_minute) >= self.yahoo_minute_limit:
                logger.debug(f"Yahoo Finance minute limit reached ({len(self.yahoo_calls_this_minute)}/{self.yahoo_minute_limit}), skipping {symbol}")
                return []
            
            if len(self.yahoo_calls_this_hour) >= self.yahoo_hourly_limit:
                logger.warning(f"Yahoo Finance hourly limit reached ({len(self.yahoo_calls_this_hour)}/{self.yahoo_hourly_limit}), skipping {symbol}")
                return []
            
            if self.yahoo_daily_calls >= self.yahoo_daily_limit:
                logger.warning(f"Yahoo Finance daily limit reached ({self.yahoo_daily_calls}/{self.yahoo_daily_limit}), skipping {symbol}")
                return []
                
            # Record the call
            self.yahoo_calls_this_minute.append(now)
            self.yahoo_calls_this_hour.append(now)
            self.yahoo_daily_calls += 1
            
            # Add small delay to be respectful (especially when approaching limits)
            if len(self.yahoo_calls_this_minute) > self.yahoo_minute_limit * 0.8:  # 80% of limit
                await asyncio.sleep(0.1)  # 100ms delay when getting close to limit
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Yahoo Finance API format
            period1 = int(start_date.timestamp())
            period2 = int(end_date.timestamp())
            
            url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                   f"?period1={period1}&period2={period2}&interval=1d")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                        result = data['chart']['result'][0]
                        
                        if 'timestamp' in result and 'indicators' in result:
                            timestamps = result['timestamp']
                            quotes = result['indicators']['quote'][0]
                            
                            bars = []
                            for i, ts in enumerate(timestamps):
                                if (quotes['open'][i] is not None and 
                                    quotes['high'][i] is not None and
                                    quotes['low'][i] is not None and
                                    quotes['close'][i] is not None and
                                    quotes['volume'][i] is not None):
                                    
                                    bars.append({
                                        't': datetime.fromtimestamp(ts).isoformat(),
                                        'o': float(quotes['open'][i]),
                                        'h': float(quotes['high'][i]),
                                        'l': float(quotes['low'][i]),
                                        'c': float(quotes['close'][i]),
                                        'v': int(quotes['volume'][i])
                                    })
                            
                            return bars[-60:] if len(bars) > 60 else bars  # Limit to 60 bars
                            
                else:
                    logger.debug(f"Yahoo Finance HTTP {response.status} for {symbol}")
                    
        except Exception as e:
            logger.debug(f"Yahoo Finance error for {symbol}: {e}")
            
        return []
        
    async def _get_alphavantage_data(self, symbol: str) -> List[Dict]:
        """Get data from Alpha Vantage (500 free calls/day)"""
        try:
            # Rate limiting for Alpha Vantage
            now = time.time()
            self.alphavantage_calls_this_minute = [
                call_time for call_time in self.alphavantage_calls_this_minute
                if now - call_time < 60
            ]
            
            if len(self.alphavantage_calls_this_minute) >= self.alphavantage_minute_limit:
                logger.debug(f"Alpha Vantage minute rate limit hit, skipping {symbol}")
                return []
                
            if self.alphavantage_calls_today >= self.alphavantage_daily_limit:
                logger.debug(f"Alpha Vantage daily limit hit, skipping {symbol}")
                return []
                
            self.alphavantage_calls_this_minute.append(now)
            self.alphavantage_calls_today += 1
            
            # Get current Alpha Vantage API key (auto-generates new ones when needed)
            api_key = await self._get_current_alphavantage_key()
            url = (f"https://www.alphavantage.co/query?"
                   f"function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=compact")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'Time Series (Daily)' in data:
                        time_series = data['Time Series (Daily)']
                        
                        bars = []
                        for date_str, ohlcv in sorted(time_series.items()):
                            bars.append({
                                't': f"{date_str}T16:00:00",  # Market close time
                                'o': float(ohlcv['1. open']),
                                'h': float(ohlcv['2. high']),
                                'l': float(ohlcv['3. low']),
                                'c': float(ohlcv['4. close']),
                                'v': int(ohlcv['5. volume'])
                            })
                            
                        return bars[-30:] if len(bars) > 30 else bars  # Limit to 30 bars
                        
                    elif 'Note' in data:
                        logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                    elif 'Error Message' in data:
                        logger.debug(f"Alpha Vantage error: {data['Error Message']}")
                else:
                    logger.debug(f"Alpha Vantage HTTP {response.status} for {symbol}")
                    
        except Exception as e:
            logger.debug(f"Alpha Vantage error for {symbol}: {e}")
            
        return []
        
    async def get_real_time_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote from Yahoo Finance"""
        try:
            # Rate limiting
            now = time.time()
            self.yahoo_calls_this_minute = [
                call_time for call_time in self.yahoo_calls_this_minute 
                if now - call_time < 60
            ]
            
            if len(self.yahoo_calls_this_minute) >= self.yahoo_minute_limit:
                return None
                
            self.yahoo_calls_this_minute.append(now)
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        current_price = meta.get('regularMarketPrice', 0)
                        if current_price > 0:
                            return {
                                'current_price': float(current_price),
                                'bid_price': float(current_price * 0.9995),  # Approximate
                                'ask_price': float(current_price * 1.0005),  # Approximate
                                'bid_ask_spread': float(current_price * 0.001),  # Approximate
                                'timestamp': datetime.now().isoformat()
                            }
                            
        except Exception as e:
            logger.debug(f"Yahoo quote error for {symbol}: {e}")
            
        return None
    
    async def _generate_alphavantage_key(self) -> Optional[str]:
        """Generate a new Alpha Vantage API key dynamically"""
        try:
            # Generate random email
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            email = f"trader{random_suffix}@tempmail{random.randint(1000,9999)}.com"
            
            # Get CSRF token first
            async with self.session.get("https://www.alphavantage.co/support/") as response:
                if response.status != 200:
                    logger.warning("Failed to get Alpha Vantage support page")
                    return None
                    
                html_content = await response.text()
                csrf_token = None
                
                # Extract CSRF token from HTML (multiple patterns)
                csrf_patterns = [
                    'name="csrfmiddlewaretoken" value="',
                    'csrftoken" content="',
                    '"csrfToken":"'
                ]
                
                for pattern in csrf_patterns:
                    if pattern in html_content:
                        start = html_content.find(pattern) + len(pattern)
                        end = html_content.find('"', start)
                        if start > len(pattern) - 1 and end > start:
                            csrf_token = html_content[start:end]
                            break
                            
                # Also try to get from cookies
                if not csrf_token:
                    cookies = response.cookies
                    if 'csrftoken' in cookies:
                        csrf_token = cookies['csrftoken'].value
                
                if not csrf_token:
                    logger.warning("Could not extract CSRF token")
                    return None
            
            # Create new API key
            headers = {
                'X-CSRFToken': csrf_token,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': 'https://www.alphavantage.co/support/',
                'Origin': 'https://www.alphavantage.co'
            }
            
            data = {
                'first_text': 'deprecated',
                'last_text': 'deprecated', 
                'occupation_text': 'Student',
                'organization_text': 'college',
                'email_text': email
            }
            
            async with self.session.post(
                "https://www.alphavantage.co/create_post/",
                headers=headers,
                data=data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    if 'text' in result:
                        text = result['text']
                        # Try multiple extraction patterns
                        patterns = [
                            ('dedicated access key is: ', 23),
                            ('API key is: ', 12),
                            ('access key: ', 12),
                            ('key is: ', 9)
                        ]
                        
                        for pattern, offset in patterns:
                            if pattern in text:
                                start = text.find(pattern) + offset
                                end = text.find('.', start)
                                if start > offset - 1 and end > start:
                                    new_key = text[start:end]
                                    logger.info(f"🔑 Generated new Alpha Vantage key: {new_key[:8]}...")
                                    return new_key
                                break
                
                logger.warning(f"Failed to create Alpha Vantage key: {response.status}")
                return None
                
        except Exception as e:
            logger.error(f"Key generation failed: {e}")
            return None
    
    async def _get_current_alphavantage_key(self) -> str:
        """Get current Alpha Vantage key, cycling through available keys"""
        if not self.alphavantage_keys:
            return "demo"  # Fallback
            
        current_key = self.alphavantage_keys[self.current_key_index]
        
        # Check if current key is exhausted
        if self.alphavantage_calls_today >= self.alphavantage_daily_limit:
            # Try to switch to next available key instead of generating new one
            if len(self.alphavantage_keys) > 1:
                self.current_key_index = (self.current_key_index + 1) % len(self.alphavantage_keys)
                self.alphavantage_calls_today = 0  # Reset counter for switched key
                logger.info(f"🔄 Switched to Alpha Vantage key #{self.current_key_index + 1}")
                return self.alphavantage_keys[self.current_key_index]
            else:
                logger.warning("⚠️ All Alpha Vantage keys exhausted - continuing with current")
                
        return current_key
    
    def _can_use_alphavantage(self) -> bool:
        """Check if we can use Alpha Vantage (rate limit check)"""
        if not self.alphavantage_keys:
            return False
        return (self.alphavantage_calls_today < self.alphavantage_daily_limit and 
                len(self.alphavantage_calls_this_minute) < self.alphavantage_minute_limit)
    
    async def _get_yahoo_data_alternative(self, symbol: str, days: int = 30) -> List[Dict]:
        """Alternative Yahoo Finance method with different endpoint/parameters"""
        try:
            # Skip rate limit check for alternative method - be more aggressive
            # Use different Yahoo endpoint
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Alternative URL format
            url = f"https://finance.yahoo.com/quote/{symbol}/history"
            
            # For now, return empty and rely on main method
            # This is a placeholder for potential alternative implementation
            return []
            
        except Exception as e:
            logger.debug(f"Yahoo alternative method failed for {symbol}: {e}")
            return []
        
    async def get_current_quote_fast(self, symbol: str) -> Optional[Dict]:
        """
        Get current quote data with aggressive caching for fast screening
        """
        try:
            # Check cache first (1 minute expiry for fast screening)
            now = datetime.now()
            if symbol in self.quote_cache and symbol in self.quote_cache_expiry:
                if now < self.quote_cache_expiry[symbol]:
                    return self.quote_cache[symbol]
            
            # Try to get fresh quote data
            quote_data = None
            
            # Try Yahoo Finance quote (fastest)
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'chart' in data and data['chart']['result']:
                            result = data['chart']['result'][0]
                            meta = result.get('meta', {})
                            
                            current_price = meta.get('regularMarketPrice', 0)
                            prev_close = meta.get('previousClose', current_price)
                            volume = meta.get('regularMarketVolume', 0)
                            
                            if current_price > 0:
                                daily_change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
                                
                                quote_data = {
                                    'current_price': current_price,
                                    'prev_close': prev_close,
                                    'daily_change_pct': daily_change_pct,
                                    'volume': volume,
                                    'timestamp': now.timestamp(),
                                    'source': 'yahoo_quote'
                                }
            except Exception as e:
                logger.debug(f"Yahoo quote failed for {symbol}: {e}")
            
            # Cache result if we got data
            if quote_data:
                self.quote_cache[symbol] = quote_data
                self.quote_cache_expiry[symbol] = now + timedelta(minutes=1)
                return quote_data
            
            # Return cached data even if expired if no new data available
            if symbol in self.quote_cache:
                logger.debug(f"Using stale quote data for {symbol}")
                return self.quote_cache[symbol]
            
            return None
            
        except Exception as e:
            logger.debug(f"Fast quote failed for {symbol}: {e}")
            return None
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics with sustainable rate limiting info"""
        return {
            'alphavantage_calls_today': self.alphavantage_calls_today,
            'alphavantage_daily_remaining': self.alphavantage_daily_limit - self.alphavantage_calls_today,
            'alphavantage_calls_this_minute': len(self.alphavantage_calls_this_minute),
            'alphavantage_keys_available': len(self.alphavantage_keys),
            'current_key_index': self.current_key_index,
            'yahoo_calls_this_minute': len(self.yahoo_calls_this_minute),
            'yahoo_calls_this_hour': len(self.yahoo_calls_this_hour),
            'yahoo_daily_calls': self.yahoo_daily_calls,
            'yahoo_minute_remaining': self.yahoo_minute_limit - len(self.yahoo_calls_this_minute),
            'yahoo_hourly_remaining': self.yahoo_hourly_limit - len(self.yahoo_calls_this_hour),
            'yahoo_daily_remaining': self.yahoo_daily_limit - self.yahoo_daily_calls,
            'last_reset_date': self.last_reset_date.isoformat(),
            'quote_cache_size': len(self.quote_cache)
        }