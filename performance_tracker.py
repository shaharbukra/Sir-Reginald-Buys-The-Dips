"""
Performance tracking and metrics calculation using REAL Alpaca API data
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class PerformanceTracker:
    """
    Performance tracking system using REAL Alpaca account data as source of truth
    """
    
    def __init__(self, gateway):
        self.gateway = gateway
        self.initial_value = None
        self.session_start_time = datetime.now()
        self.session_start_value = None
        self.daily_snapshots = []
        self.performance_cache = {}
        self.last_update = None
        
    async def initialize(self):
        """Initialize performance tracking with REAL account data"""
        try:
            # Get actual current account value from Alpaca
            account = await self.gateway.get_account_safe()
            if not account:
                raise Exception("Unable to get account data from Alpaca")
                
            current_equity = float(account.equity)
            
            # Set initial values
            self.session_start_value = current_equity
            self.session_start_time = datetime.now()
            
            # Load or set initial account value (first time system ran)
            if not self.initial_value:
                self.initial_value = self._load_or_set_initial_value(current_equity)
            
            logger.info(f"📊 Performance tracking initialized")
            logger.info(f"   Initial account value: ${self.initial_value:,.2f}")  
            logger.info(f"   Session start value: ${current_equity:,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance tracker initialization failed: {e}")
            return False
    
    def _load_or_set_initial_value(self, current_value: float) -> float:
        """Load initial value from file or set it for first time"""
        try:
            initial_value_file = "initial_account_value.json"
            
            if os.path.exists(initial_value_file):
                with open(initial_value_file, 'r') as f:
                    data = json.load(f)
                    return data['initial_value']
            else:
                # First time - save current value as initial
                data = {
                    'initial_value': current_value,
                    'date_started': datetime.now().isoformat()
                }
                with open(initial_value_file, 'w') as f:
                    json.dump(data, f)
                logger.info(f"📊 First time setup - saved initial value: ${current_value:,.2f}")
                return current_value
                
        except Exception as e:
            logger.warning(f"⚠️ Could not load initial value, using current: {e}")
            return current_value
        
    async def update_performance(self):
        """Update performance metrics using REAL Alpaca data"""
        try:
            # Get fresh account data from Alpaca
            account = await self.gateway.get_account_safe()
            if not account:
                logger.warning("⚠️ Could not get account data for performance update")
                return
                
            current_equity = float(account.equity)
            last_equity = float(account.last_equity)  # Previous day's closing equity
            
            # Update cache with real data
            self.performance_cache = {
                'current_equity': current_equity,
                'last_equity': last_equity,
                'session_start_equity': self.session_start_value,
                'initial_equity': self.initial_value,
                'last_update': datetime.now()
            }
            
            self.last_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Performance update failed: {e}")
            
    async def get_daily_summary(self) -> Dict:
        """Get daily performance summary using REAL data"""
        try:
            await self.update_performance()
            
            if not self.performance_cache:
                return {
                    'daily_pnl': 0.0,
                    'daily_pnl_pct': 0.0,
                    'total_pnl': 0.0, 
                    'total_pnl_pct': 0.0,
                    'current_equity': self.session_start_value or 0.0,
                    'error': 'No performance data available'
                }
                
            current_equity = self.performance_cache['current_equity']
            last_equity = self.performance_cache['last_equity'] 
            initial_equity = self.performance_cache['initial_equity']
            
            # Calculate REAL performance metrics
            daily_pnl = current_equity - last_equity
            daily_pnl_pct = (daily_pnl / last_equity * 100) if last_equity > 0 else 0.0
            
            total_pnl = current_equity - initial_equity  
            total_pnl_pct = (total_pnl / initial_equity * 100) if initial_equity > 0 else 0.0
            
            return {
                'daily_pnl': daily_pnl,
                'daily_pnl_pct': daily_pnl_pct,
                'total_pnl': total_pnl,
                'total_pnl_pct': total_pnl_pct,
                'current_equity': current_equity,
                'last_equity': last_equity,
                'initial_equity': initial_equity
            }
                
        except Exception as e:
            logger.error(f"Daily summary calculation failed: {e}")
            return {
                'daily_pnl': 0.0,
                'daily_pnl_pct': 0.0,
                'total_pnl': 0.0,
                'total_pnl_pct': 0.0,
                'current_equity': 0.0,
                'error': str(e)
            }
            
    async def get_positions_summary(self) -> Dict:
        """Get current positions with real P&L from Alpaca"""
        try:
            positions = await self.gateway.get_all_positions()
            position_summary = []
            
            total_market_value = 0.0
            total_unrealized_pnl = 0.0
            
            for position in positions:
                if float(position.qty) != 0:
                    market_value = float(position.market_value)
                    unrealized_pnl = float(position.unrealized_pl)
                    unrealized_pnl_pct = float(position.unrealized_plpc) * 100
                    
                    position_summary.append({
                        'symbol': position.symbol,
                        'quantity': float(position.qty),
                        'market_value': market_value,
                        'unrealized_pnl': unrealized_pnl,
                        'unrealized_pnl_pct': unrealized_pnl_pct,
                        'avg_entry_price': float(position.avg_entry_price)
                    })
                    
                    total_market_value += market_value
                    total_unrealized_pnl += unrealized_pnl
            
            return {
                'positions': position_summary,
                'total_positions': len(position_summary),
                'total_market_value': total_market_value,
                'total_unrealized_pnl': total_unrealized_pnl
            }
            
        except Exception as e:
            logger.error(f"Positions summary failed: {e}")
            return {'error': str(e), 'positions': []}
    
    async def generate_final_report(self) -> Dict:
        """Generate comprehensive final performance report using REAL data"""
        try:
            # Get final performance summary
            daily_summary = await self.get_daily_summary()
            positions_summary = await self.get_positions_summary()
            
            # Calculate session performance
            session_pnl = 0.0
            session_pnl_pct = 0.0
            
            if (self.session_start_value and 
                'current_equity' in daily_summary and 
                daily_summary['current_equity'] > 0):
                session_pnl = daily_summary['current_equity'] - self.session_start_value
                session_pnl_pct = (session_pnl / self.session_start_value) * 100
            
            return {
                'report_timestamp': datetime.now().isoformat(),
                'session_start_time': self.session_start_time.isoformat() if self.session_start_time else None,
                'session_start_value': self.session_start_value,
                'initial_account_value': self.initial_value,
                'current_equity': daily_summary.get('current_equity', 0.0),
                'daily_pnl': daily_summary.get('daily_pnl', 0.0),
                'daily_pnl_pct': daily_summary.get('daily_pnl_pct', 0.0),
                'total_pnl': daily_summary.get('total_pnl', 0.0),
                'total_pnl_pct': daily_summary.get('total_pnl_pct', 0.0),
                'session_pnl': session_pnl,
                'session_pnl_pct': session_pnl_pct,
                'positions_count': positions_summary.get('total_positions', 0),
                'total_position_value': positions_summary.get('total_market_value', 0.0),
                'total_unrealized_pnl': positions_summary.get('total_unrealized_pnl', 0.0),
                'data_source': 'Alpaca API (Real Data)'
            }
            
        except Exception as e:
            logger.error(f"Final report generation failed: {e}")
            return {
                'error': str(e),
                'report_timestamp': datetime.now().isoformat(),
                'data_source': 'Error - Could not retrieve real data'
            }