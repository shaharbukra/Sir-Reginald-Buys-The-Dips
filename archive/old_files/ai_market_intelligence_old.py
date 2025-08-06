"""
Enhanced AI assistant with market intelligence and few-shot prompting
Optimized for financial analysis and systematic decision making
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
    Uses advanced prompting techniques for consistent, reliable output
    """
    
    def __init__(self):
        self.session = None
        self.api_url = AI_CONFIG['ollama_url']
        self.model = AI_CONFIG['model_name']
        self.daily_intelligence = None
        self.last_intelligence_update = None
        
        # Few-shot examples for consistent output
        self.market_analysis_example = {
            "market_environment": {
                "regime": "BULL_TRENDING",
                "volatility": "NORMAL",
                "trend_strength": "STRONG",
                "risk_appetite": "MODERATE"
            },
            "sector_analysis": {
                "leaders": ["TECHNOLOGY", "FINANCIALS"],
                "laggards": ["UTILITIES", "REAL_ESTATE"],
                "rotation_active": True,
                "rotation_direction": "GROWTH_TO_VALUE"
            },
            "trading_strategy": {
                "primary_approach": "MOMENTUM",
                "timeframe": "3-7 days",
                "position_sizing": "MODERATE",
                "risk_level": "MEDIUM"
            }
        }
        
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
        """Clean shutdown"""
        if self.session:
            await self.session.close()
            
    async def generate_daily_market_intelligence(self, market_data: Dict) -> MarketIntelligence:
        """Generate comprehensive daily market intelligence report"""
        
        # Try data-driven analysis first, then AI, then fallback
        try:
            # OPTION 1: Use real market data analysis (most reliable)
            logger.info("📊 Generating market intelligence from real market data...")
            intelligence = await self._analyze_market_data_intelligence(market_data)
            if intelligence:
                logger.info(f"📊 Generated DATA-DRIVEN market intelligence: {intelligence.market_regime} regime, "
                           f"{intelligence.volatility_environment} volatility")
                return intelligence
        except Exception as e:
            logger.warning(f"Data-driven analysis failed: {e}")
        
        # OPTION 2: Try AI with shorter timeout (backup)
        if self.session:
            try:
                logger.info("🤖 Attempting AI-generated market intelligence...")
                intelligence = await self._generate_ai_intelligence_fast(market_data)
                if intelligence:
                    logger.info(f"📊 Generated AI market intelligence: {intelligence.market_regime} regime, "
                               f"{intelligence.volatility_environment} volatility")
                    return intelligence
            except Exception as e:
                logger.warning(f"AI generation failed: {e}")
        
        # OPTION 3: Fallback (last resort)
        logger.warning("⚠️ Using fallback intelligence - both data analysis and AI failed")
        return self._get_fallback_intelligence()
    
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
            logger.error(f"Market data analysis failed: {e}")
            return None
    
    async def _get_market_index_data(self, symbol: str) -> Optional[Dict]:
        """Get market index data for analysis"""
        try:
            # Import here to avoid circular imports
            from supplemental_data_provider import SupplementalDataProvider
            
            data_provider = SupplementalDataProvider()
            bars = await data_provider.get_historical_data(symbol, days=5, min_bars=3)
            
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
                    'high_52w': max(float(bar['h']) for bar in bars),
                    'low_52w': min(float(bar['l']) for bar in bars)
                }
            return None
        except Exception as e:
            logger.error(f"Error getting market index data: {e}")
            return None
    
    async def _get_volatility_data(self) -> Optional[Dict]:
        """Get VIX or volatility proxy data"""
        try:
            # Try to get VIX data
            vix_data = await self._get_market_index_data('VIX')
            if vix_data:
                return {
                    'vix_level': vix_data['current_price'],
                    'vix_change': vix_data['daily_change_pct']
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
                    'proxy': True
                }
            return None
        except Exception as e:
            logger.error(f"Error getting volatility data: {e}")
            return None
    
    def _determine_market_regime(self, spy_data: Optional[Dict], market_data: Dict) -> str:
        """Determine market regime from actual data"""
        if not spy_data:
            return "BULL_TRENDING"  # Default
        
        daily_change = spy_data['daily_change_pct']
        weekly_change = spy_data['weekly_change_pct']
        
        # Market regime logic based on actual price action
        if weekly_change > 3.0 and daily_change > 0.5:
            return "BULL_TRENDING"
        elif weekly_change < -3.0 and daily_change < -0.5:
            return "BEAR_TRENDING"
        elif abs(daily_change) > 2.0:
            return "VOLATILE_RANGE"
        elif abs(weekly_change) < 1.0:
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
        if spy_data['weekly_change_pct'] > 2.0 and vix_data['vix_level'] < 20:
            return "HIGH"
        # Risk-off conditions: SPY down, VIX up  
        elif spy_data['weekly_change_pct'] < -2.0 and vix_data['vix_level'] > 25:
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
                    if data and data['weekly_change_pct'] is not None:
                        sector_performance[sector] = data['weekly_change_pct']
                        
                        if data['weekly_change_pct'] > 2.0:
                            leaders.append(sector)
                        elif data['weekly_change_pct'] < -2.0:
                            laggards.append(sector)
                except Exception:
                    continue
                    
                # Rate limiting
                await asyncio.sleep(0.2)
            
            return {
                'leaders': leaders[:3] if leaders else ['TECHNOLOGY'],
                'laggards': laggards[:3] if laggards else ['UTILITIES'],
                'rotation_active': len(leaders) > 0 and len(laggards) > 0,
                'performance': sector_performance
            }
            
        except Exception as e:
            logger.error(f"Sector analysis failed: {e}")
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
            
        return risks[:3]  # Limit to top 3 risks
    
    def _calculate_data_confidence(self, spy_data: Optional[Dict], vix_data: Optional[Dict], 
                                  sector_analysis: Dict) -> float:
        """Calculate confidence based on data availability and quality"""
        confidence = 0.5  # Base confidence
        
        if spy_data:
            confidence += 0.2
        if vix_data:
            confidence += 0.15
        if sector_analysis.get('performance'):
            confidence += 0.1
        if len(sector_analysis.get('leaders', [])) > 0:
            confidence += 0.05
            
        return min(0.95, confidence)  # Cap at 95%
    
    async def _generate_ai_intelligence_fast(self, market_data: Dict) -> Optional[MarketIntelligence]:
        """Try AI generation with aggressive timeout"""
        try:
            # Much shorter timeout for AI
            prompt = f"""
ROLE: Senior quantitative strategist at elite trading firm
TASK: Generate daily market intelligence for systematic algorithmic trading

EXAMPLE OUTPUT (use this exact structure):
{json.dumps(self.market_analysis_example, indent=2)}

CURRENT MARKET DATA:
{json.dumps(market_data, indent=2)}

ANALYSIS FRAMEWORK:
1. Market Regime Classification:
   - BULL_TRENDING: Strong uptrend, momentum strategies optimal
   - BEAR_TRENDING: Downtrend, defensive positioning required
   - VOLATILE_RANGE: High volatility, mean reversion strategies
   - SECTOR_ROTATION: Leadership changing, relative strength key
   - LOW_VOLATILITY: Compression, breakout strategies optimal

2. Volatility Assessment:
   - LOW: VIX < 15, stable trends, momentum trading
   - NORMAL: VIX 15-25, standard volatility, all strategies viable
   - HIGH: VIX 25-35, increased risk, shorter timeframes
   - EXTREME: VIX > 35, defensive mode, cash preservation

3. Trading Strategy Selection:
   - MOMENTUM: Trending markets, strong directional moves
   - MEAN_REVERSION: Range-bound markets, overbought/oversold
   - BREAKOUT: Low volatility, compression patterns
   - DEFENSIVE: High uncertainty, capital preservation

REQUIRED OUTPUT FORMAT (JSON only):
{{
    "market_environment": {{
        "regime": "BULL_TRENDING",
        "volatility": "NORMAL",
        "trend_strength": "STRONG|MODERATE|WEAK",
        "risk_appetite": "HIGH|MODERATE|LOW",
        "vix_level": {market_data.get('VIX', {}).get('level', 'null')},
        "key_support": 4400,
        "key_resistance": 4500
    }},
    "sector_analysis": {{
        "leaders": ["TECHNOLOGY", "FINANCIALS"],
        "laggards": ["UTILITIES", "REAL_ESTATE"],
        "rotation_active": true,
        "rotation_direction": "GROWTH_TO_VALUE|VALUE_TO_GROWTH|NEUTRAL",
        "momentum_sectors": ["TECH", "FINANCE"],
        "defensive_sectors": ["UTILITIES", "HEALTHCARE"]
    }},
    "trading_strategy": {{
        "primary_approach": "MOMENTUM",
        "secondary_approach": "BREAKOUT",
        "optimal_timeframe": "3-7 days",
        "position_sizing": "AGGRESSIVE|MODERATE|CONSERVATIVE", 
        "risk_level": "LOW|MEDIUM|HIGH",
        "max_positions": 8,
        "preferred_instruments": ["STOCKS", "OPTIONS", "ETFS"]
    }},
    "opportunity_focus": {{
        "price_action": "BREAKOUTS|MOMENTUM|REVERSALS",
        "volume_profile": "EXPANSION|NORMAL|CONTRACTION",
        "catalyst_priority": "EARNINGS|NEWS|TECHNICAL|SECTOR",
        "entry_timing": "IMMEDIATE|PATIENT|SELECTIVE"
    }},
    "risk_factors": {{
        "primary_risks": ["FEDERAL_RESERVE", "GEOPOLITICAL", "EARNINGS"],
        "risk_level": "LOW|MEDIUM|HIGH|EXTREME",
        "hedging_recommended": true,
        "cash_allocation": 0.15,
        "max_drawdown_acceptable": 0.08
    }},
    "confidence_metrics": {{
        "overall_confidence": 0.85,
        "regime_confidence": 0.90,
        "strategy_confidence": 0.80,
        "timeframe_confidence": 0.85
    }}
}}

CRITICAL: Return ONLY valid JSON. No explanatory text before or after.
"""

        try:
            response = await self._query_ollama_with_retries(prompt)
            intelligence_data = self._parse_json_response_robust(response)
            
            # Create MarketIntelligence object
            intelligence = MarketIntelligence(
                timestamp=datetime.now(),
                market_regime=intelligence_data.get('market_environment', {}).get('regime', 'BULL_TRENDING'),
                volatility_environment=intelligence_data.get('market_environment', {}).get('volatility', 'NORMAL'),
                sector_rotation=intelligence_data.get('sector_analysis', {}),
                risk_appetite=intelligence_data.get('market_environment', {}).get('risk_appetite', 'MODERATE'),
                key_themes=intelligence_data.get('opportunity_focus', {}).get('catalyst_priority', []),
                trading_opportunities=[],  # Will be filled by separate analysis
                risk_factors=intelligence_data.get('risk_factors', {}).get('primary_risks', []),
                recommended_strategy=intelligence_data.get('trading_strategy', {}).get('primary_approach', 'MOMENTUM'),
                confidence=intelligence_data.get('confidence_metrics', {}).get('overall_confidence', 0.7)
            )
            
            # Cache for reuse
            self.daily_intelligence = intelligence
            self.last_intelligence_update = datetime.now()
            
            logger.info(f"📊 Generated AI market intelligence: {intelligence.market_regime} regime, "
                       f"{intelligence.volatility_environment} volatility")
                       
            return intelligence
            
        except Exception as e:
            logger.warning(f"⚠️ AI generation failed, using fallback intelligence: {e}")
            logger.info("🔄 Using hardcoded market intelligence (BULL_TRENDING/NORMAL)")
            return self._get_fallback_intelligence()
            
    async def evaluate_opportunity_with_context(self, opportunity, market_intelligence: MarketIntelligence) -> Dict:
        """Evaluate specific trading opportunity against market context"""
        
        prompt = f"""
ROLE: Senior portfolio manager evaluating trading opportunity
TASK: Score opportunity for systematic momentum trading system

MARKET CONTEXT:
- Regime: {market_intelligence.market_regime}
- Volatility: {market_intelligence.volatility_environment}
- Strategy: {market_intelligence.recommended_strategy}
- Risk Appetite: {market_intelligence.risk_appetite}

OPPORTUNITY DATA:
- Symbol: {opportunity.symbol}
- Price: ${opportunity.current_price:.2f}
- Daily Change: {opportunity.daily_change_pct:.1f}%
- Volume Ratio: {opportunity.volume_ratio:.1f}x
- Discovery Source: {opportunity.discovery_source}
- Sector: {opportunity.sector}
- Market Cap: ${opportunity.market_cap/1e9:.1f}B

TECHNICAL INDICATORS:
- RSI: {opportunity.rsi or 'N/A'}
- 10-day MA: ${opportunity.ma_10 or 'N/A'}
- 20-day MA: ${opportunity.ma_20 or 'N/A'}
- ATR: {opportunity.atr or 'N/A'}

EVALUATION CRITERIA:
1. Market Context Alignment (0.0-1.0)
2. Technical Setup Quality (0.0-1.0)
3. Risk/Reward Potential (0.0-1.0)
4. Timing Appropriateness (0.0-1.0)
5. Liquidity and Execution (0.0-1.0)

RETURN JSON:
{{
    "overall_score": 0.85,
    "confidence": 0.80,
    "expected_return_pct": 12.5,
    "expected_timeframe_days": 5,
    "risk_level": "MEDIUM",
    "context_alignment": 0.90,
    "technical_quality": 0.85,
    "risk_reward_ratio": 2.8,
    "execution_difficulty": "EASY",
    "primary_catalyst": "Volume breakout with momentum confirmation",
    "entry_recommendation": "IMMEDIATE|PATIENT|AVOID",
    "position_size_recommendation": "FULL|REDUCED|MINIMAL",
    "key_risks": ["Momentum failure", "Market regime change"],
    "exit_strategy": "Technical stop loss at 8%, profit target at 20%",
    "reasoning": "Strong volume breakout aligns with bull trending regime..."
}}
"""

        try:
            response = await self._query_ollama_with_retries(prompt)
            evaluation = self._parse_json_response_robust(response)
            
            # Debug logging for troubleshooting
            logger.debug(f"AI raw response for {opportunity.symbol}: {response.get('response', '')[:200]}...")
            logger.debug(f"AI parsed evaluation for {opportunity.symbol}: {evaluation}")
            
            # Use fallback if parsing failed (empty dict)
            if not evaluation or evaluation.get('overall_score', 0) == 0:
                logger.warning(f"AI evaluation parsing failed for {opportunity.symbol}, using fallback")
                return self._get_fallback_evaluation(opportunity)
                
            return evaluation
        except Exception as e:
            logger.error(f"Opportunity evaluation failed: {e}")
            return self._get_fallback_evaluation(opportunity)
            
    async def analyze_portfolio_risk(self, portfolio_data: Dict, market_intelligence: MarketIntelligence) -> Dict:
        """Comprehensive portfolio risk analysis"""
        
        prompt = f"""
ROLE: Chief Risk Officer analyzing portfolio for systematic trading
TASK: Evaluate portfolio risk and provide recommendations

PORTFOLIO DATA:
{json.dumps(portfolio_data, indent=2)}

MARKET CONTEXT:
- Regime: {market_intelligence.market_regime}
- Volatility: {market_intelligence.volatility_environment}
- Risk Factors: {market_intelligence.risk_factors}

RISK ASSESSMENT FRAMEWORK:
1. Position Concentration Risk
2. Sector/Correlation Risk  
3. Market Regime Risk
4. Liquidity Risk
5. Drawdown Risk

RETURN JSON:
{{
    "overall_risk_score": 0.65,
    "risk_level": "MEDIUM",
    "portfolio_health": "GOOD",
    "key_risks": [
        "High technology concentration (45%)",
        "Momentum strategy vulnerable to regime change"
    ],
    "risk_metrics": {{
        "concentration_risk": 0.7,
        "correlation_risk": 0.6,
        "liquidity_risk": 0.3,
        "regime_risk": 0.5,
        "drawdown_risk": 0.4
    }},
    "recommendations": [
        "Reduce technology exposure to <35%",
        "Add defensive hedge position",
        "Tighten stop losses in current environment"
    ],
    "position_adjustments": {{
        "reduce_exposure": [],
        "increase_exposure": [],
        "hedge_positions": ["VIX calls", "SPY puts"]
    }},
    "max_new_position_size": 0.06,
    "emergency_stop_level": 0.08
}}
"""

        try:
            response = await self._query_ollama_with_retries(prompt)
            return self._parse_json_response_robust(response)
        except Exception as e:
            logger.error(f"Portfolio risk analysis failed: {e}")
            return self._get_fallback_risk_analysis()
            
    async def _query_ollama_with_retries(self, prompt: str, max_retries: int = 3) -> Dict:
        """Query Ollama with retry logic and error handling"""
        
        logger.debug(f"🤖 Attempting to query Ollama (model: {self.model})...")
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"🔄 Ollama attempt {attempt + 1}/{max_retries}")
                
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": AI_CONFIG['temperature'],
                        "num_predict": AI_CONFIG['max_tokens'],
                        "top_p": 0.9,
                        "stop": ["Human:", "Assistant:"]
                    }
                }
                
                async with self.session.post(
                    f"{self.api_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=AI_CONFIG['request_timeout'])
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        if 'response' in result and result['response'].strip():
                            return result
                        else:
                            logger.warning(f"Empty response from Ollama on attempt {attempt + 1}")
                    else:
                        logger.warning(f"Ollama HTTP {response.status} on attempt {attempt + 1}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Ollama timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.warning(f"Ollama error on attempt {attempt + 1}: {e}")
                
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        logger.error("All Ollama retry attempts failed")
        return {"response": "{}"}
        
    def _parse_json_response_robust(self, response: Dict) -> Dict:
        """Robust JSON parsing with multiple fallback strategies"""
        
        response_text = response.get('response', '{}').strip()
        
        if not response_text:
            return {}
            
        # Try direct JSON parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
            
        # Try extracting JSON from response
        json_patterns = [
            r'\{.*\}',  # Match entire JSON object
            r'\[.*\]',  # Match JSON array
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
                    
        # Try finding JSON between markers
        start_markers = ['{', '[']
        end_markers = ['}', ']']
        
        for start_char, end_char in zip(start_markers, end_markers):
            start_idx = response_text.find(start_char)
            end_idx = response_text.rfind(end_char)
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                try:
                    json_str = response_text[start_idx:end_idx+1]
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
                    
        logger.debug(f"JSON parsing failed, using fallback (response: {response_text[:100]}...)")
        return {}
        
    def _get_fallback_intelligence(self) -> MarketIntelligence:
        """Fallback market intelligence when AI fails"""
        logger.info("📊 Using FALLBACK market intelligence: BULL_TRENDING regime, NORMAL volatility")
        return MarketIntelligence(
            timestamp=datetime.now(),
            market_regime="BULL_TRENDING",
            volatility_environment="NORMAL",
            sector_rotation={"leaders": ["TECHNOLOGY"], "laggards": ["UTILITIES"]},
            risk_appetite="MODERATE",
            key_themes=["MOMENTUM"],
            trading_opportunities=[],
            risk_factors=["MARKET_VOLATILITY"],
            recommended_strategy="MOMENTUM",
            confidence=0.5
        )
        
    def _get_fallback_evaluation(self, opportunity) -> Dict:
        """Fallback opportunity evaluation"""
        # Calculate basic score based on opportunity metrics
        base_score = 0.6
        
        # Boost score for high volume (simplified signal generation was triggered)
        if hasattr(opportunity, 'volume_ratio') and opportunity.volume_ratio > 2.0:
            base_score += 0.15
            
        # Boost score for positive momentum  
        if hasattr(opportunity, 'daily_change_pct') and opportunity.daily_change_pct > 0:
            base_score += 0.10
            
        overall_score = min(0.85, base_score)
        confidence = min(0.75, base_score - 0.05)
        
        return {
            "overall_score": overall_score,
            "confidence": confidence,
            "expected_return_pct": 8.0,
            "expected_timeframe_days": 5,
            "risk_level": "MEDIUM",
            "context_alignment": 0.70,
            "technical_quality": 0.65,
            "risk_reward_ratio": 2.0,
            "execution_difficulty": "EASY",
            "primary_catalyst": "High volume momentum signal",
            "entry_recommendation": "IMMEDIATE" if overall_score >= 0.75 else "PATIENT",
            "position_size_recommendation": "REDUCED",
            "key_risks": ["Market volatility", "Momentum reversal"],
            "exit_strategy": "Stop loss at 5%, profit target at 10%",
            "reasoning": f"AI analysis unavailable, fallback evaluation: score={overall_score:.2f} based on volume and momentum"
        }
        
    def _get_fallback_risk_analysis(self) -> Dict:
        """Fallback risk analysis"""
        return {
            "overall_risk_score": 0.6,
            "risk_level": "MEDIUM",
            "portfolio_health": "UNKNOWN",
            "recommendations": ["Monitor portfolio closely"],
            "max_new_position_size": 0.02
        }
        
    async def get_cached_intelligence(self) -> Optional[MarketIntelligence]:
        """Get cached daily intelligence if still valid"""
        if (self.daily_intelligence and self.last_intelligence_update and
            (datetime.now() - self.last_intelligence_update).total_seconds() < 3600):  # 1 hour cache
            return self.daily_intelligence
        return None