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
        """Load initial value from file or set it for first time with smart defaults"""
        try:
            initial_value_file = "initial_account_value.json"
            
            if os.path.exists(initial_value_file):
                with open(initial_value_file, 'r') as f:
                    data = json.load(f)
                    loaded_value = data['initial_value']
                    
                    # VALIDATION: Check if the loaded initial value makes sense
                    # If the difference is more than 1000%, something is wrong
                    if loaded_value > 0:
                        current_pct_change = abs((current_value - loaded_value) / loaded_value) * 100
                        if current_pct_change > 1000:  # More than 1000% change
                            logger.warning(f"⚠️ SUSPICIOUS INITIAL VALUE DETECTED!")
                            logger.warning(f"   Loaded initial value: ${loaded_value:,.2f}")
                            logger.warning(f"   Current value: ${current_value:,.2f}")
                            logger.warning(f"   Calculated change: {current_pct_change:.1f}%")
                            logger.warning(f"   This suggests the initial value may be incorrect")
                            
                            # Ask user to confirm or reset
                            logger.warning(f"   Consider using reset_initial_value() method to fix this")
                            
                    return loaded_value
            else:
                # First time - use smart defaults based on current account value
                logger.info(f"📊 First time setup - establishing initial account value")
                
                # SMART DEFAULT: If account is substantial (>$10K), use current value
                # If account is small (<$10K), this might be a test account
                if current_value >= 10000:
                    logger.info(f"📊 Large account detected (${current_value:,.2f}) - using as initial value")
                    logger.info(f"   This assumes you want to track performance from now forward")
                    logger.info(f"   If you want to track from a different baseline, use reset_initial_value()")
                else:
                    logger.info(f"📊 Small account detected (${current_value:,.2f}) - using as initial value")
                    logger.info(f"   This appears to be a test/training account")
                
                # Save current value as initial
                data = {
                    'initial_value': current_value,
                    'date_started': datetime.now().isoformat(),
                    'setup_type': 'first_time_auto_detection',
                    'account_size_category': 'large' if current_value >= 10000 else 'small'
                }
                with open(initial_value_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"📊 Initial value set to: ${current_value:,.2f}")
                return current_value
                
        except Exception as e:
            logger.warning(f"⚠️ Could not load initial value, using current: {e}")
            return current_value
    
    def reset_initial_value(self, new_initial_value: float):
        """Manually reset the initial account value (useful for fixing incorrect values)"""
        try:
            initial_value_file = "initial_account_value.json"
            
            # Update the stored initial value
            data = {
                'initial_value': new_initial_value,
                'date_started': datetime.now().isoformat(),
                'reset_reason': 'Manual reset by user'
            }
            
            with open(initial_value_file, 'w') as f:
                json.dump(data, f)
            
            # Update the current instance
            self.initial_value = new_initial_value
            
            logger.info(f"📊 Initial account value reset to: ${new_initial_value:,.2f}")
            logger.info(f"   Previous value was: ${self.initial_value:,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to reset initial value: {e}")
            return False
        
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
            # Try to get final performance summary, but use cached data if API gateway is closed
            try:
                daily_summary = await self.get_daily_summary()
            except Exception as e:
                logger.warning(f"⚠️ Could not get fresh data for final report, using cached: {e}")
                daily_summary = self.performance_cache.copy() if self.performance_cache else {
                    'current_equity': self.session_start_value or 2000,
                    'daily_pnl': 0.0,
                    'daily_pnl_pct': 0.0,
                    'total_pnl': 0.0,
                    'total_pnl_pct': 0.0
                }
            
            try:
                positions_summary = await self.get_positions_summary()
            except Exception as e:
                logger.warning(f"⚠️ Could not get position data for final report: {e}")
                positions_summary = {
                    'total_positions': 0,
                    'total_position_value': 0.0,
                    'total_unrealized_pnl': 0.0
                }
            
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

    async def suggest_initial_value(self) -> Dict:
        """
        Suggest better initial account value based on Alpaca account data
        This helps users choose the right baseline for performance tracking
        """
        try:
            suggestions = {
                'current_value': 0.0,
                'suggestions': [],
                'recommended': None,
                'explanation': ''
            }
            
            # Get current account data
            account = await self.gateway.get_account_safe()
            if not account:
                return {'error': 'Cannot access Alpaca account data'}
            
            current_equity = float(account.equity)
            suggestions['current_value'] = current_equity
            
            # Option 1: Track from now (current value)
            suggestions['suggestions'].append({
                'value': current_equity,
                'label': 'Track from now',
                'description': f'Start performance tracking from current value (${current_equity:,.2f})',
                'pros': ['Simple', 'No historical data needed', 'Clean baseline'],
                'cons': ['Loses historical performance', 'May not reflect true account growth']
            })
            
            # Option 2: Use a round number close to current value
            round_numbers = [1000, 5000, 10000, 25000, 50000, 100000]
            closest_round = min(round_numbers, key=lambda x: abs(x - current_equity))
            if abs(closest_round - current_equity) < current_equity * 0.1:  # Within 10%
                suggestions['suggestions'].append({
                    'value': closest_round,
                    'label': f'Round number baseline',
                    'description': f'Use ${closest_round:,} as baseline (close to current ${current_equity:,.0f})',
                    'pros': ['Clean number', 'Easy to remember', 'Good for tracking'],
                    'cons': ['May not be exact starting point']
                })
            
            # Option 3: Suggest based on account size
            if current_equity >= 50000:
                suggestions['suggestions'].append({
                    'value': 50000,
                    'label': 'Standard baseline',
                    'description': 'Use $50,000 as baseline (common starting point)',
                    'pros': ['Standard reference point', 'Easy to compare with others'],
                    'cons': ['May not reflect your actual starting point']
                })
            elif current_equity >= 25000:
                suggestions['suggestions'].append({
                    'value': 25000,
                    'label': 'Conservative baseline',
                    'description': 'Use $25,000 as baseline (conservative estimate)',
                    'pros': ['Conservative', 'Good for risk management'],
                    'cons': ['May overstate performance']
                })
            
            # Recommend the best option
            if suggestions['suggestions']:
                # Prefer current value for first-time users
                recommendations = [s for s in suggestions['suggestions'] if s['label'] == 'Track from now']
                if recommendations:
                    suggestions['recommended'] = recommendations[0]
                    suggestions['explanation'] = 'Recommended for first-time system users - tracks performance from now forward'
                else:
                    suggestions['recommended'] = suggestions['suggestions'][0]
                    suggestions['explanation'] = 'Best available option based on your account size'
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to suggest initial value: {e}")
            return {'error': str(e)}
    
    async def auto_setup_initial_value(self) -> bool:
        """
        Automatically set up initial value with user guidance
        This is the smart way to handle first-time setup
        """
        try:
            logger.info("🤖 Smart Initial Value Setup")
            logger.info("=" * 50)
            
            # Get suggestions
            suggestions = await self.suggest_initial_value()
            if 'error' in suggestions:
                logger.error(f"❌ Could not get suggestions: {suggestions['error']}")
                return False
            
            current_value = suggestions['current_value']
            logger.info(f"📊 Current Account Value: ${current_value:,.2f}")
            logger.info("")
            
            # Show options
            logger.info("🎯 Available Initial Value Options:")
            for i, suggestion in enumerate(suggestions['suggestions'], 1):
                logger.info(f"   {i}. {suggestion['label']}")
                logger.info(f"      Value: ${suggestion['value']:,.2f}")
                logger.info(f"      {suggestion['description']}")
                logger.info(f"      Pros: {', '.join(suggestion['pros'])}")
                logger.info(f"      Cons: {', '.join(suggestion['cons'])}")
                logger.info("")
            
            # Show recommendation
            if suggestions['recommended']:
                logger.info(f"💡 RECOMMENDED: {suggestions['recommended']['label']}")
                logger.info(f"   {suggestions['recommended']['description']}")
                logger.info(f"   {suggestions['explanation']}")
                logger.info("")
            
            # Auto-select recommended option
            if suggestions['recommended']:
                recommended_value = suggestions['recommended']['value']
                logger.info(f"🤖 Auto-selecting recommended option: ${recommended_value:,.2f}")
                
                success = self.reset_initial_value(recommended_value)
                if success:
                    logger.info(f"✅ Initial value automatically set to ${recommended_value:,.2f}")
                    logger.info(f"   You can change this later using reset_initial_value() if needed")
                    return True
                else:
                    logger.error(f"❌ Failed to auto-set initial value")
                    return False
            else:
                logger.warning("⚠️ No recommendations available - manual setup required")
                return False
                
        except Exception as e:
            logger.error(f"Auto setup failed: {e}")
            return False