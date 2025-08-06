"""
Conservative risk manager with multi-layer protection
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from config import *

logger = logging.getLogger(__name__)

@dataclass
class RiskAssessment:
    """Risk assessment result"""
    approved: bool
    risk_score: float
    max_position_size: float
    warnings: List[str]
    reasoning: str

class ConservativeRiskManager:
    """
    Multi-layer risk management system with conservative defaults
    Protects against position risk, portfolio risk, and drawdown risk
    """
    
    def __init__(self):
        self.initial_account_value = None
        self.daily_high_water_mark = None
        self.session_start_value = None
        self.risk_metrics = {}
        
        # Track daily performance
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.session_trades = []
        
    async def initialize(self, account_value: float):
        """Initialize risk manager with account value"""
        self.initial_account_value = account_value
        self.session_start_value = account_value
        self.daily_high_water_mark = account_value
        self.circuit_breaker_triggered = False
        
        now = datetime.now()
        self.risk_metrics = {
            'daily_start_value': account_value,
            'daily_high_water_mark': account_value,
            'last_reset_date': now.date(),
            'consecutive_losing_days': 0,
            'max_daily_drawdown_hit': False
        }
        
        logger.info(f"💰 Risk Manager initialized with ${account_value:,.2f}")
        logger.info(f"⚡ Circuit breaker at ${account_value * 0.95:,.2f} (-5% total loss)")
        
    async def assess_position_risk(self, signal, current_account_value: float, 
                                 existing_positions: List = None) -> RiskAssessment:
        """Comprehensive position risk assessment"""
        try:
            warnings = []
            risk_score = 0.0
            
            # === BASIC POSITION VALIDATION ===
            if signal.position_size_pct > RISK_CONFIG['max_position_risk_pct']:
                warnings.append(f"Position size too large: {signal.position_size_pct}%")
                signal.position_size_pct = RISK_CONFIG['max_position_risk_pct']
                
            # === RISK/REWARD VALIDATION ===
            if signal.risk_reward_ratio < RISK_CONFIG['min_risk_reward_ratio']:
                return RiskAssessment(
                    approved=False,
                    risk_score=1.0,
                    max_position_size=0.0,
                    warnings=[f"R/R ratio too low: {signal.risk_reward_ratio:.2f}"],
                    reasoning="Risk/reward ratio below minimum threshold"
                )
                
            # === DAILY TRADE LIMIT ===
            if self.daily_trades >= SYSTEM_CONFIG['max_daily_trades']:
                return RiskAssessment(
                    approved=False,
                    risk_score=1.0,
                    max_position_size=0.0,
                    warnings=["Daily trade limit exceeded"],
                    reasoning="Maximum daily trades reached"
                )
                
            # === PORTFOLIO CONCENTRATION ===
            portfolio_risk = await self._assess_portfolio_concentration(
                signal, existing_positions or []
            )
            
            if portfolio_risk['concentration_risk'] > 0.8:
                warnings.append("High portfolio concentration risk")
                risk_score += 0.3
                
            # === SECTOR CONCENTRATION ===
            sector_exposure = self._calculate_sector_exposure(signal, existing_positions or [])
            if sector_exposure > RISK_CONFIG['max_sector_concentration']:
                adjusted_size = signal.position_size_pct * 0.5
                warnings.append(f"Sector concentration limit, reducing size to {adjusted_size}%")
                signal.position_size_pct = adjusted_size
                
            # === CORRELATION RISK ===
            correlation_risk = await self._assess_correlation_risk(signal, existing_positions or [])
            if correlation_risk > RISK_CONFIG['max_correlation_exposure']:
                warnings.append("High correlation risk with existing positions")
                risk_score += 0.2
                
            # === VOLATILITY ASSESSMENT ===
            if hasattr(signal, 'atr') and signal.atr:
                atr_pct = (signal.atr / signal.entry_price) * 100
                if atr_pct > 10.0:  # Very high volatility
                    warnings.append(f"High volatility stock: {atr_pct:.1f}% ATR")
                    signal.position_size_pct *= 0.7  # Reduce size
                    risk_score += 0.2
                    
            # === ACCOUNT SIZE VALIDATION ===
            position_value = current_account_value * (signal.position_size_pct / 100)
            if position_value < 100:  # Minimum position size
                return RiskAssessment(
                    approved=False,
                    risk_score=0.5,
                    max_position_size=0.0,
                    warnings=["Position size too small to be effective"],
                    reasoning="Minimum position size not met"
                )
                
            # === FINAL RISK SCORE ===
            base_risk = signal.position_size_pct / RISK_CONFIG['max_position_risk_pct']
            confidence_adjustment = (1.0 - signal.confidence) * 0.3
            final_risk_score = base_risk + risk_score + confidence_adjustment
            
            # === APPROVAL DECISION ===
            max_risk_threshold = 0.8
            approved = final_risk_score <= max_risk_threshold
            
            if not approved:
                warnings.append(f"Risk score too high: {final_risk_score:.2f}")
                
            return RiskAssessment(
                approved=approved,
                risk_score=final_risk_score,
                max_position_size=signal.position_size_pct,
                warnings=warnings,
                reasoning=f"Risk assessment: {final_risk_score:.2f} score, {len(warnings)} warnings"
            )
            
        except Exception as e:
            logger.error(f"Position risk assessment failed: {e}")
            return RiskAssessment(
                approved=False,
                risk_score=1.0,
                max_position_size=0.0,
                warnings=["Risk assessment failed"],
                reasoning=f"Error in risk assessment: {e}"
            )
            
    async def check_daily_drawdown(self, current_account_value: float) -> bool:
        """Check if daily drawdown limit is exceeded"""
        try:
            # Reset daily tracking if new day
            today = datetime.now().date()
            if self.risk_metrics['last_reset_date'] != today:
                await self._reset_daily_metrics(current_account_value, today)
                
            # Calculate current drawdown
            daily_start = self.risk_metrics['daily_start_value']
            current_drawdown_pct = ((daily_start - current_account_value) / daily_start) * 100
            
            # Update high water mark
            if current_account_value > self.risk_metrics['daily_high_water_mark']:
                self.risk_metrics['daily_high_water_mark'] = current_account_value
                
            # Check drawdown limit
            max_dd = RISK_CONFIG['max_daily_drawdown_pct']
            if current_drawdown_pct > max_dd:
                if not self.risk_metrics['max_daily_drawdown_hit']:
                    logger.critical(f"🚨 DAILY DRAWDOWN LIMIT EXCEEDED: {current_drawdown_pct:.2f}%")
                    self.risk_metrics['max_daily_drawdown_hit'] = True
                    
                return True  # Emergency stop triggered
                
            return False
            
        except Exception as e:
            logger.error(f"Daily drawdown check failed: {e}")
            return False
    
    async def check_circuit_breaker(self, current_equity: float) -> bool:
        """Check if circuit breaker should trigger (flash crash protection)"""
        try:
            # Circuit breaker at 5% total account loss (more severe than daily drawdown)
            circuit_breaker_level = self.initial_account_value * 0.95
            
            if current_equity <= circuit_breaker_level and not self.circuit_breaker_triggered:
                total_loss_pct = ((self.initial_account_value - current_equity) / self.initial_account_value) * 100
                logger.critical(f"⚡ CIRCUIT BREAKER TRIGGERED: ${current_equity:,.2f} <= ${circuit_breaker_level:,.2f}")
                logger.critical(f"⚡ Total loss: {total_loss_pct:.1f}% - EMERGENCY LIQUIDATION REQUIRED")
                self.circuit_breaker_triggered = True
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Circuit breaker check failed: {e}")
            return False
            
    async def validate_trade_execution(self, signal, account_value: float) -> bool:
        """Final validation before trade execution"""
        try:
            # PDT rule compliance check
            if account_value < RISK_CONFIG['account_size_threshold']:
                # Check day trade count to avoid PDT violation
                day_trades_today = await self._count_day_trades_today()
                if day_trades_today >= 3:  # Stay under PDT limit
                    logger.warning("⚠️ PDT limit approaching, blocking trade")
                    return False
                    
            # Emergency conditions
            if self.risk_metrics.get('max_daily_drawdown_hit', False):
                logger.warning("⚠️ Daily drawdown limit hit, blocking new trades")
                return False
                
            # Excessive trading check
            if self.daily_trades >= SYSTEM_CONFIG['max_daily_trades']:
                logger.warning("⚠️ Maximum daily trades reached")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Trade execution validation failed: {e}")
            return False
            
    async def record_trade_execution(self, signal, execution_price: float, quantity: int):
        """Record executed trade for risk tracking"""
        try:
            trade_record = {
                'symbol': signal.symbol,
                'action': signal.action,
                'execution_price': execution_price,
                'quantity': quantity,
                'timestamp': datetime.now(),
                'position_size_pct': signal.position_size_pct,
                'risk_reward_ratio': signal.risk_reward_ratio
            }
            
            self.session_trades.append(trade_record)
            self.daily_trades += 1
            
            logger.info(f"📝 Trade recorded: {signal.symbol} {signal.action} "
                       f"{quantity} @ ${execution_price:.2f}")
                       
        except Exception as e:
            logger.error(f"Trade recording failed: {e}")
            
    async def _assess_portfolio_concentration(self, signal, existing_positions: List) -> Dict:
        """Assess portfolio concentration risk"""
        try:
            total_positions = len(existing_positions) + 1  # +1 for new position
            concentration_risk = min(1.0, total_positions / FUNNEL_CONFIG['max_active_positions'])
            
            # Calculate position value distribution
            position_values = [float(pos.market_value) for pos in existing_positions if hasattr(pos, 'market_value')]
            
            if position_values:
                # Check if new position would create concentration
                new_position_size = signal.position_size_pct / 100
                max_existing_size = max(position_values) / sum(position_values) if position_values else 0
                
                if new_position_size > 0.3 or max_existing_size > 0.4:  # 30% or 40% concentration
                    concentration_risk += 0.3
                    
            return {
                'concentration_risk': concentration_risk,
                'total_positions': total_positions,
                'max_positions': FUNNEL_CONFIG['max_active_positions']
            }
            
        except Exception as e:
            logger.error(f"Portfolio concentration assessment failed: {e}")
            return {'concentration_risk': 0.5}
            
    def _calculate_sector_exposure(self, signal, existing_positions: List) -> float:
        """Calculate sector exposure percentage"""
        try:
            # This would use real sector data
            # For now, simulate sector exposure calculation
            same_sector_positions = 0
            
            for pos in existing_positions:
                if hasattr(pos, 'symbol'):
                    # Simulate sector matching (would use real sector data)
                    if signal.symbol[0] == pos.symbol[0]:  # Simple heuristic
                        same_sector_positions += 1
                        
            total_positions = len(existing_positions) + 1
            sector_exposure = same_sector_positions / total_positions if total_positions > 0 else 0
            
            return sector_exposure
            
        except Exception as e:
            logger.error(f"Sector exposure calculation failed: {e}")
            return 0.5
            
    async def _assess_correlation_risk(self, signal, existing_positions: List) -> float:
        """Assess correlation risk with existing positions"""
        try:
            # Simplified correlation assessment
            # In production, would use actual correlation data
            
            if not existing_positions:
                return 0.0
                
            # Check for similar symbols (tech stocks, etc.)
            tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMD', 'TSLA']
            
            signal_is_tech = signal.symbol in tech_symbols
            tech_positions = sum(1 for pos in existing_positions 
                               if hasattr(pos, 'symbol') and pos.symbol in tech_symbols)
                               
            if signal_is_tech and tech_positions > 0:
                correlation_risk = min(1.0, tech_positions / len(existing_positions))
                return correlation_risk
                
            return 0.2  # Base correlation risk
            
        except Exception as e:
            logger.error(f"Correlation risk assessment failed: {e}")
            return 0.5
            
    async def _reset_daily_metrics(self, current_value: float, today):
        """Reset daily risk metrics for new trading day"""
        self.risk_metrics.update({
            'daily_start_value': current_value,
            'daily_high_water_mark': current_value,
            'last_reset_date': today,
            'max_daily_drawdown_hit': False
        })
        
        self.daily_trades = 0
        self.daily_pnl = 0.0
        
        logger.info(f"📅 Daily risk metrics reset for {today}")
        
    async def _count_day_trades_today(self) -> int:
        """Count day trades executed today for PDT compliance"""
        try:
            today = datetime.now().date()
            day_trades = 0
            
            for trade in self.session_trades:
                if (trade['timestamp'].date() == today and 
                    trade['action'] == 'SELL'):  # Simplified day trade detection
                    day_trades += 1
                    
            return day_trades
            
        except Exception as e:
            logger.error(f"Day trade counting failed: {e}")
            return 0
            
    async def get_risk_summary(self) -> Dict:
        """Get comprehensive risk summary"""
        try:
            current_time = datetime.now()
            
            return {
                'daily_trades': self.daily_trades,
                'max_daily_trades': SYSTEM_CONFIG['max_daily_trades'],
                'trades_remaining': max(0, SYSTEM_CONFIG['max_daily_trades'] - self.daily_trades),
                'daily_drawdown_limit': RISK_CONFIG['max_daily_drawdown_pct'],
                'daily_drawdown_hit': self.risk_metrics.get('max_daily_drawdown_hit', False),
                'risk_metrics': self.risk_metrics,
                'session_trades': len(self.session_trades),
                'last_update': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Risk summary generation failed: {e}")
            return {'error': str(e)}