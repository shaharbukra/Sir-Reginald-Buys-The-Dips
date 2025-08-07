"""
Gap Risk Manager for Pre-Market and After-Hours Protection
Monitors and protects positions during extended hours trading
"""

import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GapRiskAlert:
    """Gap risk alert for extended hours moves"""
    symbol: str
    gap_percent: float
    current_price: float
    previous_close: float
    position_impact: float
    risk_level: str
    timestamp: datetime

class GapRiskManager:
    """
    Manages gap risk for positions during extended hours
    Provides early warning system for overnight and pre-market moves
    """
    
    def __init__(self):
        self.position_closes = {}  # Track closing prices for gap calculation
        self.gap_alerts_sent = set()  # Prevent duplicate alerts
        self.last_reset_date = datetime.now().date()
        
    def record_market_close_positions(self, positions: List) -> None:
        """Record position prices at market close for gap calculation"""
        try:
            current_date = datetime.now().date()
            
            # Reset daily tracking
            if current_date != self.last_reset_date:
                self.position_closes.clear()
                self.gap_alerts_sent.clear()
                self.last_reset_date = current_date
            
            for position in positions:
                if float(position.qty) != 0:
                    symbol = position.symbol
                    # Use market value / quantity to get approximate close price
                    close_price = float(position.market_value) / abs(float(position.qty))
                    self.position_closes[symbol] = {
                        'close_price': close_price,
                        'quantity': float(position.qty),
                        'close_time': datetime.now()
                    }
            
            if self.position_closes:
                logger.info(f"📊 Recorded {len(self.position_closes)} position closes for gap risk monitoring")
                
        except Exception as e:
            logger.error(f"Failed to record market close positions: {e}")
    
    def calculate_gap_risk(self, symbol: str, current_price: float) -> Optional[GapRiskAlert]:
        """Calculate gap risk for a position"""
        try:
            if symbol not in self.position_closes:
                return None
            
            position_data = self.position_closes[symbol]
            close_price = position_data['close_price']
            quantity = position_data['quantity']
            
            # Calculate gap percentage
            gap_percent = ((current_price - close_price) / close_price) * 100
            
            # Calculate position impact
            position_impact = (current_price - close_price) * abs(quantity)
            
            # Determine risk level
            if abs(gap_percent) >= 10:
                risk_level = "EXTREME"
            elif abs(gap_percent) >= 5:
                risk_level = "HIGH"  
            elif abs(gap_percent) >= 2:
                risk_level = "MODERATE"
            else:
                risk_level = "LOW"
            
            return GapRiskAlert(
                symbol=symbol,
                gap_percent=gap_percent,
                current_price=current_price,
                previous_close=close_price,
                position_impact=position_impact,
                risk_level=risk_level,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Gap risk calculation failed for {symbol}: {e}")
            return None
    
    def should_alert_gap_risk(self, alert: GapRiskAlert) -> bool:
        """Determine if gap risk alert should be sent"""
        try:
            # Only alert on significant gaps
            if abs(alert.gap_percent) < 2:
                return False
            
            # Prevent duplicate alerts for same symbol
            alert_key = f"{alert.symbol}_{alert.risk_level}"
            if alert_key in self.gap_alerts_sent:
                return False
            
            self.gap_alerts_sent.add(alert_key)
            return True
            
        except Exception as e:
            logger.error(f"Gap alert decision failed: {e}")
            return False
    
    def reset_alert_tracking(self):
        """Reset alert tracking for new trading session"""
        try:
            alerts_cleared = len(self.gap_alerts_sent)
            self.gap_alerts_sent.clear()
            if alerts_cleared > 0:
                logger.info(f"🔄 Reset {alerts_cleared} gap risk alert suppressions for new trading session")
        except Exception as e:
            logger.error(f"Failed to reset alert tracking: {e}")
    
    def get_portfolio_gap_exposure(self) -> Dict:
        """Get overall portfolio gap risk exposure"""
        try:
            total_positions = len(self.position_closes)
            
            if total_positions == 0:
                return {
                    'total_positions_at_risk': 0,
                    'max_single_position_value': 0,
                    'total_market_exposure': 0,
                    'risk_level': 'NONE'
                }
            
            # Calculate exposure metrics
            total_exposure = sum(
                abs(pos_data['quantity']) * pos_data['close_price'] 
                for pos_data in self.position_closes.values()
            )
            
            max_position_value = max(
                abs(pos_data['quantity']) * pos_data['close_price']
                for pos_data in self.position_closes.values()
            )
            
            # Determine overall risk level
            if total_positions >= 5:
                risk_level = "HIGH"
            elif total_positions >= 3:
                risk_level = "MODERATE"
            else:
                risk_level = "LOW"
            
            return {
                'total_positions_at_risk': total_positions,
                'max_single_position_value': max_position_value,
                'total_market_exposure': total_exposure,
                'risk_level': risk_level,
                'positions': list(self.position_closes.keys())
            }
            
        except Exception as e:
            logger.error(f"Portfolio gap exposure calculation failed: {e}")
            return {'error': str(e)}
    
    def generate_gap_risk_report(self) -> Dict:
        """Generate comprehensive gap risk report"""
        try:
            exposure = self.get_portfolio_gap_exposure()
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': len(self.position_closes) > 0,
                'positions_monitored': list(self.position_closes.keys()),
                'total_exposure': exposure.get('total_market_exposure', 0),
                'risk_assessment': exposure.get('risk_level', 'UNKNOWN'),
                'alerts_sent_today': len(self.gap_alerts_sent),
                'recommendations': []
            }
            
            # Add recommendations based on risk level
            if exposure.get('risk_level') == 'HIGH':
                report['recommendations'].extend([
                    'Consider reducing position sizes before market close',
                    'Set tight stop losses on volatile positions',
                    'Monitor extended hours news and earnings calendars'
                ])
            elif exposure.get('risk_level') == 'MODERATE':
                report['recommendations'].extend([
                    'Monitor positions during extended hours',
                    'Be prepared for gap openings'
                ])
            
            return report
            
        except Exception as e:
            logger.error(f"Gap risk report generation failed: {e}")
            return {'error': str(e)}