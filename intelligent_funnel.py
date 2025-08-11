"""
Intelligent Funnel: Market-wide opportunity discovery with surgical API usage
Three-stage funnel: Broad Scan → AI Filtering → Deep Dive Analysis
Enhanced with Tiered Analysis System for comprehensive coverage
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import json
from config import *
from tiered_analyzer import TieredAnalyzer, AnalysisResult, AnalysisTier

logger = logging.getLogger(__name__)

@dataclass
class MarketOpportunity:
    """Comprehensive market opportunity with discovery metadata"""
    symbol: str
    discovery_source: str
    discovery_timestamp: datetime
    
    # Price and volume data
    current_price: float
    daily_change_pct: float
    volume: int
    avg_volume: float
    volume_ratio: float
    
    # Market data
    market_cap: float
    sector: str
    beta: float = 1.0
    
    # Technical indicators
    rsi: Optional[float] = None
    ma_10: Optional[float] = None
    ma_20: Optional[float] = None
    ma_50: Optional[float] = None
    atr: Optional[float] = None
    
    # Opportunity scoring
    opportunity_score: float = 0.0
    confidence: float = 0.0
    expected_return_pct: float = 0.0
    risk_level: str = "MEDIUM"
    time_horizon_days: int = 5
    
    # Analysis metadata
    primary_catalyst: str = ""
    technical_setup: str = ""
    news_sentiment: str = "NEUTRAL"
    ai_reasoning: str = ""
    
    # Tracking
    times_analyzed: int = 0
    last_analysis: Optional[datetime] = None
    watchlist_entry_time: Optional[datetime] = None

class RateLimitTracker:
    """Sophisticated rate limit tracking with priority management"""
    
    def __init__(self):
        self.request_history = deque(maxlen=200)  # Track last 200 requests
        self.budget_allocation = RATE_LIMIT_CONFIG['budget_allocation'].copy()
        self.used_budget = defaultdict(int)
        self.priority_queue = defaultdict(list)
        self.reset_time = datetime.now()
        
    def can_make_request(self, category: str, priority: int = 5) -> bool:
        """Check if request can be made within budget and limits - UNLIMITED MODE"""
        # With unlimited Alpha Vantage keys, always allow requests
        # Just do basic cleanup to prevent memory bloat
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        while self.request_history and self.request_history[0] < cutoff:
            self.request_history.popleft()
            
        # Always return True for unlimited scanning
        return True
        
    def record_request(self, category: str):
        """Record API request"""
        now = datetime.now()
        self.request_history.append(now)
        self.used_budget[category] += 1
        
    def reset_budgets(self):
        """Reset category budgets (called every minute)"""
        self.used_budget.clear()
        self.reset_time = datetime.now()
        
    def get_remaining_budget(self, category: str) -> int:
        """Get remaining budget for category"""
        return max(0, self.budget_allocation.get(category, 0) - self.used_budget[category])

class IntelligentMarketFunnel:
    """
    Three-stage intelligent funnel for market-wide opportunity discovery
    Designed for maximum market coverage with minimal API usage
    """
    
    def __init__(self, gateway, ai_assistant, supplemental_data_provider=None, strategy=None):
        self.gateway = gateway
        self.ai_assistant = ai_assistant
        self.rate_limiter = RateLimitTracker()
        
        # Initialize tiered analyzer for comprehensive coverage
        if supplemental_data_provider and strategy:
            self.tiered_analyzer = TieredAnalyzer(gateway, supplemental_data_provider, strategy)
            logger.info("🔧 Tiered Analyzer initialized for comprehensive stock coverage")
        else:
            self.tiered_analyzer = None
        
        # State management
        self.current_watchlist: Dict[str, MarketOpportunity] = {}
        self.discovery_cache = {}
        self.market_regime = MarketRegime.BULL_TRENDING
        self.last_broad_scan = None
        self.scanning_active = False
        
        # Dynamic asset universe
        self.asset_universe = []  # All tradeable assets from Alpaca
        self.last_universe_update = None
        
        # Performance tracking
        self.scan_statistics = {
            'total_scans': 0,
            'opportunities_found': 0,
            'api_calls_used': 0,
            'successful_trades': 0
        }
        
    async def _update_asset_universe(self):
        """Update the dynamic asset universe from Alpaca"""
        try:
            # Update universe once per day or if empty
            now = datetime.now()
            if (not self.asset_universe or 
                not self.last_universe_update or
                (now - self.last_universe_update).total_seconds() > 86400):  # 24 hours
                
                logger.info("🔄 Updating dynamic asset universe...")
                assets = await self.gateway.get_all_assets()
                
                if assets:
                    # Filter out problematic symbols
                    filtered_assets = []
                    for asset in assets:
                        symbol = asset['symbol']
                        
                        # Skip crypto and forex
                        crypto_patterns = ['USD', 'BTC', 'ETH', 'USDT', 'EUR', 'GBP', 'JPY', 'CRYPTO', 'COIN']
                        if any(crypto in symbol.upper() for crypto in crypto_patterns):
                            continue
                            
                        # Skip USD-ending symbols
                        if symbol.upper().endswith('USD'):
                            continue
                            
                        # Skip very long symbols (likely derivatives)
                        if len(symbol) > 5:
                            continue
                            
                        # Skip symbols with special characters
                        if not symbol.replace('.', '').replace('-', '').isalnum():
                            continue
                            
                        filtered_assets.append(asset)
                    
                    self.asset_universe = filtered_assets
                    self.last_universe_update = now
                    logger.info(f"✅ Updated asset universe: {len(self.asset_universe)} tradeable symbols")
                else:
                    logger.warning("⚠️ No assets returned from API, keeping existing universe")
                    
        except Exception as e:
            logger.error(f"Failed to update asset universe: {e}")
    
    async def execute_intelligent_funnel(self) -> List[MarketOpportunity]:
        """
        Main funnel execution: Broad Scan → AI Filtering → Deep Dive
        Returns ranked list of high-conviction opportunities
        """
        try:
            if self.scanning_active:
                logger.debug("Scan already in progress, skipping")
                return list(self.current_watchlist.values())
                
            self.scanning_active = True
            start_time = datetime.now()
            
            logger.info("🔍 Starting intelligent market funnel scan...")
            
            # First, ensure we have a current asset universe
            await self._update_asset_universe()
            
            # STEP 1: Broad Market Scan (2-5 API calls)
            broad_candidates = await self._execute_broad_scan()
            logger.info(f"📊 Broad scan found {len(broad_candidates)} candidates")
            
            if not broad_candidates:
                logger.warning("No candidates from broad scan")
                return []
                
            # STEP 2: AI-Powered Strategic Filtering (0 API calls)
            filtered_candidates = await self._execute_ai_filtering(broad_candidates)
            logger.info(f"🧠 AI filtering selected {len(filtered_candidates)} candidates")
            
            # STEP 3: Deep Dive Analysis (15-20 API calls)
            final_opportunities = await self._execute_deep_dive(filtered_candidates)
            logger.info(f"🎯 Deep dive analysis identified {len(final_opportunities)} opportunities")
            
            # Update watchlist
            await self._update_dynamic_watchlist(final_opportunities)
            
            # Update statistics
            scan_duration = (datetime.now() - start_time).total_seconds()
            self.scan_statistics['total_scans'] += 1
            self.scan_statistics['opportunities_found'] += len(final_opportunities)
            
            logger.info(f"✅ Funnel scan completed in {scan_duration:.2f}s, "
                       f"found {len(final_opportunities)} opportunities")
                       
            return final_opportunities
            
        except Exception as e:
            logger.error(f"❌ Intelligent funnel scan failed: {e}")
            return []
        finally:
            self.scanning_active = False
    
    async def execute_tiered_analysis(self, symbols: List[str], priority_level: str = "HIGH") -> List[AnalysisResult]:
        """
        Execute comprehensive tiered analysis to ensure no good stocks are missed
        This is the ROBUST SOLUTION for handling rate limits and data issues
        """
        if not self.tiered_analyzer:
            logger.warning("⚠️ Tiered analyzer not available - falling back to standard analysis")
            return []
        
        logger.info(f"🔍 Executing tiered analysis for {len(symbols)} stocks (priority: {priority_level})")
        
        try:
            # Execute the comprehensive tiered analysis
            results = await self.tiered_analyzer.analyze_stock_list(symbols, priority_level)
            
            # Filter for actionable results
            actionable_results = [
                r for r in results 
                if r.recommendation in ['BUY', 'SELL'] and r.signal_strength > 0.6
            ]
            
            logger.info(f"✅ Tiered analysis complete: {len(actionable_results)} actionable signals from {len(results)} analyzed")
            
            # Log summary statistics
            summary = self.tiered_analyzer.get_analysis_summary()
            logger.info(f"📊 Analysis Stats: {summary['statistics']}")
            
            return actionable_results
            
        except Exception as e:
            logger.error(f"❌ Tiered analysis failed: {e}")
            return []
    
    async def analyze_hot_stocks(self, symbols: List[str]) -> List[AnalysisResult]:
        """
        Analyze specific "hot" stocks mentioned by traders/news with HIGH priority
        Ensures these high-potential stocks get full analysis regardless of system load
        """
        logger.info(f"🔥 Analyzing {len(symbols)} hot stocks with maximum priority")
        
        if not self.tiered_analyzer:
            logger.warning("⚠️ Tiered analyzer not available")
            return []
        
        # Use HIGH priority to ensure these get processed
        results = await self.execute_tiered_analysis(symbols, priority_level="HIGH")
        
        # Log detailed results for hot stocks
        for result in results:
            logger.info(f"🎯 HOT STOCK {result.symbol}: {result.recommendation} "
                       f"(strength: {result.signal_strength:.2f}, confidence: {result.confidence:.2f}) "
                       f"- {result.reasoning}")
        
        return results
            
    async def _execute_broad_scan(self) -> List[MarketOpportunity]:
        """
        STEP 1: Broad market scan using efficient Alpaca endpoints
        Target: 5,000+ stocks → 50-100 candidates with 2-5 API calls
        """
        try:
            all_candidates = []
            api_calls_used = 0
            
            # 1. Market Movers (Top Gainers/Losers) - 2 API calls
            if FUNNEL_CONFIG['broad_scan_apis']['market_movers']:
                if self.rate_limiter.can_make_request('discovery', priority=4):
                    gainers = await self._get_market_movers('gainers')
                    self.rate_limiter.record_request('discovery')
                    api_calls_used += 1
                    
                if self.rate_limiter.can_make_request('discovery', priority=4):
                    losers = await self._get_market_movers('losers')
                    self.rate_limiter.record_request('discovery')
                    api_calls_used += 1
                    
                    movers = (gainers or []) + (losers or [])
                    all_candidates.extend(movers)
                    logger.debug(f"Market movers: {len(movers)} candidates")
                    
            # 2. Most Active Stocks (Volume Leaders) - 1 API call
            if FUNNEL_CONFIG['broad_scan_apis']['most_active']:
                if self.rate_limiter.can_make_request('discovery', priority=4):
                    active_stocks = await self._get_most_active_stocks()
                    self.rate_limiter.record_request('discovery')
                    api_calls_used += 1
                    
                    if active_stocks:
                        all_candidates.extend(active_stocks)
                        logger.debug(f"Most active: {len(active_stocks)} candidates")
                        
            # 3. News-Driven Movers - 1 API call
            if FUNNEL_CONFIG['broad_scan_apis']['news_movers']:
                if self.rate_limiter.can_make_request('discovery', priority=4):
                    news_movers = await self._get_news_driven_movers()
                    self.rate_limiter.record_request('discovery')
                    api_calls_used += 1
                    
                    if news_movers:
                        all_candidates.extend(news_movers)
                        logger.debug(f"News movers: {len(news_movers)} candidates")
                        
            # 4. Unusual Volume Detection - 1 API call
            if FUNNEL_CONFIG['broad_scan_apis']['unusual_volume']:
                if self.rate_limiter.can_make_request('discovery', priority=4):
                    volume_anomalies = await self._detect_unusual_volume()
                    self.rate_limiter.record_request('discovery')
                    api_calls_used += 1
                    
                    if volume_anomalies:
                        all_candidates.extend(volume_anomalies)
                        logger.debug(f"Volume anomalies: {len(volume_anomalies)} candidates")
                        
            # Deduplicate and apply basic filters
            unique_candidates = self._deduplicate_candidates(all_candidates)
            filtered_candidates = self._apply_basic_filters(unique_candidates)
            
            logger.info(f"📊 Broad scan: {api_calls_used} API calls → {len(filtered_candidates)} candidates")
            self.scan_statistics['api_calls_used'] += api_calls_used
            
            # 5. Add comprehensive market scan for unlimited Alpha Vantage scenario
            if FUNNEL_CONFIG['broad_scan_apis'].get('comprehensive_scan', False):
                if self.rate_limiter.can_make_request('discovery', priority=3):
                    comprehensive_results = await self._execute_comprehensive_market_scan()
                    if comprehensive_results:
                        all_candidates.extend(comprehensive_results)
                        logger.info(f"Comprehensive scan: {len(comprehensive_results)} additional candidates")
            
            # Deduplicate and apply basic filters
            unique_candidates = self._deduplicate_candidates(all_candidates)
            filtered_candidates = self._apply_basic_filters(unique_candidates)
            
            logger.info(f"📊 Broad scan: {api_calls_used} API calls → {len(filtered_candidates)} candidates")
            self.scan_statistics['api_calls_used'] += api_calls_used
            
            return filtered_candidates[:FUNNEL_CONFIG['max_broad_scan_results']]
            
        except Exception as e:
            logger.error(f"Broad scan failed: {e}")
            return []
            
    async def _execute_ai_filtering(self, candidates: List[MarketOpportunity]) -> List[MarketOpportunity]:
        """
        STEP 2: AI-powered strategic filtering (0 API calls)
        Target: 50-100 candidates → 20-30 high-potential candidates
        """
        try:
            # Get current market regime analysis
            market_context = await self._get_market_regime_analysis()
            self.market_regime = MarketRegime(market_context.get('regime', 'bull_trending'))
            
            # Apply regime-specific filtering
            regime_criteria = SCREENING_CRITERIA['regime_criteria'].get(self.market_regime, {})
            
            # Get account size for price filtering (if available)
            account_value = None
            try:
                if hasattr(self, 'gateway') and self.gateway:
                    account = await self.gateway.get_account_safe()
                    if account:
                        account_value = float(account.equity)
            except:
                account_value = None
            
            filtered_candidates = []
            sector_counts = {}  # Track sector diversification (Grok feedback)
            price_filtered_count = 0
            
            for candidate in candidates:
                # Account-size-aware price filtering (prioritize affordable stocks for small accounts)
                if account_value and account_value < 10000:
                    # For small accounts, prioritize stocks that allow proper position sizing
                    expensive_stocks = ['GOOGL', 'GOOG', 'AMZN', 'TSLA', 'BRK.A', 'BRK.B', 'NVDA', 'META']
                    max_affordable_price = (account_value * 0.08) / 1.05  # 8% of account after slippage
                    
                    if (candidate.symbol in expensive_stocks or 
                        candidate.current_price > max_affordable_price):
                        price_filtered_count += 1
                        logger.debug(f"💰 {candidate.symbol}: Filtered due to price ${candidate.current_price:.0f} (>${max_affordable_price:.0f} max for ${account_value:,.0f} account)")
                        continue
                
                # Apply market regime filters
                meets_criteria = self._meets_regime_criteria(candidate, regime_criteria)
                logger.debug(f"📊 {candidate.symbol}: change={candidate.daily_change_pct:.1f}%, vol_ratio={candidate.volume_ratio:.1f}, sector={candidate.sector}, meets_criteria={meets_criteria}")
                
                if meets_criteria:
                    # Calculate preliminary opportunity score
                    candidate.opportunity_score = self._calculate_preliminary_score(
                        candidate, market_context, regime_criteria
                    )
                    
                    if candidate.opportunity_score >= 0.2:  # Restored to reasonable threshold
                        # Apply sector diversification (Grok's recommendation)
                        candidate_sector = getattr(candidate, 'sector', 'UNKNOWN')
                        current_sector_count = sector_counts.get(candidate_sector, 0)
                        
                        # Limit sector concentration (max 3 per sector)
                        if current_sector_count < 3:
                            filtered_candidates.append(candidate)
                            sector_counts[candidate_sector] = current_sector_count + 1
                            logger.debug(f"   ✅ {candidate.symbol}: score={candidate.opportunity_score:.2f}, sector={candidate_sector} ({current_sector_count+1}/3)")
                        elif candidate.opportunity_score > 0.8:  # Exception for high-quality opportunities
                            filtered_candidates.append(candidate)
                            sector_counts[candidate_sector] = current_sector_count + 1
                            logger.info(f"🎯 High-quality sector exception: {candidate.symbol} ({candidate_sector}) score={candidate.opportunity_score:.2f}")
                        else:
                            logger.debug(f"   🚫 {candidate.symbol}: sector limit reached for {candidate_sector} ({current_sector_count}/3)")
                    else:
                        logger.debug(f"   ❌ {candidate.symbol}: score={candidate.opportunity_score:.2f} (below threshold)")
                        
            # Sort by opportunity score and return top candidates
            filtered_candidates.sort(key=lambda x: x.opportunity_score, reverse=True)
            top_candidates = filtered_candidates[:FUNNEL_CONFIG['deep_dive_candidates']]
            
            # Log sector distribution for transparency
            final_sectors = {}
            for candidate in top_candidates:
                sector = getattr(candidate, 'sector', 'UNKNOWN')
                final_sectors[sector] = final_sectors.get(sector, 0) + 1
            
            logger.info(f"🧠 AI filtering: {len(candidates)} → {len(top_candidates)} candidates "
                       f"(regime: {self.market_regime.value})")
            if price_filtered_count > 0:
                logger.info(f"💰 Price filtering: {price_filtered_count} expensive stocks filtered for small account")
            if final_sectors:
                logger.info(f"🏢 Sector diversification: {dict(final_sectors)}")
                       
            return top_candidates
            
        except Exception as e:
            logger.warning(f"⚠️ AI FILTERING FAILURE: {e}")
            logger.warning(f"⚠️ Falling back to technical filtering for candidate selection")
            return candidates[:FUNNEL_CONFIG['deep_dive_candidates']]
            
    async def _execute_deep_dive(self, candidates: List[MarketOpportunity]) -> List[MarketOpportunity]:
        """
        STEP 3: Deep dive analysis on top candidates (15-20 API calls)
        Target: 20-30 candidates → 5-10 high-conviction opportunities
        """
        try:
            analyzed_opportunities = []
            api_calls_used = 0
            max_api_calls = FUNNEL_CONFIG['deep_dive_api_budget']
            
            for candidate in candidates:
                if api_calls_used >= max_api_calls:
                    logger.warning(f"Deep dive API budget exhausted at {api_calls_used} calls")
                    break
                    
                # Detailed technical analysis
                if self.rate_limiter.can_make_request('analysis', priority=3):
                    technical_data = await self._get_detailed_technicals(candidate.symbol)
                    if technical_data:
                        candidate = self._update_candidate_technicals(candidate, technical_data)
                        self.rate_limiter.record_request('analysis')
                        api_calls_used += 1
                        
                # News analysis for catalyst detection
                if (NEWS_CONFIG['enable_news_analysis'] and 
                    self.rate_limiter.can_make_request('analysis', priority=3)):
                    news_data = await self._get_news_analysis(candidate.symbol)
                    if news_data:
                        candidate = self._update_candidate_news(candidate, news_data)
                        self.rate_limiter.record_request('analysis')
                        api_calls_used += 1
                        
                # AI-powered final scoring
                final_score = await self._calculate_final_ai_score(candidate)
                candidate.opportunity_score = final_score
                candidate.last_analysis = datetime.now()
                candidate.times_analyzed += 1
                
                # Only keep high-conviction opportunities
                if candidate.opportunity_score >= 0.7 and candidate.confidence >= 0.6:
                    analyzed_opportunities.append(candidate)
                    
            # Final ranking by AI opportunity score
            analyzed_opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)
            
            logger.info(f"🎯 Deep dive: {api_calls_used} API calls → {len(analyzed_opportunities)} opportunities")
            self.scan_statistics['api_calls_used'] += api_calls_used
            
            return analyzed_opportunities[:10]  # Top 10 opportunities
            
        except Exception as e:
            logger.error(f"Deep dive analysis failed: {e}")
            return []
            
    async def _get_market_movers(self, direction: str) -> List[MarketOpportunity]:
        """Get top gainers or losers from Alpaca API"""
        try:
            # Use real Alpaca market movers API
            movers_data = await self.gateway.get_market_movers(direction, limit=25)
            
            opportunities = []
            for data in movers_data:
                # Parse real Alpaca API response
                symbol = data.get('symbol', '')
                
                # Skip crypto and forex symbols - comprehensive filtering
                crypto_patterns = ['USD', 'BTC', 'ETH', 'USDT', 'EUR', 'GBP', 'JPY', 'CRYPTO', 'COIN']
                if any(crypto in symbol.upper() for crypto in crypto_patterns):
                    logger.debug(f"Skipping crypto/forex symbol: {symbol}")
                    continue
                
                # Skip invalid or problematic symbols
                invalid_symbols = ['NDTAF', 'BRK.A', 'BRK.B']  # Common invalid/problematic symbols
                invalid_patterns = ['.A', '.B', 'TEST', 'TEMP']
                if (symbol in invalid_symbols or 
                    any(pattern in symbol for pattern in invalid_patterns) or
                    len(symbol) > 5 or len(symbol) < 1):
                    logger.debug(f"Skipping invalid symbol: {symbol}")
                    continue
                    
                # Skip if symbol ends with USD (common crypto pattern)
                if symbol.upper().endswith('USD'):
                    logger.debug(f"Skipping USD-ending symbol: {symbol}")
                    continue
                    
                # Skip if symbol is too long (likely crypto pair)
                if len(symbol) > 5:
                    logger.debug(f"Skipping long symbol: {symbol}")
                    continue
                
                price = float(data.get('price', 0)) if data.get('price') else 0
                change_pct = float(data.get('change_percent', 0)) if data.get('change_percent') else 0
                volume = int(data.get('volume', 0)) if data.get('volume') else 0
                
                if symbol and price > SCREENING_CRITERIA['min_price']:
                    opportunity = MarketOpportunity(
                        symbol=symbol,
                        discovery_source=f'market_{direction}',
                        discovery_timestamp=datetime.now(),
                        current_price=price,
                        daily_change_pct=change_pct,
                        volume=volume,
                        avg_volume=volume / 1.5,  # Estimate from volume
                        volume_ratio=1.5,
                        market_cap=self._estimate_market_cap(symbol),
                        sector=self._get_sector(symbol),
                    )
                    opportunities.append(opportunity)
                    
            # Fallback to dynamic discovery if API returns no data
            if not opportunities:
                logger.info(f"No live {direction} data, using dynamic discovery")
                return await self._get_dynamic_market_movers(direction)
                
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to get market {direction}: {e}")
            # Fallback to dynamic discovery
            return await self._get_dynamic_market_movers(direction)
    
    async def _get_dynamic_market_movers(self, direction: str) -> List[MarketOpportunity]:
        """Dynamic market movers discovery using real asset universe and live data"""
        if not self.asset_universe:
            logger.warning("No asset universe available for dynamic discovery")
            return []
            
        logger.info(f"🔍 Dynamic discovery: scanning {len(self.asset_universe)} assets for {direction}")
        
        # Sample from universe - focus on liquid, major exchange symbols
        candidate_symbols = []
        for asset in self.asset_universe:
            symbol = asset['symbol']
            if (asset.get('exchange') in ['NYSE', 'NASDAQ', 'NYSEARCA'] and 
                len(symbol) <= 4 and symbol.isalpha()):
                candidate_symbols.append(symbol)
        
        # More comprehensive sampling for better opportunity discovery
        import random
        
        # With unlimited Alpha Vantage keys, scan much more comprehensively
        sample_size = min(100, len(candidate_symbols))  # Fast execution - focus on top candidates
        test_symbols = random.sample(candidate_symbols, sample_size)
        
        opportunities = []
        symbols_tested = 0
        
        for symbol in test_symbols:
            if len(opportunities) >= 100:  # Find up to 100 opportunities per direction
                break
                
            try:
                # Use supplemental data provider to avoid Alpaca rate limits
                from supplemental_data_provider import SupplementalDataProvider
                
                data_provider = SupplementalDataProvider()
                await data_provider.initialize()
                
                try:
                    bars = await data_provider.get_historical_data(symbol, days=2, min_bars=2)
                finally:
                    await data_provider.shutdown()
                if not bars or len(bars) < 2:
                    continue
                    
                current_price = float(bars[-1].get('c', 0))
                prev_price = float(bars[-2].get('c', current_price))
                volume = int(bars[-1].get('v', 0))
                
                if current_price < SCREENING_CRITERIA['min_price'] or volume == 0:
                    continue
                    
                change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                
                # Filter based on direction and minimum movement - more lenient thresholds
                if direction == 'gainers' and change_pct > 0.2:  # Reduced from 0.5% to 0.2% gain
                    opportunity = MarketOpportunity(
                        symbol=symbol,
                        discovery_source=f'dynamic_{direction}',
                        discovery_timestamp=datetime.now(),
                        current_price=current_price,
                        daily_change_pct=change_pct,
                        volume=volume,
                        avg_volume=volume / 1.5,
                        volume_ratio=1.5,
                        market_cap=self._estimate_market_cap(symbol),
                        sector=self._get_sector_from_universe(symbol),
                    )
                    opportunities.append(opportunity)
                elif direction == 'losers' and change_pct < -0.2:  # Reduced from -0.5% to -0.2% loss
                    opportunity = MarketOpportunity(
                        symbol=symbol,
                        discovery_source=f'dynamic_{direction}',
                        discovery_timestamp=datetime.now(),
                        current_price=current_price,
                        daily_change_pct=change_pct,
                        volume=volume,
                        avg_volume=volume / 1.5,
                        volume_ratio=1.5,
                        market_cap=self._estimate_market_cap(symbol),
                        sector=self._get_sector_from_universe(symbol),
                    )
                    opportunities.append(opportunity)
                    
                symbols_tested += 1
                    
            except Exception as e:
                logger.debug(f"Failed to analyze {symbol} for dynamic {direction}: {e}")
                continue
        
        logger.info(f"🎯 Dynamic {direction}: tested {symbols_tested} symbols, found {len(opportunities)} opportunities")
        return opportunities
    
    async def _execute_comprehensive_market_scan(self) -> List[MarketOpportunity]:
        """
        Comprehensive market scan using unlimited Alpha Vantage keys
        Analyzes thousands of stocks for maximum opportunity discovery
        """
        if not self.asset_universe:
            logger.warning("No asset universe available for comprehensive scan")
            return []
            
        logger.info(f"🔍 COMPREHENSIVE SCAN: Analyzing large portion of {len(self.asset_universe)} stocks")
        
        # Filter to high-quality candidates
        quality_symbols = []
        for asset in self.asset_universe:
            symbol = asset['symbol']
            if (asset.get('exchange') in ['NYSE', 'NASDAQ', 'NYSEARCA'] and 
                len(symbol) <= 5 and symbol.isalpha() and
                not any(bad in symbol for bad in ['WARR', 'UNIT', 'RIGHT'])):
                quality_symbols.append(symbol)
        
        # Optimize sample size for real-time performance
        import random
        comprehensive_sample_size = min(1000, len(quality_symbols))  # Reduced to 1000 for faster execution
        test_symbols = random.sample(quality_symbols, comprehensive_sample_size)
        
        logger.info(f"🔄 Comprehensive scan: analyzing {len(test_symbols)} high-quality stocks")
        
        opportunities = []
        batch_size = 50  # Smaller batches for faster processing
        
        # Process batches in parallel for much faster execution
        import asyncio
        
        tasks = []
        for i in range(0, len(test_symbols), batch_size):
            batch = test_symbols[i:i + batch_size]
            task = self._analyze_symbol_batch_parallel(batch)
            tasks.append(task)
        
        # Execute all batches in parallel
        logger.info(f"🚀 Starting parallel analysis of {len(tasks)} batches...")
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for batch_result in batch_results:
            if isinstance(batch_result, list):
                opportunities.extend(batch_result)
            elif isinstance(batch_result, Exception):
                logger.warning(f"Batch analysis failed: {batch_result}")
        
        logger.info(f"⚡ Parallel analysis complete: {len(opportunities)} opportunities found")
        
        logger.info(f"🎯 COMPREHENSIVE SCAN COMPLETE: {len(opportunities)} total opportunities from {len(test_symbols)} stocks")
        return opportunities
    
    async def _analyze_symbol_batch_parallel(self, symbols: List[str]) -> List[MarketOpportunity]:
        """Analyze a batch of symbols with parallel data fetching for speed"""
        opportunities = []
        
        # Create one data provider for this batch to reuse connection
        from supplemental_data_provider import SupplementalDataProvider
        data_provider = SupplementalDataProvider()
        await data_provider.initialize()
        
        try:
            # Process symbols in parallel within the batch
            import asyncio
            
            # Create tasks for parallel data fetching
            tasks = []
            for symbol in symbols:
                task = self._analyze_single_symbol_fast(symbol, data_provider)
                tasks.append(task)
            
            # Execute all symbol analyses in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect successful results
            for result in results:
                if isinstance(result, MarketOpportunity):
                    opportunities.append(result)
                elif isinstance(result, Exception):
                    logger.debug(f"Symbol analysis failed: {result}")
                    
        finally:
            await data_provider.shutdown()
            
        return opportunities
    
    async def _analyze_single_symbol_fast(self, symbol: str, data_provider) -> Optional[MarketOpportunity]:
        """Fast analysis of a single symbol"""
        try:
            bars = await data_provider.get_historical_data(symbol, days=3, min_bars=2)
            if not bars or len(bars) < 2:
                return None
                
            current_price = float(bars[-1].get('c', 0))
            prev_price = float(bars[-2].get('c', current_price))
            volume = int(bars[-1].get('v', 0))
            
            # Skip if below minimum criteria
            if current_price < SCREENING_CRITERIA['min_price'] or volume < 100000:
                return None
            
            change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
            
            # Look for any significant movement or volume
            avg_volume = sum(int(bar.get('v', 0)) for bar in bars) / len(bars) if bars else volume
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
            
            # More inclusive criteria for comprehensive scan
            if (abs(change_pct) > 0.1 or volume_ratio > 1.2):  # 0.1% move OR 20% volume increase
                return MarketOpportunity(
                    symbol=symbol,
                    discovery_source='comprehensive_scan',
                    discovery_timestamp=datetime.now(),
                    current_price=current_price,
                    daily_change_pct=change_pct,
                    volume=volume,
                    avg_volume=avg_volume,
                    volume_ratio=volume_ratio,
                    market_cap=self._estimate_market_cap(symbol),
                    sector=self._get_sector_from_universe(symbol),
                )
            return None
            
        except Exception as e:
            logger.debug(f"Failed to analyze {symbol} in fast mode: {e}")
            return None
    
    async def _analyze_symbol_batch(self, symbols: List[str]) -> List[MarketOpportunity]:
        """Analyze a batch of symbols for opportunities"""
        opportunities = []
        
        for symbol in symbols:
            try:
                # Use supplemental data provider instead of Alpaca to avoid rate limits
                from supplemental_data_provider import SupplementalDataProvider
                
                data_provider = SupplementalDataProvider()
                await data_provider.initialize()
                
                try:
                    bars = await data_provider.get_historical_data(symbol, days=3, min_bars=2)
                finally:
                    await data_provider.shutdown()
                if not bars or len(bars) < 2:
                    continue
                    
                current_price = float(bars[-1].get('c', 0))
                prev_price = float(bars[-2].get('c', current_price))
                volume = int(bars[-1].get('v', 0))
                
                # Skip if below minimum criteria
                if current_price < SCREENING_CRITERIA['min_price'] or volume < 100000:
                    continue
                
                change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                
                # Look for any significant movement or volume
                avg_volume = sum(int(bar.get('v', 0)) for bar in bars) / len(bars) if bars else volume
                volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
                
                # More inclusive criteria for comprehensive scan
                if (abs(change_pct) > 0.1 or volume_ratio > 1.2):  # 0.1% move OR 20% volume increase
                    opportunity = MarketOpportunity(
                        symbol=symbol,
                        discovery_source='comprehensive_scan',
                        discovery_timestamp=datetime.now(),
                        current_price=current_price,
                        daily_change_pct=change_pct,
                        volume=volume,
                        avg_volume=avg_volume,
                        volume_ratio=volume_ratio,
                        market_cap=self._estimate_market_cap(symbol),
                        sector=self._get_sector_from_universe(symbol),
                    )
                    opportunities.append(opportunity)
                    
            except Exception as e:
                logger.debug(f"Failed to analyze {symbol} in comprehensive scan: {e}")
                continue
                
        return opportunities
    
    async def _get_dynamic_most_active(self) -> List[MarketOpportunity]:
        """Dynamic most active discovery using real volume data"""
        if not self.asset_universe:
            logger.warning("No asset universe available for dynamic active discovery")
            return []
            
        logger.info(f"🔍 Dynamic discovery: scanning for high volume from {len(self.asset_universe)} assets")
        
        # Sample from universe
        candidate_symbols = []
        for asset in self.asset_universe:
            symbol = asset['symbol']
            if (asset.get('exchange') in ['NYSE', 'NASDAQ', 'NYSEARCA'] and 
                len(symbol) <= 4):
                candidate_symbols.append(symbol)
        
        import random
        sample_size = min(75, len(candidate_symbols))  # Fast execution - focus on high-quality candidates
        test_symbols = random.sample(candidate_symbols, sample_size)
        
        volume_candidates = []
        
        for symbol in test_symbols:
            try:
                # Use supplemental data provider to avoid Alpaca rate limits
                from supplemental_data_provider import SupplementalDataProvider
                
                data_provider = SupplementalDataProvider()
                await data_provider.initialize()
                
                try:
                    bars = await data_provider.get_historical_data(symbol, days=5, min_bars=3)
                finally:
                    await data_provider.shutdown()
                if not bars or len(bars) < 3:
                    continue
                    
                current_volume = int(bars[-1].get('v', 0))
                avg_prev_volume = sum(int(bar.get('v', 0)) for bar in bars[-4:-1]) / 3
                
                if current_volume > 0 and avg_prev_volume > 0:
                    volume_ratio = current_volume / avg_prev_volume
                    if volume_ratio > 1.5:  # 50% above average volume
                        current_price = float(bars[-1].get('c', 0))
                        prev_price = float(bars[-2].get('c', current_price))
                        change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                        
                        if current_price >= SCREENING_CRITERIA['min_price']:
                            volume_candidates.append({
                                'symbol': symbol,
                                'volume': current_volume,
                                'volume_ratio': volume_ratio,
                                'price': current_price,
                                'change_pct': change_pct
                            })
                            
            except Exception as e:
                logger.debug(f"Failed to analyze volume for {symbol}: {e}")
                continue
        
        # Sort by volume ratio and take top candidates
        volume_candidates.sort(key=lambda x: x['volume_ratio'], reverse=True)
        
        opportunities = []
        for data in volume_candidates[:5]:  # Top 5 by volume
            opportunity = MarketOpportunity(
                symbol=data['symbol'],
                discovery_source='dynamic_volume',
                discovery_timestamp=datetime.now(),
                current_price=data['price'],
                daily_change_pct=data['change_pct'],
                volume=data['volume'],
                avg_volume=data['volume'] / data['volume_ratio'],
                volume_ratio=data['volume_ratio'],
                market_cap=self._estimate_market_cap(data['symbol']),
                sector=self._get_sector_from_universe(data['symbol']),
            )
            opportunities.append(opportunity)
        
        logger.info(f"🎯 Dynamic volume: found {len(opportunities)} high-volume opportunities")
        return opportunities
            
    async def _get_simulated_market_movers(self, direction: str) -> List[MarketOpportunity]:
        """Fallback simulated market movers using dynamic asset universe and recent data"""
        # Use dynamic asset universe instead of hardcoded symbols
        if not self.asset_universe:
            logger.warning("No asset universe available for simulation")
            return []
            
        # Sample from asset universe - focus on liquid, well-known symbols
        candidate_symbols = []
        for asset in self.asset_universe:
            symbol = asset['symbol']
            # Prefer major exchanges and avoid penny stocks
            if (asset.get('exchange') in ['NYSE', 'NASDAQ'] and 
                len(symbol) <= 4 and symbol.isalpha()):
                candidate_symbols.append(symbol)
        
        # Sample up to 20 symbols for testing
        import random
        test_symbols = random.sample(candidate_symbols, min(20, len(candidate_symbols)))
        
        movers_data = []
        symbols_processed = 0
        target_count = 3
        
        for symbol in test_symbols:
            if symbols_processed >= target_count:
                break
                
            try:
                # Get latest quote for current price
                quote = await self.gateway.get_latest_quote(symbol)
                if not quote:
                    continue
                    
                # Get recent bars for change calculation
                bars = await self.gateway.get_bars(symbol, '1Day', limit=2)
                if not bars or len(bars) < 2:
                    continue
                    
                current_price = float(quote.get('ask_price', 0)) or float(quote.get('bid_price', 0))
                if current_price <= 0:
                    continue
                    
                # Calculate change from previous day
                prev_close = float(bars[-2].get('c', 0))
                if prev_close <= 0:
                    continue
                    
                change_pct = ((current_price - prev_close) / prev_close) * 100
                volume = int(bars[-1].get('v', 0))
                
                # Filter by direction
                if direction == 'gainers' and change_pct > 2.0:
                    movers_data.append({
                        'symbol': symbol,
                        'price': current_price,
                        'change_pct': change_pct,
                        'volume': volume
                    })
                    symbols_processed += 1
                elif direction == 'losers' and change_pct < -2.0:
                    movers_data.append({
                        'symbol': symbol,
                        'price': current_price,
                        'change_pct': change_pct,
                        'volume': volume
                    })
                    symbols_processed += 1
                    
            except Exception as e:
                logger.debug(f"Failed to get data for {symbol}: {e}")
                continue
                
        # If no real data available, use minimal fallback
        if not movers_data:
            logger.warning("No real market data available, using minimal fallback")
            return []
            
        opportunities = []
        for data in movers_data:
            opportunity = MarketOpportunity(
                symbol=data['symbol'],
                discovery_source=f'market_{direction}',
                discovery_timestamp=datetime.now(),
                current_price=data['price'],
                daily_change_pct=data['change_pct'],
                volume=data['volume'],
                avg_volume=data['volume'] / 1.5,
                volume_ratio=1.5,
                market_cap=self._estimate_market_cap(data['symbol']),
                sector=self._get_sector(data['symbol']),
            )
            opportunities.append(opportunity)
            
        return opportunities
            
    async def _get_most_active_stocks(self) -> List[MarketOpportunity]:
        """Get most active stocks by volume"""
        try:
            # Use real Alpaca most active API
            active_data = await self.gateway.get_most_active_stocks(limit=25)
            
            opportunities = []
            for data in active_data:
                # Parse real Alpaca API response
                symbol = data.get('symbol', '')
                price = float(data.get('price', 0)) if data.get('price') else 0
                change_pct = float(data.get('change_percent', 0)) if data.get('change_percent') else 0
                volume = int(data.get('volume', 0)) if data.get('volume') else 0
                
                if symbol and price > SCREENING_CRITERIA['min_price']:
                    opportunity = MarketOpportunity(
                        symbol=symbol,
                        discovery_source='most_active',
                        discovery_timestamp=datetime.now(),
                        current_price=price,
                        daily_change_pct=change_pct,
                        volume=volume,
                        avg_volume=volume / 2.0,  # Estimate from volume
                        volume_ratio=2.0,
                        market_cap=self._estimate_market_cap(symbol),
                        sector=self._get_sector(symbol),
                    )
                    opportunities.append(opportunity)
                    
            # Fallback to dynamic discovery if API returns no data
            if not opportunities:
                logger.info("No live most active data, using dynamic discovery")
                return await self._get_dynamic_most_active()
                
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to get most active stocks: {e}")
            # Fallback to dynamic discovery
            return await self._get_dynamic_most_active()
            
    async def _get_news_driven_movers(self) -> List[MarketOpportunity]:
        """Detect news-driven market movements"""
        try:
            # Get recent news and identify symbols with significant movement
            news_data = await self.gateway.get_news(limit=20)
            
            opportunities = []
            processed_symbols = set()
            
            for news_item in news_data:
                # Extract symbols from news
                symbols = news_item.get('symbols', [])
                headline = news_item.get('headline', '')
                
                for symbol in symbols[:2]:  # Process first 2 symbols per news item
                    if symbol in processed_symbols:
                        continue
                    
                    # Skip crypto and forex symbols - comprehensive filtering
                    crypto_patterns = ['USD', 'BTC', 'ETH', 'USDT', 'EUR', 'GBP', 'JPY', 'CRYPTO', 'COIN']
                    if any(crypto in symbol.upper() for crypto in crypto_patterns):
                        logger.debug(f"🚫 Filtered crypto/forex symbol: {symbol}")
                        continue
                        
                    # Skip invalid or problematic symbols
                    invalid_symbols = ['NDTAF', 'BRK.A', 'BRK.B']  # Common invalid/problematic symbols
                    invalid_patterns = ['.A', '.B', 'TEST', 'TEMP']
                    if (symbol in invalid_symbols or 
                        any(pattern in symbol for pattern in invalid_patterns) or
                        len(symbol) > 5 or len(symbol) < 1):
                        logger.debug(f"🚫 Filtered invalid symbol: {symbol}")
                        continue
                        
                    # Skip if symbol ends with USD (common crypto pattern)
                    if symbol.upper().endswith('USD'):
                        logger.debug(f"🚫 Filtered USD-ending symbol: {symbol}")
                        continue
                        
                    # Skip if symbol is too long (likely crypto pair)
                    if len(symbol) > 5:
                        logger.debug(f"🚫 Filtered long symbol: {symbol}")
                        continue
                        
                    processed_symbols.add(symbol)
                    
                    # Get current price data for the symbol
                    quote = await self.gateway.get_latest_quote(symbol)
                    if not quote:
                        continue
                        
                    # Estimate price and volume from available data
                    current_price = float(quote.get('ask_price', 0)) or float(quote.get('bid_price', 0))
                    if current_price < SCREENING_CRITERIA['min_price']:
                        continue
                        
                    # Determine catalyst from headline keywords
                    catalyst = self._extract_catalyst_from_headline(headline)
                    
                    opportunity = MarketOpportunity(
                        symbol=symbol,
                        discovery_source='news_movers',
                        discovery_timestamp=datetime.now(),
                        current_price=current_price,
                        daily_change_pct=0.0,  # Would need historical data to calculate
                        volume=0,  # Would need volume data
                        avg_volume=1000000,  # Estimate
                        volume_ratio=3.0,  # Higher ratio for news-driven
                        market_cap=self._estimate_market_cap(symbol),
                        sector=self._get_sector(symbol),
                        primary_catalyst=catalyst
                    )
                    opportunities.append(opportunity)
                    
                    if len(opportunities) >= 10:  # Limit to top 10
                        break
                        
            # Fallback to simulated data if no news-driven opportunities found
            if not opportunities:
                logger.info("No news-driven opportunities, using simulated data")
                return await self._get_simulated_news_movers()
                
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to get news-driven movers: {e}")
            # Fallback to simulated data
            return await self._get_simulated_news_movers()
            
    async def _detect_unusual_volume(self) -> List[MarketOpportunity]:
        """Detect unusual volume patterns using real market data"""
        try:
            # Get a diverse set of symbols to check for unusual volume
            check_symbols = ['SPY', 'QQQ', 'IWM', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'AMD', 
                           'META', 'NFLX', 'CRM', 'ROKU', 'ZM', 'SNAP', 'TWTR', 'UBER', 'LYFT', 'SQ']
            
            volume_data = []
            
            for symbol in check_symbols:
                try:
                    # Get recent bars to calculate average volume
                    bars = await self.gateway.get_bars(symbol, '1Day', limit=10)
                    if not bars or len(bars) < 5:
                        continue
                        
                    # Calculate average volume from last 5-9 days (excluding today)
                    historical_volumes = [int(bar.get('v', 0)) for bar in bars[:-1]]
                    if not historical_volumes or all(v == 0 for v in historical_volumes):
                        continue
                        
                    avg_volume = sum(historical_volumes) / len(historical_volumes)
                    current_volume = int(bars[-1].get('v', 0))
                    
                    if avg_volume == 0 or current_volume == 0:
                        continue
                        
                    volume_ratio = current_volume / avg_volume
                    
                    # Look for volume spikes (3x+ normal volume)
                    if volume_ratio >= 3.0:
                        current_price = float(bars[-1].get('c', 0))
                        prev_close = float(bars[-2].get('c', current_price)) if len(bars) >= 2 else current_price
                        change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
                        
                        if current_price >= SCREENING_CRITERIA['min_price']:
                            volume_data.append({
                                'symbol': symbol,
                                'price': current_price,
                                'change_pct': change_pct,
                                'volume': current_volume,
                                'volume_ratio': volume_ratio
                            })
                            
                    if len(volume_data) >= 5:  # Limit results
                        break
                        
                except Exception as e:
                    logger.debug(f"Volume analysis failed for {symbol}: {e}")
                    continue
                    
            if not volume_data:
                logger.info("No unusual volume patterns detected")
                return []
            
            opportunities = []
            for data in volume_data:
                opportunity = MarketOpportunity(
                    symbol=data['symbol'],
                    discovery_source='unusual_volume',
                    discovery_timestamp=datetime.now(),
                    current_price=data['price'],
                    daily_change_pct=data['change_pct'],
                    volume=data['volume'],
                    avg_volume=data['volume'] / data['volume_ratio'],
                    volume_ratio=data['volume_ratio'],
                    market_cap=self._estimate_market_cap(data['symbol']),
                    sector=self._get_sector(data['symbol']),
                )
                opportunities.append(opportunity)
                
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to detect unusual volume: {e}")
            return []
            
    async def _get_simulated_most_active(self) -> List[MarketOpportunity]:
        """Fallback simulated most active stocks using dynamic asset universe"""
        if not self.asset_universe:
            logger.warning("No asset universe available for most active simulation")
            return []
            
        # Sample high-liquidity symbols from universe
        candidate_symbols = []
        for asset in self.asset_universe:
            symbol = asset['symbol']
            # Focus on major exchanges, ETFs, and well-known stocks
            if (asset.get('exchange') in ['NYSE', 'NASDAQ', 'NYSEARCA'] and 
                len(symbol) <= 4):
                candidate_symbols.append(symbol)
        
        # Sample for testing
        import random
        test_symbols = random.sample(candidate_symbols, min(8, len(candidate_symbols)))
        
        active_data = []
        
        for symbol in test_symbols[:5]:  # Top 5
            try:
                # Get latest quote and recent bar data
                quote = await self.gateway.get_latest_quote(symbol)
                bars = await self.gateway.get_bars(symbol, '1Day', limit=2)
                
                if not quote or not bars:
                    continue
                    
                current_price = float(quote.get('ask_price', 0)) or float(quote.get('bid_price', 0))
                if current_price <= 0:
                    continue
                    
                latest_bar = bars[-1]
                volume = int(latest_bar.get('v', 0))
                prev_close = float(bars[-2].get('c', current_price)) if len(bars) >= 2 else current_price
                
                change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
                
                if volume > 0:  # Only include if we have volume data
                    active_data.append({
                        'symbol': symbol,
                        'price': current_price,
                        'volume': volume,
                        'change_pct': change_pct
                    })
                    
            except Exception as e:
                logger.debug(f"Failed to get active data for {symbol}: {e}")
                continue
                
        # If no real data, return empty (don't create fake data)
        if not active_data:
            logger.warning("No real active stock data available")
            return []
        
        opportunities = []
        for data in active_data:
            opportunity = MarketOpportunity(
                symbol=data['symbol'],
                discovery_source='most_active',
                discovery_timestamp=datetime.now(),
                current_price=data['price'],
                daily_change_pct=data['change_pct'],
                volume=data['volume'],
                avg_volume=data['volume'] / 2.0,
                volume_ratio=2.0,
                market_cap=self._estimate_market_cap(data['symbol']),
                sector=self._get_sector(data['symbol']),
            )
            opportunities.append(opportunity)
            
        return opportunities
        
    async def _get_simulated_news_movers(self) -> List[MarketOpportunity]:
        """Fallback news-driven movers using recent news and market data"""
        try:
            # Get recent news to find symbols with catalysts
            news_data = await self.gateway.get_news(limit=10)
            
            news_movers_data = []
            processed_symbols = set()
            
            for news_item in news_data:
                symbols = news_item.get('symbols', [])
                headline = news_item.get('headline', '')
                
                for symbol in symbols[:1]:  # One symbol per news item
                    if symbol in processed_symbols or len(news_movers_data) >= 3:
                        continue
                    
                    # Log all symbols being processed
                    logger.debug(f"Processing news symbol: {symbol}")
                        
                    # Skip crypto and forex symbols - comprehensive filtering
                    crypto_patterns = ['USD', 'BTC', 'ETH', 'USDT', 'EUR', 'GBP', 'JPY', 'CRYPTO', 'COIN']
                    if any(crypto in symbol.upper() for crypto in crypto_patterns):
                        logger.info(f"🚫 Filtered crypto/forex symbol: {symbol}")
                        continue
                        
                    # Skip invalid or problematic symbols
                    invalid_symbols = ['NDTAF', 'BRK.A', 'BRK.B']  # Common invalid/problematic symbols
                    invalid_patterns = ['.A', '.B', 'TEST', 'TEMP']
                    if (symbol in invalid_symbols or 
                        any(pattern in symbol for pattern in invalid_patterns) or
                        len(symbol) > 5 or len(symbol) < 1):
                        logger.info(f"🚫 Filtered invalid symbol: {symbol}")
                        continue
                        
                    # Skip if symbol ends with USD (common crypto pattern)
                    if symbol.upper().endswith('USD'):
                        logger.info(f"🚫 Filtered USD-ending symbol: {symbol}")
                        continue
                        
                    processed_symbols.add(symbol)
                    
                    # Get current market data for this symbol
                    quote = await self.gateway.get_latest_quote(symbol)
                    bars = await self.gateway.get_bars(symbol, '1Day', limit=2)
                    
                    if not quote or not bars:
                        continue
                        
                    current_price = float(quote.get('ask_price', 0)) or float(quote.get('bid_price', 0))
                    if current_price <= 0:
                        continue
                        
                    volume = int(bars[-1].get('v', 0)) if bars else 0
                    prev_close = float(bars[-2].get('c', current_price)) if len(bars) >= 2 else current_price
                    change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
                    
                    catalyst = self._extract_catalyst_from_headline(headline)
                    
                    news_movers_data.append({
                        'symbol': symbol,
                        'price': current_price,
                        'change_pct': change_pct,
                        'volume': volume,
                        'catalyst': catalyst
                    })
                    
            if not news_movers_data:
                logger.warning("No news-driven opportunities found")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get news movers: {e}")
            return []
        
        opportunities = []
        for data in news_movers_data:
            opportunity = MarketOpportunity(
                symbol=data['symbol'],
                discovery_source='news_movers',
                discovery_timestamp=datetime.now(),
                current_price=data['price'],
                daily_change_pct=data['change_pct'],
                volume=data['volume'],
                avg_volume=data['volume'] / 3.0,
                volume_ratio=3.0,
                market_cap=self._estimate_market_cap(data['symbol']),
                sector=self._get_sector(data['symbol']),
                primary_catalyst=data['catalyst']
            )
            opportunities.append(opportunity)
            
        return opportunities
        
    def _extract_catalyst_from_headline(self, headline: str) -> str:
        """Extract trading catalyst from news headline"""
        headline_lower = headline.lower()
        
        # Common catalysts
        if any(word in headline_lower for word in ['earnings', 'beat', 'miss', 'guidance']):
            return 'earnings'
        elif any(word in headline_lower for word in ['acquisition', 'merger', 'buyout']):
            return 'M&A activity'
        elif any(word in headline_lower for word in ['breakthrough', 'innovation', 'patent']):
            return 'innovation'
        elif any(word in headline_lower for word in ['upgrade', 'downgrade', 'rating']):
            return 'analyst action'
        elif any(word in headline_lower for word in ['fda', 'approval', 'clinical']):
            return 'regulatory'
        else:
            return 'general news'
            
    def _deduplicate_candidates(self, candidates: List[MarketOpportunity]) -> List[MarketOpportunity]:
        """Remove duplicate symbols, keeping best discovery source"""
        seen_symbols = {}
        
        # Priority order for discovery sources
        source_priority = {
            'market_gainers': 1,
            'unusual_volume': 2,
            'news_movers': 3,
            'most_active': 4,
            'market_losers': 5
        }
        
        for candidate in candidates:
            symbol = candidate.symbol
            current_priority = source_priority.get(candidate.discovery_source, 10)
            
            if (symbol not in seen_symbols or 
                current_priority < source_priority.get(seen_symbols[symbol].discovery_source, 10)):
                seen_symbols[symbol] = candidate
                
        return list(seen_symbols.values())
        
    def _apply_basic_filters(self, candidates: List[MarketOpportunity]) -> List[MarketOpportunity]:
        """Apply basic screening criteria"""
        filtered = []
        
        for candidate in candidates:
            # Price filters
            if (candidate.current_price < SCREENING_CRITERIA['min_price'] or
                candidate.current_price > SCREENING_CRITERIA['max_price']):
                continue
                
            # Volume filter
            if candidate.avg_volume < SCREENING_CRITERIA['min_avg_volume']:
                continue
                
            # Market cap filter
            if candidate.market_cap < SCREENING_CRITERIA['min_market_cap']:
                continue
                
            filtered.append(candidate)
            
        return filtered
        
    async def _get_market_regime_analysis(self) -> Dict:
        """Get AI analysis of current market regime"""
        
        # Get market indicators
        market_data = await self._collect_market_indicators()
        
        prompt = f"""
        ROLE: Senior market strategist analyzing market regime
        TASK: Determine current market environment for optimal trading strategy
        
        MARKET INDICATORS:
        - VIX Level: {market_data.get('vix', 'N/A')}
        - SPY vs 20-day MA: {market_data.get('spy_trend', 'N/A')}
        - Volume Profile: {market_data.get('volume_profile', 'N/A')}
        - Sector Rotation: {market_data.get('sector_rotation', 'N/A')}
        - Options Flow: {market_data.get('options_flow', 'N/A')}
        
        DETERMINE MARKET REGIME:
        1. bull_trending: Strong uptrend, low volatility, momentum strategies optimal
        2. bear_trending: Downtrend, defensive positioning, oversold bounces
        3. volatile_range: High volatility, range-bound, mean reversion optimal
        4. sector_rotation: Leadership changing, relative strength important
        5. low_volatility: Compression, breakout strategies optimal
        
        RETURN JSON:
        {{
            "regime": "bull_trending",
            "confidence": 0.85,
            "volatility_environment": "normal",
            "primary_strategy": "momentum",
            "optimal_timeframe": "3-7 days",
            "risk_appetite": "moderate",
            "sector_preference": ["TECHNOLOGY", "FINANCIALS"],
            "avoid_sectors": ["UTILITIES"],
            "reasoning": "Strong uptrend with normal volatility supports momentum plays..."
        }}
        """
        
        try:
            if hasattr(self.ai_assistant, '_query_ollama'):
                response = await self.ai_assistant._query_ollama(prompt)
                return self.ai_assistant._parse_json_response(response)
            else:
                # Fallback market regime detection
                return {
                    "regime": "bull_trending",
                    "confidence": 0.5,
                    "primary_strategy": "momentum"
                }
        except Exception as e:
            logger.error(f"Market regime analysis failed: {e}")
            return {
                "regime": "bull_trending",
                "confidence": 0.5,
                "primary_strategy": "momentum"
            }
            
    async def _collect_market_indicators(self) -> Dict:
        """Collect current market indicators from real market data"""
        try:
            indicators = {}
            
            # Get SPY data for market trend analysis
            spy_bars = await self.gateway.get_bars('SPY', '1Day', limit=21)  # 21 days for MA20
            if spy_bars and len(spy_bars) >= 20:
                current_price = float(spy_bars[-1].get('c', 0))
                prices = [float(bar.get('c', 0)) for bar in spy_bars[-20:]]
                ma_20 = sum(prices) / len(prices) if prices else current_price
                
                indicators['spy_price'] = current_price
                indicators['spy_ma20'] = ma_20
                indicators['spy_trend'] = 'above_ma' if current_price > ma_20 else 'below_ma'
            else:
                indicators['spy_trend'] = 'unknown'
                
            # Try to get VIX data (may not be available in all Alpaca tiers)
            try:
                vix_quote = await self.gateway.get_latest_quote('VIX')
                if vix_quote:
                    vix_price = float(vix_quote.get('ask_price', 0)) or float(vix_quote.get('bid_price', 0))
                    indicators['vix'] = vix_price if vix_price > 0 else None
            except:
                indicators['vix'] = None
                
            # Analyze volume profile from major ETFs
            volume_data = []
            for etf in ['SPY', 'QQQ', 'IWM']:
                try:
                    bars = await self.gateway.get_bars(etf, '1Day', limit=5)
                    if bars:
                        recent_volumes = [int(bar.get('v', 0)) for bar in bars]
                        if recent_volumes:
                            avg_volume = sum(recent_volumes) / len(recent_volumes)
                            volume_data.append(avg_volume)
                except:
                    continue
                    
            if volume_data:
                total_avg_volume = sum(volume_data) / len(volume_data)
                indicators['volume_profile'] = 'high' if total_avg_volume > 50000000 else 'normal'
            else:
                indicators['volume_profile'] = 'unknown'
                
            # Simple sector analysis by comparing tech vs overall market
            try:
                qqq_bars = await self.gateway.get_bars('QQQ', '1Day', limit=2)
                if qqq_bars and len(qqq_bars) >= 2:
                    qqq_change = ((float(qqq_bars[-1].get('c', 0)) - float(qqq_bars[-2].get('c', 0))) / 
                                 float(qqq_bars[-2].get('c', 1))) * 100
                    spy_change = 0
                    if spy_bars and len(spy_bars) >= 2:
                        spy_change = ((float(spy_bars[-1].get('c', 0)) - float(spy_bars[-2].get('c', 0))) / 
                                     float(spy_bars[-2].get('c', 1))) * 100
                    
                    indicators['sector_rotation'] = 'tech_leading' if qqq_change > spy_change else 'broad_market'
            except:
                indicators['sector_rotation'] = 'unknown'
                
            indicators['options_flow'] = 'unknown'  # Would need options data
            
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to collect market indicators: {e}")
            return {
                'vix': None,
                'spy_trend': 'unknown',
                'volume_profile': 'unknown',
                'sector_rotation': 'unknown',
                'options_flow': 'unknown'
            }
        
    def _meets_regime_criteria(self, candidate: MarketOpportunity, regime_criteria: Dict) -> bool:
        """Check if candidate meets market regime criteria"""
        try:
            # Focus criteria - use dynamic thresholds from config
            focus = regime_criteria.get('focus_on', 'all')
            min_daily_change = regime_criteria.get('min_daily_change', 0.0)
            
            if focus == 'gainers' and candidate.daily_change_pct < min_daily_change:
                return False
            elif focus == 'oversold_bounces' and candidate.daily_change_pct > min_daily_change:
                return False
                
            # Volume ratio check
            min_volume_ratio = regime_criteria.get('min_volume_ratio', 1.0)
            if candidate.volume_ratio < min_volume_ratio:
                return False
                
            # Sector preference
            preferred_sectors = regime_criteria.get('preferred_sectors', [])
            avoid_sectors = regime_criteria.get('avoid_sectors', [])
            
            if preferred_sectors and 'ALL' not in preferred_sectors:
                if candidate.sector not in preferred_sectors:
                    return False
                    
            if candidate.sector in avoid_sectors:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Regime criteria check failed: {e}")
            return True
            
    def _calculate_preliminary_score(self, candidate: MarketOpportunity, 
                                   market_context: Dict, regime_criteria: Dict) -> float:
        """Calculate preliminary opportunity score"""
        try:
            score = 0.0
            
            # Volume score (0-0.3)
            volume_score = min(0.3, candidate.volume_ratio * 0.1)
            score += volume_score
            
            # Price movement score (0-0.3)
            abs_change = abs(candidate.daily_change_pct)
            movement_score = min(0.3, abs_change * 0.03)
            score += movement_score
            
            # Market cap score (0-0.2)
            if candidate.market_cap > 10e9:  # >$10B
                score += 0.2
            elif candidate.market_cap > 1e9:  # >$1B
                score += 0.15
            else:
                score += 0.1
                
            # Discovery source score (0-0.2)
            source_scores = {
                'market_gainers': 0.2,
                'news_movers': 0.18,
                'unusual_volume': 0.15,
                'most_active': 0.12,
                'market_losers': 0.1
            }
            score += source_scores.get(candidate.discovery_source, 0.1)
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Preliminary scoring failed: {e}")
            return 0.5
            
    async def _get_detailed_technicals(self, symbol: str) -> Optional[Dict]:
        """Get detailed technical analysis data"""
        try:
            # Simulate technical data retrieval
            return {
                'rsi': np.random.uniform(30, 70),
                'ma_10': np.random.uniform(100, 200),
                'ma_20': np.random.uniform(95, 195),
                'ma_50': np.random.uniform(90, 190),
                'atr': np.random.uniform(2, 8)
            }
        except Exception as e:
            logger.error(f"Technical analysis failed for {symbol}: {e}")
            return None
            
    async def _get_news_analysis(self, symbol: str) -> Optional[Dict]:
        """Get news analysis for symbol"""
        try:
            # Simulate news analysis
            sentiments = ['POSITIVE', 'NEGATIVE', 'NEUTRAL']
            return {
                'sentiment': np.random.choice(sentiments),
                'news_count': np.random.randint(0, 5),
                'catalyst_strength': np.random.uniform(0.3, 0.9)
            }
        except Exception as e:
            logger.error(f"News analysis failed for {symbol}: {e}")
            return None
            
    def _update_candidate_technicals(self, candidate: MarketOpportunity, technical_data: Dict) -> MarketOpportunity:
        """Update candidate with technical data"""
        candidate.rsi = technical_data.get('rsi')
        candidate.ma_10 = technical_data.get('ma_10')
        candidate.ma_20 = technical_data.get('ma_20')
        candidate.ma_50 = technical_data.get('ma_50')
        candidate.atr = technical_data.get('atr')
        return candidate
        
    def _update_candidate_news(self, candidate: MarketOpportunity, news_data: Dict) -> MarketOpportunity:
        """Update candidate with news data"""
        candidate.news_sentiment = news_data.get('sentiment', 'NEUTRAL')
        if news_data.get('catalyst_strength', 0) > 0.7:
            candidate.primary_catalyst = f"High-impact news ({candidate.news_sentiment})"
        return candidate
        
    async def _calculate_final_ai_score(self, candidate: MarketOpportunity) -> float:
        """Calculate final AI-powered opportunity score"""
        try:
            # Enhance preliminary score with technical and news factors
            base_score = candidate.opportunity_score
            
            # Technical enhancement
            technical_boost = 0.0
            if candidate.rsi and 30 <= candidate.rsi <= 70:  # Good RSI range
                technical_boost += 0.1
            if candidate.ma_10 and candidate.ma_20 and candidate.ma_10 > candidate.ma_20:  # Uptrend
                technical_boost += 0.1
                
            # News sentiment enhancement
            news_boost = 0.0
            if candidate.news_sentiment == 'POSITIVE':
                news_boost += 0.15
            elif candidate.news_sentiment == 'NEGATIVE':
                news_boost -= 0.1
                
            # Volume confirmation
            volume_boost = min(0.1, (candidate.volume_ratio - 1.0) * 0.05)
            
            final_score = base_score + technical_boost + news_boost + volume_boost
            candidate.confidence = min(0.95, final_score + 0.1)
            
            return min(1.0, final_score)
            
        except Exception as e:
            logger.error(f"Final AI scoring failed: {e}")
            return candidate.opportunity_score
            
    async def _update_dynamic_watchlist(self, opportunities: List[MarketOpportunity]):
        """Update dynamic watchlist with pruning and additions"""
        try:
            current_time = datetime.now()
            
            # Prune existing watchlist
            symbols_to_remove = []
            for symbol, opportunity in self.current_watchlist.items():
                if self._should_prune_opportunity(opportunity, current_time):
                    symbols_to_remove.append(symbol)
                    
            for symbol in symbols_to_remove:
                del self.current_watchlist[symbol]
                logger.debug(f"Pruned {symbol} from watchlist")
                
            # Add new high-conviction opportunities
            added_count = 0
            for opportunity in opportunities:
                if (len(self.current_watchlist) < WATCHLIST_CONFIG['max_size'] and
                    opportunity.symbol not in self.current_watchlist and
                    opportunity.opportunity_score >= WATCHLIST_CONFIG['addition_criteria']['min_opportunity_score']):
                    
                    opportunity.watchlist_entry_time = current_time
                    self.current_watchlist[opportunity.symbol] = opportunity
                    added_count += 1
                    
            logger.info(f"📝 Watchlist updated: -{len(symbols_to_remove)} +{added_count} "
                       f"= {len(self.current_watchlist)} total")
                       
        except Exception as e:
            logger.error(f"Watchlist update failed: {e}")
            
    def _should_prune_opportunity(self, opportunity: MarketOpportunity, current_time: datetime) -> bool:
        """Determine if opportunity should be pruned from watchlist"""
        
        # Age-based pruning - more aggressive
        if opportunity.watchlist_entry_time:
            age_hours = (current_time - opportunity.watchlist_entry_time).total_seconds() / 3600
            if age_hours > WATCHLIST_CONFIG['pruning_criteria']['max_age_hours']:
                return True
        
        # Force refresh after 30 minutes if we have many opportunities
        if len(self.current_watchlist) > 15 and opportunity.watchlist_entry_time:
            age_minutes = (current_time - opportunity.watchlist_entry_time).total_seconds() / 60
            if age_minutes > 30:  # Remove older ones when watchlist is getting full
                return True
                
        # Score-based pruning
        if opportunity.opportunity_score < 0.4:
            return True
            
        # Volume decline pruning
        if (opportunity.volume_ratio < 
            WATCHLIST_CONFIG['pruning_criteria']['volume_decline_threshold']):
            return True
            
        return False
        
    # Helper methods for dynamic data lookups
    def _estimate_market_cap(self, symbol: str) -> float:
        """Estimate market cap based on symbol characteristics and price"""
        try:
            # ETF market caps are not applicable - return 0
            if symbol in ['SPY', 'QQQ', 'IWM', 'XLF', 'XLK', 'XLE', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLB', 'XLRE']:
                return 0
                
            # For stocks, estimate based on typical market cap ranges by symbol characteristics
            # Large cap tech (typically >$500B)
            large_cap_tech = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN']
            if symbol in large_cap_tech:
                return 2000000000000  # $2T estimate
                
            # Major tech stocks (typically $100B-$1T)
            major_tech = ['NVDA', 'META', 'TSLA', 'NFLX', 'CRM', 'ADBE', 'ORCL', 'INTC', 'AMD', 'QCOM']
            if symbol in major_tech:
                return 500000000000  # $500B estimate
                
            # Mid-cap stocks (typically $10B-$100B)
            mid_cap_indicators = len(symbol) <= 4 and not any(char.isdigit() for char in symbol)
            if mid_cap_indicators:
                return 50000000000  # $50B estimate
                
            # Small-cap default
            return 10000000000  # $10B estimate
            
        except Exception as e:
            logger.debug(f"Market cap estimation failed for {symbol}: {e}")
            return 25000000000  # Default $25B
        
    def _get_sector_from_universe(self, symbol: str) -> str:
        """Get sector from asset universe data"""
        for asset in self.asset_universe:
            if asset['symbol'] == symbol:
                # Use exchange as a proxy for sector classification
                exchange = asset.get('exchange', '')
                if exchange == 'NYSEARCA':
                    return 'EQUITY'  # ETFs
                elif 'name' in asset:
                    name = asset['name'].upper()
                    if any(tech in name for tech in ['TECH', 'SOFTWARE', 'COMPUTER', 'DATA']):
                        return 'TECHNOLOGY'
                    elif any(health in name for health in ['HEALTH', 'PHARMA', 'BIO', 'MEDICAL']):
                        return 'HEALTHCARE'
                    elif any(fin in name for fin in ['BANK', 'FINANCIAL', 'INSURANCE']):
                        return 'FINANCIAL'
                    else:
                        return 'EQUITY'
                return 'EQUITY'
        return 'UNKNOWN'
    
    def _get_sector(self, symbol: str) -> str:
        """Get sector classification based on symbol characteristics"""
        try:
            # ETFs
            if symbol in ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO']:
                return 'ETF'
            
            # Sector ETFs
            sector_etfs = {
                'XLK': 'TECHNOLOGY_ETF',
                'XLF': 'FINANCIALS_ETF', 
                'XLE': 'ENERGY_ETF',
                'XLV': 'HEALTHCARE_ETF',
                'XLI': 'INDUSTRIALS_ETF',
                'XLP': 'CONSUMER_STAPLES_ETF',
                'XLY': 'CONSUMER_DISCRETIONARY_ETF',
                'XLU': 'UTILITIES_ETF',
                'XLB': 'MATERIALS_ETF',
                'XLRE': 'REAL_ESTATE_ETF'
            }
            if symbol in sector_etfs:
                return sector_etfs[symbol]
                
            # Major technology companies
            tech_companies = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'AMD', 'INTC', 
                            'CRM', 'ORCL', 'ADBE', 'NFLX', 'ROKU', 'ZM', 'SNAP', 'TWTR', 'SQ', 'PYPL']
            if symbol in tech_companies:
                return 'TECHNOLOGY'
                
            # Automotive/EV
            auto_companies = ['TSLA', 'F', 'GM', 'NIO', 'XPEV', 'LI', 'RIVN', 'LCID']
            if symbol in auto_companies:
                return 'AUTOMOTIVE'
                
            # Financial services
            financial_companies = ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'AXP', 'BRK.A', 'BRK.B']
            if symbol in financial_companies:
                return 'FINANCIALS'
                
            # Healthcare/Biotech
            healthcare_companies = ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'ABT', 'MRK', 'LLY', 'GILD', 'AMGN']
            if symbol in healthcare_companies:
                return 'HEALTHCARE'
                
            # Energy
            energy_companies = ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'VLO', 'PSX']
            if symbol in energy_companies:
                return 'ENERGY'
                
            # Default classification based on symbol patterns
            if len(symbol) <= 4 and symbol.isalpha():
                return 'EQUITY'  # Generic equity
            
            return 'OTHER'
            
        except Exception as e:
            logger.debug(f"Sector classification failed for {symbol}: {e}")
            return 'UNKNOWN'
        
    async def get_current_opportunities(self) -> List[MarketOpportunity]:
        """Get current watchlist opportunities sorted by score"""
        opportunities = list(self.current_watchlist.values())
        opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)
        return opportunities
        
    async def get_funnel_statistics(self) -> Dict:
        """Get comprehensive funnel performance statistics"""
        return {
            'scan_statistics': self.scan_statistics,
            'current_watchlist_size': len(self.current_watchlist),
            'market_regime': self.market_regime.value,
            'api_budget_remaining': {
                category: self.rate_limiter.get_remaining_budget(category)
                for category in RATE_LIMIT_CONFIG['budget_allocation'].keys()
            },
            'last_scan_time': self.last_broad_scan.isoformat() if self.last_broad_scan else None
        }