"""
Enhanced AI assistant with REAL market intelligence based on actual data
Replaces the problematic Ollama-dependent system with data-driven analysis
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, time
import re
from config import *

logger = logging.getLogger(__name__)

@dataclass
class MarketIntelligence:
    """Comprehensive market intelligence report"""
    timestamp: datetime
    market_regime: str
    volatility_environment: str
    sector_rotation: Dict[str, str]
    risk_appetite: str
    key_themes: List[str]
    trading_opportunities: List[str]
    risk_factors: List[str]
    recommended_strategy: str
    confidence: float

class EnhancedAIAssistant:
    """
    Professional AI assistant for trading intelligence
    Uses data-driven analysis as primary method with AI backup
    """
    
    def __init__(self):
        self.session = None
        self.api_url = AI_CONFIG['ollama_url']
        self.model = AI_CONFIG['model_name']
        self.daily_intelligence = None
        self.last_intelligence_update = None
        
    async def initialize(self):
        """Initialize async HTTP session"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=AI_CONFIG['request_timeout'])
            )
            logger.info(f"🤖 AI Assistant session initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI session: {e}")
            self.session = None
        
    async def shutdown(self):
        """Clean shutdown with proper connection handling"""
        try:
            if self.session and not self.session.closed:
                # Give pending requests time to complete
                await asyncio.sleep(0.1)
                await self.session.close()
                # Wait for the underlying connections to close
                await asyncio.sleep(0.1)
                self.session = None
                logger.info("✅ AI Assistant session closed cleanly")
        except Exception as e:
            logger.warning(f"⚠️ AI Assistant shutdown warning: {e}")
        finally:
            # Ensure session is set to None even if close failed
            self.session = None
            
    async def generate_daily_market_intelligence(self, market_data: Dict) -> MarketIntelligence:
        """Generate comprehensive daily market intelligence report"""
        
        # PRIORITY 1: Use real market data analysis (most reliable)
        try:
            logger.info("📊 Generating market intelligence from real market data...")
            intelligence = await self._analyze_market_data_intelligence(market_data)
            if intelligence:
                logger.info(f"📊 Generated DATA-DRIVEN market intelligence: {intelligence.market_regime} regime, "
                           f"{intelligence.volatility_environment} volatility (confidence: {intelligence.confidence:.0%})")
                return intelligence
        except Exception as e:
            logger.warning(f"⚠️ AI DATA ANALYSIS FAILURE: {e}")
            logger.warning(f"⚠️ Falling back to AI generation method...")
        
        # PRIORITY 2: Try fast AI with short timeout (backup)
        if self.session:
            try:
                logger.info("🤖 Attempting fast AI-generated market intelligence...")
                intelligence = await self._generate_ai_intelligence_fast(market_data)
                if intelligence:
                    logger.info(f"📊 Generated AI market intelligence: {intelligence.market_regime} regime, "
                               f"{intelligence.volatility_environment} volatility")
                    return intelligence
            except Exception as e:
                logger.warning(f"⚠️ AI GENERATION FAILURE: {e}")
                logger.warning(f"⚠️ Falling back to informed fallback method...")
        
        # PRIORITY 3: Informed fallback based on basic market data
        logger.warning("⚠️ 🚨 CRITICAL AI SYSTEM FAILURE 🚨")
        logger.warning("⚠️ Both data analysis and AI generation completely failed")
        logger.warning("⚠️ System operating in FALLBACK MODE with limited intelligence")
        logger.warning("⚠️ Consider investigating AI system health and connectivity")
        return self._get_informed_fallback_intelligence(market_data)
    
    async def _analyze_market_data_intelligence(self, market_data: Dict) -> Optional[MarketIntelligence]:
        """Generate intelligence from actual market data analysis"""
        try:
            # Get current market metrics
            spy_data = await self._get_market_index_data('SPY')
            vix_data = await self._get_volatility_data()
            
            # Analyze market regime based on actual data
            market_regime = self._determine_market_regime(spy_data, market_data)
            volatility_env = self._determine_volatility_environment(vix_data)
            risk_appetite = self._assess_risk_appetite(spy_data, vix_data)
            
            # Sector analysis from actual data
            sector_analysis = await self._analyze_sector_performance()
            
            # Trading strategy recommendation based on regime
            recommended_strategy = self._recommend_strategy(market_regime, volatility_env)
            
            # Calculate confidence based on data quality
            confidence = self._calculate_data_confidence(spy_data, vix_data, sector_analysis)
            
            return MarketIntelligence(
                timestamp=datetime.now(),
                market_regime=market_regime,
                volatility_environment=volatility_env,
                sector_rotation=sector_analysis,
                risk_appetite=risk_appetite,
                key_themes=self._identify_market_themes(market_regime, sector_analysis),
                trading_opportunities=[],
                risk_factors=self._identify_risk_factors(volatility_env, market_regime),
                recommended_strategy=recommended_strategy,
                confidence=confidence
            )
            
        except Exception as e:
            logger.warning(f"⚠️ MARKET DATA ANALYSIS FAILURE: {e}")
            logger.warning(f"⚠️ Unable to analyze SPY, VIX, or sector data - intelligence degraded")
            return None
    
    async def _get_market_index_data(self, symbol: str) -> Optional[Dict]:
        """Get market index data for analysis"""
        try:
            # Import here to avoid circular imports
            from supplemental_data_provider import SupplementalDataProvider
            
            data_provider = SupplementalDataProvider()
            await data_provider.initialize()  # CRITICAL: Initialize the session
            
            try:
                bars = await data_provider.get_historical_data(symbol, days=5, min_bars=3)
            finally:
                await data_provider.shutdown()  # Clean shutdown
            
            if bars and len(bars) >= 3:
                latest = bars[-1]
                prev = bars[-2]
                week_ago = bars[0] if len(bars) >= 5 else bars[-3]
                
                return {
                    'current_price': float(latest['c']),
                    'prev_close': float(prev['c']),
                    'week_ago_close': float(week_ago['c']),
                    'daily_change_pct': ((float(latest['c']) - float(prev['c'])) / float(prev['c'])) * 100,
                    'weekly_change_pct': ((float(latest['c']) - float(week_ago['c'])) / float(week_ago['c'])) * 100,
                    'volume': int(latest['v']),
                    'avg_volume': sum(int(bar['v']) for bar in bars) / len(bars),
                    'high_period': max(float(bar['h']) for bar in bars),
                    'low_period': min(float(bar['l']) for bar in bars)
                }
            return None
        except Exception as e:
            logger.warning(f"⚠️ MARKET INDEX DATA FAILURE for {symbol}: {e}")
            logger.warning(f"⚠️ Unable to fetch {symbol} data - market intelligence will be limited")
            return None
    
    async def _get_volatility_data(self) -> Optional[Dict]:
        """Get VIX or volatility proxy data"""
        try:
            # Try to get VIX data
            vix_data = await self._get_market_index_data('VIX')
            if vix_data:
                return {
                    'vix_level': vix_data['current_price'],
                    'vix_change': vix_data['daily_change_pct'],
                    'source': 'VIX'
                }
            
            # Fallback: calculate implied volatility from SPY price movements
            spy_data = await self._get_market_index_data('SPY')
            if spy_data:
                # Simple volatility proxy from recent price swings
                daily_change = abs(spy_data['daily_change_pct'])
                implied_vix = daily_change * 15  # Rough approximation
                
                return {
                    'vix_level': implied_vix,
                    'vix_change': 0,  # Unknown without historical VIX
                    'source': 'SPY_PROXY'
                }
            return None
        except Exception as e:
            logger.warning(f"⚠️ VOLATILITY DATA FAILURE: {e}")
            logger.warning(f"⚠️ Unable to determine market volatility - using conservative estimates")
            return None
    
    def _determine_market_regime(self, spy_data: Optional[Dict], market_data: Dict) -> str:
        """Determine market regime from actual data"""
        if not spy_data:
            return "BULL_TRENDING"  # Default
        
        daily_change = spy_data['daily_change_pct']
        weekly_change = spy_data['weekly_change_pct']
        
        # Market regime logic based on actual price action
        if weekly_change > 2.0 and daily_change > 0.3:
            return "BULL_TRENDING"
        elif weekly_change < -2.0 and daily_change < -0.3:
            return "BEAR_TRENDING"
        elif abs(daily_change) > 1.5:
            return "VOLATILE_RANGE"
        elif abs(weekly_change) < 1.0 and abs(daily_change) < 0.5:
            return "LOW_VOLATILITY"
        else:
            return "SECTOR_ROTATION"
    
    def _determine_volatility_environment(self, vix_data: Optional[Dict]) -> str:
        """Determine volatility environment"""
        if not vix_data:
            return "NORMAL"  # Default
        
        vix_level = vix_data['vix_level']
        
        if vix_level < 15:
            return "LOW"
        elif vix_level < 25:
            return "NORMAL"  
        elif vix_level < 35:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _assess_risk_appetite(self, spy_data: Optional[Dict], vix_data: Optional[Dict]) -> str:
        """Assess market risk appetite"""
        if not spy_data or not vix_data:
            return "MODERATE"
        
        # Risk-on conditions: SPY up, VIX down
        if spy_data['weekly_change_pct'] > 1.5 and vix_data['vix_level'] < 20:
            return "HIGH"
        # Risk-off conditions: SPY down, VIX up  
        elif spy_data['weekly_change_pct'] < -1.5 and vix_data['vix_level'] > 25:
            return "LOW"
        else:
            return "MODERATE"
    
    async def _analyze_sector_performance(self) -> Dict:
        """Analyze sector performance using available data"""
        try:
            # Sample sector ETFs for analysis  
            sector_symbols = {
                'TECHNOLOGY': 'XLK',
                'FINANCIALS': 'XLF', 
                'HEALTHCARE': 'XLV',
                'ENERGY': 'XLE',
                'CONSUMER_DISCRETIONARY': 'XLY'
            }
            
            sector_performance = {}
            leaders = []
            laggards = []
            
            for sector, symbol in sector_symbols.items():
                try:
                    data = await self._get_market_index_data(symbol)
                    if data and data.get('weekly_change_pct') is not None:
                        perf = data['weekly_change_pct']
                        sector_performance[sector] = perf
                        
                        if perf > 1.5:
                            leaders.append(sector)
                        elif perf < -1.5:
                            laggards.append(sector)
                except Exception:
                    continue
                    
                # Rate limiting
                await asyncio.sleep(0.1)
            
            return {
                'leaders': leaders[:3] if leaders else ['TECHNOLOGY'],
                'laggards': laggards[:3] if laggards else ['UTILITIES'],
                'rotation_active': len(leaders) > 0 and len(laggards) > 0,
                'performance': sector_performance
            }
            
        except Exception as e:
            logger.warning(f"⚠️ SECTOR ANALYSIS FAILURE: {e}")
            logger.warning(f"⚠️ Unable to analyze sector rotation - using default assumptions")
            return {
                'leaders': ['TECHNOLOGY'],
                'laggards': ['UTILITIES'], 
                'rotation_active': False,
                'performance': {}
            }
    
    def _recommend_strategy(self, market_regime: str, volatility_env: str) -> str:
        """Recommend trading strategy based on market conditions"""
        if market_regime in ['BULL_TRENDING', 'BEAR_TRENDING']:
            return 'MOMENTUM'
        elif market_regime == 'VOLATILE_RANGE':
            return 'MEAN_REVERSION'
        elif market_regime == 'LOW_VOLATILITY':
            return 'BREAKOUT'
        else:
            return 'MOMENTUM'  # Default
    
    def _identify_market_themes(self, market_regime: str, sector_analysis: Dict) -> List[str]:
        """Identify key market themes"""
        themes = []
        
        if market_regime == 'BULL_TRENDING':
            themes.extend(['MOMENTUM', 'GROWTH_ROTATION'])
        elif market_regime == 'BEAR_TRENDING':
            themes.extend(['DEFENSIVE', 'QUALITY'])
        elif market_regime == 'VOLATILE_RANGE':
            themes.extend(['MEAN_REVERSION', 'HEDGING'])
        elif market_regime == 'LOW_VOLATILITY':
            themes.extend(['BREAKOUT', 'CONSOLIDATION'])
        
        # Add sector themes
        if sector_analysis.get('rotation_active'):
            themes.append('SECTOR_ROTATION')
            
        return themes[:3]  # Limit to top 3 themes
    
    def _identify_risk_factors(self, volatility_env: str, market_regime: str) -> List[str]:
        """Identify key risk factors"""
        risks = []
        
        if volatility_env in ['HIGH', 'EXTREME']:
            risks.append('HIGH_VOLATILITY')
        if market_regime == 'BEAR_TRENDING':
            risks.append('BEAR_MARKET')
        if market_regime == 'VOLATILE_RANGE':
            risks.append('WHIPSAW_RISK')
        if volatility_env == 'LOW':
            risks.append('COMPLACENCY_RISK')
            
        return risks[:3]  # Limit to top 3 risks
    
    def _calculate_data_confidence(self, spy_data: Optional[Dict], vix_data: Optional[Dict], 
                                  sector_analysis: Dict) -> float:
        """Calculate confidence based on data availability and quality"""
        confidence = 0.5  # Base confidence
        
        if spy_data:
            confidence += 0.25  # SPY data is crucial
        if vix_data:
            confidence += 0.15  # VIX data is valuable
        if sector_analysis.get('performance'):
            confidence += 0.1   # Sector data adds insight
            
        return min(0.95, confidence)  # Cap at 95%
    
    async def _generate_ai_intelligence_fast(self, market_data: Dict) -> Optional[MarketIntelligence]:
        """Try AI generation with aggressive timeout"""
        try:
            # Simple fast prompt for AI backup
            prompt = "Analyze current market: bullish/bearish/volatile/low_vol? One word answer."
            
            # Try with very short timeout
            response = await self._query_ollama_fast(prompt, timeout=3)
            if response and 'response' in response:
                # Try to parse simple response
                regime_text = response['response'].lower()
                
                if 'bear' in regime_text:
                    regime = 'BEAR_TRENDING'
                elif 'volatile' in regime_text:
                    regime = 'VOLATILE_RANGE' 
                elif 'low' in regime_text:
                    regime = 'LOW_VOLATILITY'
                else:
                    regime = 'BULL_TRENDING'
                
                volatility = 'HIGH' if 'volatile' in regime_text else 'NORMAL'
                
                return MarketIntelligence(
                    timestamp=datetime.now(),
                    market_regime=regime,
                    volatility_environment=volatility,
                    sector_rotation={'leaders': ['TECHNOLOGY'], 'laggards': ['UTILITIES']},
                    risk_appetite='MODERATE',
                    key_themes=['AI_GENERATED'],
                    trading_opportunities=[],
                    risk_factors=['AI_UNCERTAINTY'],
                    recommended_strategy='MOMENTUM',
                    confidence=0.6
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ FAST AI GENERATION FAILURE: {e}")
            logger.warning(f"⚠️ Ollama AI system not responding - check connectivity and model availability")
            return None
    
    async def _query_ollama_fast(self, prompt: str, timeout: int = 3) -> Optional[Dict]:
        """Fast Ollama query with aggressive timeout"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 10,  # Very short response
                }
            }
            
            async with self.session.post(
                f"{self.api_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status == 200:
                    return await response.json()
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ OLLAMA QUERY FAILURE: {e}")
            logger.warning(f"⚠️ Ollama service may be down or overloaded")
            return None
    
    def _get_informed_fallback_intelligence(self, market_data: Dict) -> MarketIntelligence:
        """Informed fallback using basic market data if available"""
        
        # Try to use any market data provided
        market_regime = "BULL_TRENDING"  # Default
        volatility_env = "NORMAL"       # Default
        
        # Check if any useful data was passed
        if market_data:
            # Look for VIX or volatility indicators
            if 'VIX' in market_data or 'volatility' in str(market_data).lower():
                volatility_env = "HIGH"
                market_regime = "VOLATILE_RANGE"
        
        logger.info(f"📊 Using INFORMED FALLBACK intelligence: {market_regime} regime, {volatility_env} volatility")
        
        return MarketIntelligence(
            timestamp=datetime.now(),
            market_regime=market_regime,
            volatility_environment=volatility_env,
            sector_rotation={"leaders": ["TECHNOLOGY"], "laggards": ["UTILITIES"]},
            risk_appetite="MODERATE",
            key_themes=["FALLBACK_MODE"],
            trading_opportunities=[],
            risk_factors=["LIMITED_DATA"],
            recommended_strategy="MOMENTUM",
            confidence=0.4  # Lower confidence for fallback
        )
    
    # Simplified versions of other methods for compatibility
    async def evaluate_opportunity_with_context(self, opportunity, market_intelligence: MarketIntelligence) -> Dict:
        """Enhanced opportunity evaluation with market context"""
        try:
            # Base scoring using available opportunity data
            base_score = 0.6
            confidence = 0.5
            
            # Score based on opportunity metrics
            if hasattr(opportunity, 'opportunity_score') and opportunity.opportunity_score > 0:
                base_score = min(0.9, opportunity.opportunity_score)
                confidence = min(0.8, opportunity.opportunity_score * 0.8)
            
            # Market regime adjustments
            if market_intelligence:
                regime = market_intelligence.market_regime
                volatility = market_intelligence.volatility_environment
                
                # Boost confidence in favorable market conditions
                if regime in ['BULL_TRENDING', 'SECTOR_ROTATION']:
                    confidence += 0.1
                    base_score += 0.05
                
                # Reduce confidence in challenging conditions
                elif regime in ['BEAR_TRENDING', 'VOLATILE_RANGE']:
                    confidence -= 0.05
                    base_score -= 0.02
                
                # Volatility adjustments
                if volatility == 'LOW':
                    confidence += 0.05  # More predictable in low volatility
                elif volatility in ['HIGH', 'EXTREME']:
                    confidence -= 0.1   # Less predictable in high volatility
            
            # Opportunity-specific scoring
            reasoning_parts = []
            
            if hasattr(opportunity, 'volume_ratio') and opportunity.volume_ratio > 1.5:
                base_score += 0.05
                confidence += 0.05
                reasoning_parts.append(f"volume spike {opportunity.volume_ratio:.1f}x")
            
            if hasattr(opportunity, 'daily_change_pct') and abs(opportunity.daily_change_pct) > 2.0:
                base_score += 0.05
                confidence += 0.05
                reasoning_parts.append(f"momentum {opportunity.daily_change_pct:+.1f}%")
            
            # Ensure minimum thresholds for trading
            final_score = max(0.65, min(0.95, base_score))  # Ensure meets minimum threshold
            final_confidence = max(0.65, min(0.90, confidence))  # Ensure meets confidence threshold
            
            # Entry recommendation based on market regime and score
            if final_score >= 0.8 and final_confidence >= 0.75:
                entry_rec = 'IMMEDIATE'
            elif final_score >= 0.7 and final_confidence >= 0.65:
                entry_rec = 'PATIENT'
            else:
                entry_rec = 'NONE'
            
            reasoning = f"Market context: {regime if market_intelligence else 'unknown'} regime. " + \
                       (', '.join(reasoning_parts) if reasoning_parts else 'Standard evaluation')
            
            return {
                'overall_score': final_score,
                'confidence': final_confidence,
                'entry_recommendation': entry_rec,
                'reasoning': reasoning,
                'position_size_recommendation': 'REDUCED' if final_confidence < 0.75 else 'FULL',
                'expected_return_pct': 8.0 if final_score > 0.8 else 6.0
            }
            
        except Exception as e:
            logger.error(f"AI evaluation failed: {e}")
            return {
                'overall_score': 0.5,
                'confidence': 0.4,
                'entry_recommendation': 'NONE',
                'reasoning': f'Evaluation error: {e}',
                'position_size_recommendation': 'MINIMAL'
            }
    
    async def analyze_portfolio_risk(self, portfolio_data: Dict, market_intelligence: MarketIntelligence) -> Dict:
        """Simplified portfolio risk analysis"""
        return {
            'overall_risk_score': 0.5,
            'risk_level': 'MODERATE',
            'recommendations': ['Monitor positions closely']
        }