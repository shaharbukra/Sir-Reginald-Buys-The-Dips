"""
Tiered Analysis System: Ensures no high-potential stocks are missed
Multi-tier approach: Fast Screening → Priority Analysis → Deep Dive
Handles rate limits, data issues, and ensures comprehensive coverage
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
from enum import Enum
from config import *

logger = logging.getLogger(__name__)

class AnalysisTier(Enum):
    FAST_SCREEN = 1      # Basic price/volume analysis (no external API calls)
    PRIORITY_ANALYSIS = 2 # Enhanced analysis with some data calls
    DEEP_DIVE = 3        # Full technical + AI analysis

@dataclass
class AnalysisResult:
    """Result from tiered analysis"""
    symbol: str
    tier_completed: AnalysisTier
    signal_strength: float  # 0.0 to 1.0
    confidence: float      # 0.0 to 1.0
    recommendation: str    # BUY, SELL, HOLD, NONE
    reasoning: str
    data_quality: str      # EXCELLENT, GOOD, LIMITED, POOR
    needs_deeper_analysis: bool = False
    priority_score: float = 0.0

@dataclass
class StockData:
    """Consolidated stock data from all sources"""
    symbol: str
    # Price data
    current_price: float = 0.0
    prev_close: float = 0.0
    daily_change_pct: float = 0.0
    
    # Volume data
    volume: int = 0
    avg_volume: float = 0.0
    volume_ratio: float = 1.0
    
    # Price history (last N bars)
    price_history: List[float] = field(default_factory=list)
    volume_history: List[int] = field(default_factory=list)
    
    # Technical indicators (if available)
    rsi: Optional[float] = None
    ma_10: Optional[float] = None
    ma_20: Optional[float] = None
    atr: Optional[float] = None
    
    # Data quality metrics
    data_age_minutes: int = 0
    data_sources: List[str] = field(default_factory=list)
    bars_available: int = 0

class TieredAnalyzer:
    """
    Robust tiered analysis system that ensures no good stocks are missed
    """
    
    def __init__(self, api_gateway, supplemental_data_provider, strategy):
        self.api_gateway = api_gateway
        self.supplemental_data_provider = supplemental_data_provider
        self.strategy = strategy
        
        # Analysis queues by priority
        self.high_priority_queue = deque()    # Market movers, news events
        self.medium_priority_queue = deque()  # Volume spikes, breakouts
        self.low_priority_queue = deque()     # General scanning
        
        # Results cache
        self.analysis_cache = {}
        self.cache_expiry = {}
        
        # Statistics
        self.stats = {
            'fast_screen_count': 0,
            'priority_analysis_count': 0,
            'deep_dive_count': 0,
            'rate_limited_count': 0,
            'data_issues_count': 0,
            'signals_generated': 0
        }
    
    async def analyze_stock_list(self, symbols: List[str], priority_level: str = "MEDIUM") -> List[AnalysisResult]:
        """
        Analyze a list of stocks with tiered approach
        Ensures comprehensive coverage regardless of data/rate limit issues
        """
        logger.info(f"🔍 Starting tiered analysis of {len(symbols)} stocks (priority: {priority_level})")
        
        results = []
        
        # Step 1: Fast screening of ALL stocks (no external API calls)
        fast_screen_results = await self._fast_screen_all(symbols)
        logger.info(f"📊 Fast screening completed: {len(fast_screen_results)} results")
        
        # Step 2: Prioritize based on fast screening
        prioritized_stocks = self._prioritize_stocks(fast_screen_results, priority_level)
        logger.info(f"🎯 Prioritized {len(prioritized_stocks)} stocks for deeper analysis")
        
        # Step 3: Progressive deeper analysis
        for tier in [AnalysisTier.PRIORITY_ANALYSIS, AnalysisTier.DEEP_DIVE]:
            enhanced_results = await self._analyze_tier(prioritized_stocks, tier)
            results.extend(enhanced_results)
            
            # Update prioritization based on new results
            prioritized_stocks = self._update_priorities(prioritized_stocks, enhanced_results)
        
        # Step 4: Ensure no high-potential stocks were missed
        missed_opportunities = self._identify_missed_opportunities(results, symbols)
        if missed_opportunities:
            logger.warning(f"🚨 Analyzing {len(missed_opportunities)} potentially missed opportunities")
            recovery_results = await self._emergency_analysis(missed_opportunities)
            results.extend(recovery_results)
        
        logger.info(f"✅ Tiered analysis complete: {len(results)} final results")
        self._log_analysis_stats()
        
        return results
    
    async def _fast_screen_all(self, symbols: List[str]) -> List[AnalysisResult]:
        """
        Tier 1: Fast screening using minimal data (no external API calls)
        Uses only data we already have or can get instantly
        """
        results = []
        
        for symbol in symbols:
            try:
                # Check cache first
                if self._is_cached_and_fresh(symbol, AnalysisTier.FAST_SCREEN):
                    results.append(self.analysis_cache[symbol])
                    continue
                
                # Fast analysis using basic heuristics
                result = await self._fast_screen_single(symbol)
                if result:
                    results.append(result)
                    self._cache_result(symbol, result, AnalysisTier.FAST_SCREEN)
                
                self.stats['fast_screen_count'] += 1
                
            except Exception as e:
                logger.debug(f"Fast screening failed for {symbol}: {e}")
                continue
        
        return results
    
    async def _fast_screen_single(self, symbol: str) -> Optional[AnalysisResult]:
        """
        Basic screening using symbol characteristics and minimal data
        """
        try:
            # Basic symbol filtering
            if len(symbol) > 5 or '.' in symbol or '-' in symbol:
                return None  # Skip complex symbols
            
            # Try to get minimal quote data (fast)
            quote_data = None
            try:
                quote_data = await self.supplemental_data_provider.get_current_quote_fast(symbol)
            except:
                pass
            
            if not quote_data or not quote_data.get('current_price'):
                # No data available - try alternative quote sources
                try:
                    # Try alternative quote from Alpaca
                    alpaca_quote = await self.api_gateway.get_latest_quote(symbol)
                    if alpaca_quote:
                        current_price = float(alpaca_quote.get('ask_price', 0)) or float(alpaca_quote.get('bid_price', 0))
                        if current_price > 0:
                            quote_data = {
                                'current_price': current_price,
                                'daily_change_pct': 0,  # Unknown
                                'volume': 0,  # Unknown
                                'source': 'alpaca_quote'
                            }
                except:
                    pass
                
                if not quote_data or not quote_data.get('current_price'):
                    # Still no data available - but don't reject completely
                    return AnalysisResult(
                        symbol=symbol,
                        tier_completed=AnalysisTier.FAST_SCREEN,
                        signal_strength=0.3,  # Neutral
                        confidence=0.2,       # Low confidence without data
                        recommendation="NONE",
                        reasoning="No quote data available - needs deeper analysis",
                        data_quality="POOR", 
                        needs_deeper_analysis=True,
                        priority_score=0.4    # Medium priority for data recovery
                    )
            
            current_price = float(quote_data['current_price'])
            
            # Basic price filters
            if current_price < 5.0 or current_price > 500.0:
                return None
            
            # Calculate basic metrics
            daily_change = quote_data.get('daily_change_pct', 0)
            volume = quote_data.get('volume', 0)
            
            # Fast scoring based on available data
            signal_strength = 0.5  # Neutral base
            priority_score = 0.5
            
            # Price momentum signals
            if abs(daily_change) > 3.0:
                signal_strength += 0.2
                priority_score += 0.3
            elif abs(daily_change) > 1.5:
                signal_strength += 0.1
                priority_score += 0.2
            
            # Volume signals (if available)
            if volume > 1000000:  # High volume
                signal_strength += 0.1
                priority_score += 0.2
            
            # Determine recommendation
            if daily_change > 2.0 and signal_strength > 0.6:
                recommendation = "BUY"
                needs_deeper = True
            elif daily_change < -2.0 and signal_strength > 0.6:
                recommendation = "SELL"
                needs_deeper = True
            else:
                recommendation = "NONE"
                needs_deeper = signal_strength > 0.6
            
            return AnalysisResult(
                symbol=symbol,
                tier_completed=AnalysisTier.FAST_SCREEN,
                signal_strength=min(1.0, signal_strength),
                confidence=0.6,  # Moderate confidence from fast screening
                recommendation=recommendation,
                reasoning=f"Fast screen: {daily_change:+.1f}% daily change, volume {volume:,}",
                data_quality="LIMITED",
                needs_deeper_analysis=needs_deeper,
                priority_score=min(1.0, priority_score)
            )
            
        except Exception as e:
            logger.debug(f"Fast screening error for {symbol}: {e}")
            return None
    
    def _prioritize_stocks(self, fast_results: List[AnalysisResult], priority_level: str) -> List[str]:
        """
        Prioritize stocks for deeper analysis based on fast screening results
        """
        # Sort by priority score and signal strength
        sorted_results = sorted(
            fast_results,
            key=lambda x: (x.priority_score, x.signal_strength, x.needs_deeper_analysis),
            reverse=True
        )
        
        # Determine how many to analyze deeper based on priority level
        if priority_level == "HIGH":
            max_deep_analysis = min(200, len(sorted_results))
        elif priority_level == "MEDIUM":
            max_deep_analysis = min(100, len(sorted_results))
        else:  # LOW
            max_deep_analysis = min(50, len(sorted_results))
        
        # Always include stocks that need deeper analysis
        priority_symbols = []
        
        # High priority: Strong signals or needs deeper analysis
        for result in sorted_results:
            if (result.needs_deeper_analysis or 
                result.signal_strength > 0.7 or 
                result.priority_score > 0.7):
                priority_symbols.append(result.symbol)
            
            if len(priority_symbols) >= max_deep_analysis:
                break
        
        logger.info(f"🎯 Selected {len(priority_symbols)} stocks for deeper analysis from {len(fast_results)} screened")
        return priority_symbols
    
    async def _analyze_tier(self, symbols: List[str], tier: AnalysisTier) -> List[AnalysisResult]:
        """
        Analyze stocks at specific tier level
        """
        results = []
        
        if tier == AnalysisTier.PRIORITY_ANALYSIS:
            results = await self._priority_analysis_batch(symbols)
        elif tier == AnalysisTier.DEEP_DIVE:
            results = await self._deep_dive_analysis_batch(symbols)
        
        return results
    
    async def _priority_analysis_batch(self, symbols: List[str]) -> List[AnalysisResult]:
        """
        Tier 2: Priority analysis with some data fetching
        More thorough than fast screening but not full deep dive
        """
        results = []
        
        # Process in batches to manage rate limits
        batch_size = 20
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_results = await self._priority_analysis_single_batch(batch)
            results.extend(batch_results)
            
            # Small delay between batches
            await asyncio.sleep(0.5)
        
        return results
    
    async def _priority_analysis_single_batch(self, symbols: List[str]) -> List[AnalysisResult]:
        """
        Analyze a single batch with priority analysis
        """
        results = []
        
        # Create tasks for parallel processing
        tasks = []
        for symbol in symbols:
            task = self._priority_analyze_single(symbol)
            tasks.append(task)
        
        # Execute with timeout and error handling
        try:
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for symbol, result in zip(symbols, batch_results):
                if isinstance(result, Exception):
                    logger.debug(f"Priority analysis failed for {symbol}: {result}")
                    # Create fallback result
                    fallback_result = AnalysisResult(
                        symbol=symbol,
                        tier_completed=AnalysisTier.PRIORITY_ANALYSIS,
                        signal_strength=0.4,
                        confidence=0.3,
                        recommendation="NONE",
                        reasoning="Analysis failed - data or rate limit issues",
                        data_quality="POOR",
                        needs_deeper_analysis=True,
                        priority_score=0.6  # Higher priority due to failure
                    )
                    results.append(fallback_result)
                elif result:
                    results.append(result)
                    
        except Exception as e:
            logger.error(f"Batch priority analysis failed: {e}")
        
        return results
    
    async def _priority_analyze_single(self, symbol: str) -> Optional[AnalysisResult]:
        """
        Priority analysis for single stock with enhanced data
        """
        try:
            # Check cache
            if self._is_cached_and_fresh(symbol, AnalysisTier.PRIORITY_ANALYSIS):
                return self.analysis_cache[symbol]
            
            # Get enhanced data with fallback options
            stock_data = await self._get_enhanced_stock_data(symbol)
            
            if not stock_data or stock_data.current_price <= 0:
                return None
            
            # Enhanced analysis
            result = self._analyze_enhanced_data(symbol, stock_data)
            
            if result:
                self._cache_result(symbol, result, AnalysisTier.PRIORITY_ANALYSIS)
                self.stats['priority_analysis_count'] += 1
            
            return result
            
        except Exception as e:
            logger.debug(f"Priority analysis failed for {symbol}: {e}")
            return None
    
    async def _get_enhanced_stock_data(self, symbol: str) -> Optional[StockData]:
        """
        Get enhanced stock data with multiple fallback options
        """
        stock_data = StockData(symbol=symbol)
        
        # Try quote data first (fast)
        try:
            quote = await self.supplemental_data_provider.get_current_quote_fast(symbol)
            if quote:
                stock_data.current_price = float(quote.get('current_price', 0))
                stock_data.volume = int(quote.get('volume', 0))
                stock_data.daily_change_pct = float(quote.get('daily_change_pct', 0))
                stock_data.data_sources.append('quote')
        except:
            pass
        
        # Try to get some historical data (limited) with multiple fallbacks
        try:
            # Try Yahoo Finance first
            bars = await self.supplemental_data_provider.get_historical_data(symbol, days=2, min_bars=2)
            if bars and len(bars) >= 2:
                stock_data.bars_available = len(bars)
                
                # Extract price history
                stock_data.price_history = [float(bar['c']) for bar in bars]
                stock_data.volume_history = [int(bar['v']) for bar in bars]
                
                # Update current price if not from quote
                if stock_data.current_price <= 0 and stock_data.price_history:
                    stock_data.current_price = stock_data.price_history[-1]
                
                # Calculate volume ratio
                if len(stock_data.volume_history) > 1:
                    recent_vol = stock_data.volume_history[-1]
                    avg_vol = sum(stock_data.volume_history[:-1]) / len(stock_data.volume_history[:-1])
                    stock_data.volume_ratio = recent_vol / avg_vol if avg_vol > 0 else 1.0
                
                stock_data.data_sources.append('historical')
            else:
                # Fallback: Try to get ANY bars from Alpaca
                try:
                    alpaca_bars = await self.api_gateway.get_bars(symbol, '1Hour', limit=10)
                    if alpaca_bars and len(alpaca_bars) >= 2:
                        stock_data.bars_available = len(alpaca_bars)
                        stock_data.price_history = [float(bar.get('c', bar.get('close', 0))) for bar in alpaca_bars]
                        stock_data.volume_history = [int(bar.get('v', bar.get('volume', 0))) for bar in alpaca_bars]
                        
                        if stock_data.current_price <= 0 and stock_data.price_history:
                            stock_data.current_price = stock_data.price_history[-1]
                        
                        stock_data.data_sources.append('alpaca_hourly')
                except:
                    pass
        except:
            pass
        
        # Calculate data quality
        if stock_data.current_price <= 0:
            return None
        
        return stock_data
    
    def _analyze_enhanced_data(self, symbol: str, stock_data: StockData) -> Optional[AnalysisResult]:
        """
        Analyze enhanced stock data
        """
        try:
            signal_strength = 0.5
            confidence = 0.5
            reasoning_parts = []
            
            # Price analysis
            if stock_data.daily_change_pct > 3.0:
                signal_strength += 0.2
                reasoning_parts.append(f"+{stock_data.daily_change_pct:.1f}% strong momentum")
            elif stock_data.daily_change_pct > 1.5:
                signal_strength += 0.1
                reasoning_parts.append(f"+{stock_data.daily_change_pct:.1f}% momentum")
            elif stock_data.daily_change_pct < -3.0:
                signal_strength += 0.15  # Potential oversold bounce
                reasoning_parts.append(f"{stock_data.daily_change_pct:.1f}% oversold")
            
            # Volume analysis
            if stock_data.volume_ratio > 2.0:
                signal_strength += 0.15
                confidence += 0.1
                reasoning_parts.append(f"{stock_data.volume_ratio:.1f}x volume")
            elif stock_data.volume_ratio > 1.5:
                signal_strength += 0.1
                reasoning_parts.append(f"{stock_data.volume_ratio:.1f}x volume")
            
            # Price history analysis
            if len(stock_data.price_history) >= 3:
                recent_trend = 0
                for i in range(1, min(4, len(stock_data.price_history))):
                    if stock_data.price_history[-i] > stock_data.price_history[-i-1]:
                        recent_trend += 1
                
                if recent_trend >= 2:
                    signal_strength += 0.1
                    reasoning_parts.append("uptrend")
                confidence += 0.1  # More data = more confidence
            
            # Data quality adjustment
            data_quality = "GOOD" if len(stock_data.data_sources) > 1 else "LIMITED"
            if data_quality == "LIMITED":
                confidence *= 0.8
            
            # Determine recommendation
            if signal_strength > 0.75 and stock_data.daily_change_pct > 1.0:
                recommendation = "BUY"
                needs_deeper = True
            elif signal_strength > 0.7 and stock_data.daily_change_pct < -2.0:
                recommendation = "SELL"  
                needs_deeper = True
            else:
                recommendation = "NONE"
                needs_deeper = signal_strength > 0.65
            
            reasoning = f"Enhanced: {', '.join(reasoning_parts) if reasoning_parts else 'neutral signals'}"
            
            return AnalysisResult(
                symbol=symbol,
                tier_completed=AnalysisTier.PRIORITY_ANALYSIS,
                signal_strength=min(1.0, signal_strength),
                confidence=min(1.0, confidence),
                recommendation=recommendation,
                reasoning=reasoning,
                data_quality=data_quality,
                needs_deeper_analysis=needs_deeper,
                priority_score=signal_strength
            )
            
        except Exception as e:
            logger.debug(f"Enhanced data analysis failed for {symbol}: {e}")
            return None
    
    async def _deep_dive_analysis_batch(self, symbols: List[str]) -> List[AnalysisResult]:
        """
        Tier 3: Full deep dive analysis for highest priority stocks
        """
        results = []
        
        # Only analyze top candidates for deep dive
        max_deep_dive = min(50, len(symbols))
        top_symbols = symbols[:max_deep_dive]
        
        logger.info(f"🔬 Starting deep dive analysis for {len(top_symbols)} stocks")
        
        for symbol in top_symbols:
            try:
                result = await self._deep_dive_single(symbol)
                if result:
                    results.append(result)
                    self.stats['deep_dive_count'] += 1
                
                # Rate limiting
                await asyncio.sleep(0.2)
                
            except Exception as e:
                logger.debug(f"Deep dive failed for {symbol}: {e}")
                continue
        
        return results
        
    async def _deep_dive_single(self, symbol: str) -> Optional[AnalysisResult]:
        """
        Full deep dive analysis using existing strategy system
        """
        try:
            # Check cache
            if self._is_cached_and_fresh(symbol, AnalysisTier.DEEP_DIVE):
                return self.analysis_cache[symbol]
            
            # Get comprehensive data
            bars = await self.supplemental_data_provider.get_historical_data(symbol, days=5, min_bars=5)
            quote_data = await self.supplemental_data_provider.get_current_quote_fast(symbol)
            
            if not bars or len(bars) < 5:
                return None
            
            # Use existing strategy system for full analysis
            trading_signal = await self.strategy.analyze_symbol(
                symbol=symbol,
                bars=bars,
                quote_data=quote_data,
                data_sources=['enhanced']
            )
            
            if trading_signal:
                self.stats['signals_generated'] += 1
                
                result = AnalysisResult(
                    symbol=symbol,
                    tier_completed=AnalysisTier.DEEP_DIVE,
                    signal_strength=trading_signal.confidence,
                    confidence=trading_signal.confidence,
                    recommendation=trading_signal.action,
                    reasoning=f"Deep dive: {trading_signal.reasoning}",
                    data_quality="EXCELLENT",
                    needs_deeper_analysis=False,
                    priority_score=trading_signal.confidence
                )
                
                self._cache_result(symbol, result, AnalysisTier.DEEP_DIVE)
                return result
            
            return None
            
        except Exception as e:
            logger.debug(f"Deep dive analysis failed for {symbol}: {e}")
            return None
    
    def _update_priorities(self, symbols: List[str], new_results: List[AnalysisResult]) -> List[str]:
        """
        Update priority list based on analysis results
        """
        # Create result map
        result_map = {r.symbol: r for r in new_results}
        
        # Re-sort based on updated priorities
        updated_priorities = []
        for symbol in symbols:
            if symbol in result_map:
                result = result_map[symbol]
                if result.needs_deeper_analysis or result.signal_strength > 0.7:
                    updated_priorities.append(symbol)
        
        return updated_priorities
    
    def _identify_missed_opportunities(self, results: List[AnalysisResult], original_symbols: List[str]) -> List[str]:
        """
        Identify potentially missed high-value opportunities
        """
        analyzed_symbols = {r.symbol for r in results}
        missed_symbols = []
        
        for symbol in original_symbols:
            if symbol not in analyzed_symbols:
                # This symbol was completely missed - add to recovery list
                missed_symbols.append(symbol)
        
        # Prioritize missed symbols that might have been high-value
        # (This is a safety net for rate limit failures)
        return missed_symbols[:20]  # Limit recovery attempts
    
    async def _emergency_analysis(self, symbols: List[str]) -> List[AnalysisResult]:
        """
        Emergency analysis for potentially missed opportunities
        Uses most basic analysis to ensure nothing is completely ignored
        """
        logger.info(f"🚨 Emergency analysis for {len(symbols)} missed stocks")
        results = []
        
        for symbol in symbols:
            try:
                # Very basic analysis
                result = await self._fast_screen_single(symbol)
                if result:
                    result.reasoning = f"Emergency recovery: {result.reasoning}"
                    result.priority_score += 0.1  # Slight boost for recovery
                    results.append(result)
                    
            except Exception as e:
                logger.debug(f"Emergency analysis failed for {symbol}: {e}")
                continue
        
        return results
    
    def _is_cached_and_fresh(self, symbol: str, tier: AnalysisTier) -> bool:
        """Check if cached result is still fresh"""
        if symbol not in self.analysis_cache:
            return False
        
        cached_result = self.analysis_cache[symbol]
        if cached_result.tier_completed.value < tier.value:
            return False  # Need higher tier analysis
        
        # Check expiry
        if symbol in self.cache_expiry:
            if datetime.now() > self.cache_expiry[symbol]:
                return False
        
        return True
    
    def _cache_result(self, symbol: str, result: AnalysisResult, tier: AnalysisTier):
        """Cache analysis result"""
        self.analysis_cache[symbol] = result
        
        # Set expiry based on tier
        if tier == AnalysisTier.FAST_SCREEN:
            expiry_minutes = 5
        elif tier == AnalysisTier.PRIORITY_ANALYSIS:
            expiry_minutes = 15
        else:  # DEEP_DIVE
            expiry_minutes = 30
            
        self.cache_expiry[symbol] = datetime.now() + timedelta(minutes=expiry_minutes)
    
    def _log_analysis_stats(self):
        """Log analysis statistics"""
        logger.info("📊 Tiered Analysis Statistics:")
        logger.info(f"   - Fast screens: {self.stats['fast_screen_count']}")
        logger.info(f"   - Priority analyses: {self.stats['priority_analysis_count']}")
        logger.info(f"   - Deep dives: {self.stats['deep_dive_count']}")
        logger.info(f"   - Signals generated: {self.stats['signals_generated']}")
        logger.info(f"   - Rate limited: {self.stats['rate_limited_count']}")
        logger.info(f"   - Data issues: {self.stats['data_issues_count']}")
    
    def get_analysis_summary(self) -> Dict:
        """Get summary of analysis performance"""
        return {
            'statistics': self.stats.copy(),
            'cache_size': len(self.analysis_cache),
            'queue_sizes': {
                'high_priority': len(self.high_priority_queue),
                'medium_priority': len(self.medium_priority_queue),
                'low_priority': len(self.low_priority_queue)
            }
        }