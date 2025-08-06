# -*- coding: utf-8 -*-
"""
Main trading application with intelligent funnel and AI enhancement
Complete system orchestration for market-wide opportunity discovery
"""

import asyncio
import logging
import signal
import sys
import os
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
import json

# Load environment variables from .env file
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Import all system modules
from config import *
from intelligent_funnel import IntelligentMarketFunnel, MarketOpportunity
from ai_market_intelligence import EnhancedAIAssistant, MarketIntelligence
from enhanced_momentum_strategy import EventDrivenMomentumStrategy, TradingSignal
from corporate_actions_filter import CorporateActionsFilter
from api_gateway import ResilientAlpacaGateway
from risk_manager import ConservativeRiskManager
from order_executor import SimpleTradeExecutor
from market_status_manager import MarketStatusManager
from performance_tracker import PerformanceTracker
from supplemental_data_provider import SupplementalDataProvider
from alerter import CriticalAlerter
from pdt_manager import PDTManager
from gap_risk_manager import GapRiskManager

class IntelligentTradingSystem:
    """
    Complete intelligent trading system with market-wide discovery
    Integrates all components for systematic algorithmic trading
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.running = False
        self.system_initialized = False
        
        # Core system components
        self.gateway = ResilientAlpacaGateway()
        self.supplemental_data = SupplementalDataProvider()
        self.market_status = MarketStatusManager(self.gateway.trading_client)
        self.ai_assistant = EnhancedAIAssistant()
        self.strategy_engine = EventDrivenMomentumStrategy()
        self.market_funnel = IntelligentMarketFunnel(
            self.gateway, 
            self.ai_assistant, 
            self.supplemental_data, 
            self.strategy_engine
        )
        self.risk_manager = ConservativeRiskManager()
        self.order_executor = SimpleTradeExecutor(self.gateway, self.risk_manager)
        # Note: PDT manager will be linked after initialization
        self.performance_tracker = PerformanceTracker()
        self.corporate_actions_filter = CorporateActionsFilter()  # CRITICAL: Corporate actions protection
        self.alerter = CriticalAlerter()  # CRITICAL: Emergency alerting system
        self.pdt_manager = PDTManager()  # CRITICAL: PDT rule compliance
        self.gap_risk_manager = GapRiskManager()  # CRITICAL: Extended hours gap protection
        
        # System state
        self.current_intelligence: Optional[MarketIntelligence] = None
        self.active_opportunities: List[MarketOpportunity] = []
        self.last_intelligence_update = None
        self.last_opportunity_scan = None
        
        # Performance tracking
        self.session_stats = {
            'opportunities_discovered': 0,
            'signals_generated': 0,
            'trades_executed': 0,
            'api_calls_made': 0,
            'system_uptime_start': datetime.now()
        }
        
    def _setup_logging(self):
        """Setup comprehensive structured logging"""
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOGGING_CONFIG['log_file']),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        
        # Add custom filters for different log categories
        if LOGGING_CONFIG['structured_logging']:
            # Add structured logging enhancements here
            pass
            
        return logger
        
    async def initialize_system(self) -> bool:
        """Comprehensive system initialization with validation"""
        try:
            self.logger.info("🚀 Initializing Intelligent Trading System...")
            
            # Validate configuration
            validate_configuration()
            self.logger.info("✅ Configuration validated")
            
            # Initialize core components
            if not await self.gateway.initialize():
                self.logger.error("❌ Gateway initialization failed")
                return False
            self.logger.info("✅ API Gateway connected")
            
            # Initialize AI assistant
            try:
                await self.ai_assistant.initialize()
                self.logger.info("✅ AI Assistant online")
            except Exception as ai_init_error:
                self.logger.warning(f"⚠️ 🚨 AI ASSISTANT INITIALIZATION FAILURE 🚨")
                self.logger.warning(f"⚠️ Error: {ai_init_error}")
                self.logger.warning(f"⚠️ System will continue with degraded AI capabilities")
                self.logger.warning(f"⚠️ Check Ollama service and model availability")
            
            # Initialize supplemental data provider
            await self.supplemental_data.initialize()
            self.logger.info("✅ Supplemental Data Provider online")
            
            # Validate account and trading permissions
            account = await self.gateway.get_account_safe()
            if not account:
                self.logger.error("❌ Cannot access account")
                return False
                
            account_value = float(account.equity)
            self.logger.info(f"💰 Account Value: ${account_value:,.2f}")
            
            if account_value < 100:
                self.logger.error("❌ Insufficient account balance")
                return False
                
            # Initialize risk manager
            await self.risk_manager.initialize(account_value)
            self.logger.info("✅ Risk Manager initialized")
            
            # Initialize performance tracker
            await self.performance_tracker.initialize(account_value)
            self.logger.info("✅ Performance Tracker ready")
            
            # Initialize PDT manager
            await self.pdt_manager.initialize(self.gateway)
            self.order_executor.pdt_manager = self.pdt_manager  # Link PDT manager to executor
            self.logger.info("✅ PDT Manager ready")
            
            # STARTUP SAFETY CHECK: Scan for naked positions without stop protection
            await self._startup_position_safety_check()
            
            # POSITION RECONCILIATION: Verify our understanding matches broker reality
            await self._startup_position_reconciliation()
            
            # Reset PDT blocks for new trading day
            self.gateway.reset_pdt_blocks()
            
            # Validate market access
            should_trade, reason = await self.market_status.should_start_trading()
            if not should_trade and "closed" not in reason.lower():
                self.logger.warning(f"⚠️ Market status: {reason}")
                
            # Generate initial market intelligence
            try:
                market_data = await self._collect_initial_market_data()
                self.current_intelligence = await self.ai_assistant.generate_daily_market_intelligence(market_data)
                self.logger.info(f"🧠 Market Intelligence: {self.current_intelligence.market_regime} regime")
            except Exception as intelligence_error:
                self.logger.warning(f"⚠️ 🚨 INITIAL MARKET INTELLIGENCE FAILURE 🚨")
                self.logger.warning(f"⚠️ Error: {intelligence_error}")
                self.logger.warning(f"⚠️ System will attempt to generate intelligence later")
                self.current_intelligence = None
            
            self.system_initialized = True
            self.logger.info("🎯 SYSTEM READY FOR INTELLIGENT TRADING")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")
            return False
    
    async def _startup_position_safety_check(self):
        """Check for naked positions without stop protection at system startup"""
        try:
            self.logger.info("🔍 Performing startup position safety check...")
            
            # Get all current positions
            positions = await self.gateway.get_all_positions()
            active_positions = [pos for pos in positions if float(pos.qty) != 0]
            
            if not active_positions:
                self.logger.info("✅ No active positions found at startup")
                return
            
            # Get all open orders to check for protective stops
            open_orders = await self.gateway.get_orders('open')
            
            naked_positions = []
            
            for position in active_positions:
                symbol = position.symbol
                qty = float(position.qty)
                position_side = 'long' if qty > 0 else 'short'
                
                # Look for protective stop orders for this position
                has_stop_protection = False
                
                for order in open_orders:
                    if (hasattr(order, 'symbol') and order.symbol == symbol and 
                        hasattr(order, 'type') and 'stop' in order.type.lower()):
                        has_stop_protection = True
                        break
                
                if not has_stop_protection:
                    naked_positions.append({
                        'symbol': symbol,
                        'qty': qty,
                        'side': position_side,
                        'market_value': float(position.market_value),
                        'unrealized_pl': float(position.unrealized_pl),
                        'unrealized_pct': float(position.unrealized_plpc) * 100
                    })
            
            if naked_positions:
                self.logger.critical(f"🚨 STARTUP ALERT: {len(naked_positions)} positions without stop protection found")
                
                for pos in naked_positions:
                    self.logger.critical(f"   {pos['symbol']}: {pos['qty']} shares, "
                                       f"{pos['unrealized_pct']:.1f}% P&L, ${pos['market_value']:,.2f} value")
                
                # Send critical alert
                naked_symbols = [pos['symbol'] for pos in naked_positions]
                await self.alerter.send_system_startup_alert(naked_symbols)
                
                # Optionally create emergency stops for naked positions
                await self._create_emergency_stops_for_naked_positions(naked_positions)
            else:
                self.logger.info("✅ All positions have stop protection")
                
        except Exception as e:
            self.logger.error(f"Startup position safety check failed: {e}")
            await self.alerter.send_critical_alert(
                "Startup position safety check failed",
                f"Unable to verify position safety at startup: {e}"
            )
    
    async def _create_emergency_stops_for_naked_positions(self, naked_positions: List[Dict]):
        """Create emergency stop losses for positions without protection"""
        try:
            self.logger.info("🆘 Creating emergency stops for naked positions...")
            
            stops_created = 0
            
            for pos in naked_positions:
                try:
                    symbol = pos['symbol']
                    qty = abs(pos['qty'])
                    current_price = pos['market_value'] / abs(pos['qty'])  # Approximate current price
                    
                    # Calculate emergency stop price (8% below current for long positions)
                    if pos['side'] == 'long':
                        stop_price = current_price * 0.92  # 8% stop loss
                        side = 'sell'
                    else:
                        stop_price = current_price * 1.08  # 8% stop loss for short
                        side = 'buy'
                    
                    # Create emergency stop order
                    emergency_stop_data = {
                        'symbol': symbol,
                        'qty': str(int(qty)),
                        'side': side,
                        'type': 'stop',
                        'stop_price': str(round(stop_price, 2)),
                        'time_in_force': 'day'
                    }
                    
                    stop_response = await self.gateway.submit_order(emergency_stop_data)
                    
                    if stop_response:
                        self.logger.critical(f"✅ Emergency stop created: {symbol} @ ${stop_price:.2f}")
                        stops_created += 1
                    else:
                        self.logger.error(f"❌ Failed to create emergency stop for {symbol}")
                        
                except Exception as stop_error:
                    self.logger.error(f"Failed to create emergency stop for {pos['symbol']}: {stop_error}")
            
            if stops_created > 0:
                self.logger.info(f"✅ Created {stops_created} emergency stop orders")
            else:
                self.logger.warning("⚠️ No emergency stops could be created")
                
        except Exception as e:
            self.logger.error(f"Emergency stop creation failed: {e}")
    
    async def _startup_position_reconciliation(self):
        """Reconcile our position understanding with actual broker positions"""
        try:
            self.logger.info("🔄 Performing startup position reconciliation...")
            
            # Get actual positions from broker
            broker_positions = await self.gateway.get_all_positions()
            broker_symbols = {pos.symbol: float(pos.qty) for pos in broker_positions if float(pos.qty) != 0}
            
            # Check if we have any internal position tracking (would be implemented with persistent storage)
            # For now, just validate broker positions make sense
            
            discrepancies = []
            suspicious_positions = []
            
            for symbol, qty in broker_symbols.items():
                # Check for suspicious position sizes
                account = await self.gateway.get_account_safe()
                if account:
                    account_value = float(account.equity)
                    try:
                        # Get current price to estimate position value
                        quote = await self.gateway.get_latest_quote(symbol)
                        if quote:
                            current_price = float(quote.get('ask_price', 0)) or float(quote.get('bid_price', 0))
                            if current_price > 0:
                                position_value = abs(qty) * current_price
                                position_pct = (position_value / account_value) * 100
                                
                                # Flag positions larger than 10% of account
                                if position_pct > 10:
                                    suspicious_positions.append({
                                        'symbol': symbol,
                                        'qty': qty,
                                        'value': position_value,
                                        'percentage': position_pct
                                    })
                    except Exception as price_error:
                        self.logger.debug(f"Could not get price for {symbol}: {price_error}")
            
            if suspicious_positions:
                self.logger.warning(f"⚠️ LARGE POSITIONS DETECTED: {len(suspicious_positions)} positions > 10% of account")
                for pos in suspicious_positions:
                    self.logger.warning(f"   {pos['symbol']}: {pos['qty']} shares, ${pos['value']:,.2f} ({pos['percentage']:.1f}%)")
                
                await self.alerter.send_critical_alert(
                    "Large positions detected at startup",
                    f"Found {len(suspicious_positions)} positions > 10% of account: {', '.join([p['symbol'] for p in suspicious_positions])}"
                )
            
            if broker_symbols:
                self.logger.info(f"✅ Position reconciliation complete: {len(broker_symbols)} active positions")
                for symbol, qty in broker_symbols.items():
                    self.logger.info(f"   {symbol}: {qty} shares")
            else:
                self.logger.info("✅ Position reconciliation complete: No active positions")
                
        except Exception as e:
            self.logger.error(f"Position reconciliation failed: {e}")
            await self.alerter.send_critical_alert(
                "Position reconciliation failed at startup",
                f"Unable to verify position accuracy: {e}"
            )
            
    async def run_intelligent_trading_loop(self):
        """Main intelligent trading loop with market-wide discovery"""
        self.running = True
        self.logger.info("🔥 STARTING INTELLIGENT TRADING ENGINE")
        
        try:
            # Wait for market open if needed, but check for shutdown signals
            while self.running:
                should_trade, reason = await self.market_status.should_start_trading()
                should_monitor_extended = self.market_status.should_monitor_positions_extended_hours()
                
                if should_trade:
                    break
                elif should_monitor_extended:
                    self.logger.info(f"⏰ {reason} - but monitoring positions for gap risk")
                    # Run extended hours monitoring loop
                    await self._extended_hours_monitoring_loop()
                    continue
                elif not self.running:
                    self.logger.info("Shutdown requested during market wait")
                    return
                else:
                    self.logger.info(f"⏰ {reason}")
                    # Wait 60 seconds but check for shutdown every 5 seconds
                    for _ in range(12):  # 12 * 5 = 60 seconds
                        if not self.running:
                            self.logger.info("Shutdown requested during market wait")
                            return
                        await asyncio.sleep(5)
            
            loop_count = 0
            while self.running:
                loop_start = datetime.now()
                loop_count += 1
                
                # === MARKET INTELLIGENCE UPDATE ===
                try:
                    await self._update_market_intelligence()
                except Exception as e:
                    self.logger.warning(f"⚠️ 🚨 MARKET INTELLIGENCE SYSTEM FAILURE 🚨")
                    self.logger.warning(f"⚠️ Market intelligence update failed: {e}")
                    self.logger.warning(f"⚠️ Trading decisions will operate with degraded market context")
                    self.logger.warning(f"⚠️ Consider checking AI system health and data connectivity")
                
                # === CORPORATE ACTIONS CHECK (CRITICAL) ===
                try:
                    await self._check_corporate_actions()
                except Exception as e:
                    self.logger.error(f"❌ Corporate actions check error: {e}")
                
                # === OPPORTUNITY DISCOVERY ===
                try:
                    await self._discover_market_opportunities()
                except Exception as e:
                    self.logger.error(f"❌ Opportunity discovery error: {e}")
                
                # === TIERED ANALYSIS TEST (First loop only) ===
                if loop_count == 1:  # Run on first iteration
                    try:
                        self.logger.info("🧪 Running Tiered Analysis Test with Hot Stocks...")
                        await self.test_tiered_analysis_with_hot_stocks()
                    except Exception as e:
                        self.logger.error(f"❌ Tiered analysis test error: {e}")
                
                # === SIGNAL GENERATION & VALIDATION ===
                try:
                    await self._generate_and_validate_signals()
                except Exception as e:
                    self.logger.error(f"❌ Signal generation error: {e}")
                
                # === POSITION MANAGEMENT (CRITICAL - MUST NOT FAIL) ===
                try:
                    await self._manage_existing_positions()
                except Exception as e:
                    self.logger.error(f"❌ CRITICAL: Position management error: {e}")
                
                # === STOP LOSS & TRAILING STOPS (CRITICAL) ===
                try:
                    await self.order_executor.check_stop_losses()
                    await self.order_executor.update_trailing_stops()
                except Exception as e:
                    self.logger.error(f"❌ CRITICAL: Stop loss management error: {e}")
                
                # === RISK MONITORING ===
                try:
                    await self._monitor_system_risk()
                except Exception as e:
                    self.logger.error(f"❌ Risk monitoring error: {e}")
                
                # === PERFORMANCE TRACKING ===
                try:
                    await self._update_performance_metrics()
                except Exception as e:
                    self.logger.error(f"❌ Performance tracking error: {e}")
                
                # === GAP RISK MONITORING (Record closes before 4 PM) ===
                try:
                    await self._record_market_close_positions()
                except Exception as e:
                    self.logger.error(f"❌ Gap risk recording error: {e}")
                
                # === SYSTEM HEALTH CHECK ===
                try:
                    await self._system_health_check()
                except Exception as e:
                    self.logger.error(f"❌ Health check error: {e}")
                
                # === PDT STATUS MONITORING ===
                try:
                    await self._monitor_pdt_status()
                except Exception as e:
                    self.logger.error(f"❌ PDT monitoring error: {e}")
                    
                # === ADAPTIVE LOOP TIMING ===
                execution_time = (datetime.now() - loop_start).total_seconds()
                
                # Adaptive sleep based on market conditions and discovery frequency
                if self.current_intelligence and self.current_intelligence.volatility_environment == "HIGH":
                    sleep_time = max(30, 60 - execution_time)  # Faster in high volatility
                else:
                    sleep_time = max(60, 120 - execution_time)  # Standard timing
                    
                self.logger.debug(f"⏱️ Loop completed in {execution_time:.2f}s, sleeping {sleep_time:.0f}s")
                
                # Sleep in smaller chunks to be responsive to shutdown signals
                sleep_chunks = int(sleep_time / 5)  # Sleep in 5-second chunks
                for _ in range(sleep_chunks):
                    if not self.running:
                        self.logger.info("Shutdown requested during sleep")
                        return
                    await asyncio.sleep(5)
                    
                # Handle remaining sleep time
                remaining_sleep = sleep_time % 5
                if remaining_sleep > 0 and self.running:
                    await asyncio.sleep(remaining_sleep)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Graceful shutdown requested")
        except asyncio.CancelledError:
            self.logger.info("🛑 Shutdown signal received")
        except Exception as e:
            self.logger.critical(f"💥 CRITICAL ERROR: {e}")
            await self._emergency_shutdown("Critical system error")
        finally:
            await self._graceful_shutdown()
            
    async def _update_market_intelligence(self):
        """Update market intelligence and regime analysis"""
        try:
            # Check if intelligence needs refresh
            if (not self.last_intelligence_update or
                (datetime.now() - self.last_intelligence_update).total_seconds() > 
                AI_CONFIG['market_regime_analysis_frequency'] * 60):
                
                self.logger.debug("🧠 Updating market intelligence...")
                
                # Collect fresh market data
                market_data = await self._collect_current_market_data()
                
                # Generate new intelligence
                self.current_intelligence = await self.ai_assistant.generate_daily_market_intelligence(market_data)
                self.last_intelligence_update = datetime.now()
                
                self.logger.info(f"📊 Market Intelligence Updated: {self.current_intelligence.market_regime} "
                               f"({self.current_intelligence.confidence:.0%} confidence)")
                               
        except Exception as e:
            self.logger.warning(f"⚠️ 🚨 CRITICAL: Market Intelligence Update Failed 🚨")
            self.logger.warning(f"⚠️ Error: {e}")
            self.logger.warning(f"⚠️ System will continue with stale or fallback intelligence")
            self.logger.warning(f"⚠️ Trading performance may be degraded until resolved")
    
    async def _check_corporate_actions(self):
        """Check for corporate actions that could affect trading"""
        try:
            # Get current watchlist symbols for checking
            watchlist_symbols = []
            
            # Add symbols from active opportunities
            for opportunity in self.active_opportunities:
                if hasattr(opportunity, 'symbol'):
                    watchlist_symbols.append(opportunity.symbol)
            
            # Add symbols from current positions
            try:
                positions = await self.gateway.get_all_positions()
                for position in positions:
                    if float(position.qty) != 0:
                        watchlist_symbols.append(position.symbol)
            except Exception as e:
                self.logger.error(f"Error getting positions for corporate actions check: {e}")
            
            # Remove duplicates
            watchlist_symbols = list(set(watchlist_symbols))
            
            if not watchlist_symbols:
                self.logger.debug("No symbols to check for corporate actions")
                return
            
            # Check for corporate actions (runs only on first check of the day)
            current_date = datetime.now().date()
            if not hasattr(self, '_last_corporate_check_date') or self._last_corporate_check_date != current_date:
                blocked_symbols = await self.corporate_actions_filter.check_pre_market_corporate_actions(watchlist_symbols)
                
                if blocked_symbols:
                    self.logger.warning(f"🚫 Corporate actions detected - {len(blocked_symbols)} symbols blocked")
                    
                    # Remove blocked symbols from active opportunities
                    self.active_opportunities = [
                        opp for opp in self.active_opportunities 
                        if not hasattr(opp, 'symbol') or opp.symbol not in blocked_symbols
                    ]
                
                # Mark that we've done today's corporate actions check
                self._last_corporate_check_date = current_date
            
            # Always check if individual symbols are blocked before trading
            blocked_info = self.corporate_actions_filter.get_blocked_symbols_info()
            if blocked_info['total_blocked'] > 0:
                self.logger.info(f"📊 Corporate actions status: {blocked_info['total_blocked']} symbols blocked")
                
        except Exception as e:
            self.logger.error(f"Corporate actions check failed: {e}")
            
    async def _discover_market_opportunities(self):
        """Execute intelligent funnel for opportunity discovery"""
        try:
            # Check if opportunity scan is needed
            if (not self.last_opportunity_scan or
                (datetime.now() - self.last_opportunity_scan).total_seconds() > 
                FUNNEL_CONFIG['broad_scan_frequency_minutes'] * 60):
                
                self.logger.debug("🔍 Executing opportunity discovery...")
                
                # Run intelligent funnel
                new_opportunities = await self.market_funnel.execute_intelligent_funnel()
                
                if new_opportunities:
                    self.active_opportunities = new_opportunities
                    self.session_stats['opportunities_discovered'] += len(new_opportunities)
                    
                    # Log top opportunities
                    self.logger.info("🎯 TOP OPPORTUNITIES:")
                    for i, opp in enumerate(new_opportunities[:5], 1):
                        self.logger.info(f"   {i}. {opp.symbol}: {opp.opportunity_score:.2f} "
                                       f"({opp.discovery_source}) - {opp.primary_catalyst}")
                                       
                self.last_opportunity_scan = datetime.now()
                
        except Exception as e:
            self.logger.error(f"Opportunity discovery failed: {e}")
            
    async def _generate_and_validate_signals(self):
        """Generate trading signals and validate with AI"""
        try:
            if not self.active_opportunities:
                self.logger.debug("No active opportunities for signal generation")
                return
                
            self.logger.info(f"🔍 Analyzing {len(self.active_opportunities)} opportunities for trade signals...")
                
            signals_generated = 0
            
            # Get existing positions to prevent duplicate trades
            existing_positions = await self.gateway.get_all_positions()
            existing_symbols = {pos.symbol for pos in existing_positions if float(pos.qty) != 0}
            
            if existing_symbols:
                self.logger.info(f"🔒 Existing positions: {', '.join(existing_symbols)} - will skip these symbols")
            
            for opportunity in self.active_opportunities[:10]:  # Process top 10
                try:
                    # SKIP if we already have a position in this symbol
                    if opportunity.symbol in existing_symbols:
                        self.logger.info(f"⏭️ SKIPPING {opportunity.symbol}: Already have position")
                        continue
                    
                    # CRITICAL: SKIP if symbol is blocked due to corporate actions
                    if self.corporate_actions_filter.is_symbol_blocked(opportunity.symbol):
                        self.logger.warning(f"🚫 SKIPPING {opportunity.symbol}: Blocked due to corporate actions")
                        continue
                    
                    # CRITICAL: SKIP if symbol is PDT-blocked to prevent repeated failed attempts
                    if self.gateway.is_symbol_pdt_blocked(opportunity.symbol):
                        self.logger.warning(f"🚫 SKIPPING {opportunity.symbol}: PDT-blocked from previous violation")
                        continue
                        
                    # COMPREHENSIVE DATA ACQUISITION STRATEGY WITH FREE SUPPLEMENTS
                    bars = None
                    data_sources_tried = []
                    quote_data = None
                    
                    # Strategy 1: Try Alpaca first (limited on free tier)
                    from datetime import datetime, timedelta
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    
                    bars = await self.gateway.get_bars(
                        opportunity.symbol, '1Day', limit=50, 
                        start=start_date, end=end_date
                    )
                    data_sources_tried.append(f"Alpaca-daily ({len(bars) if bars else 0} bars)")
                    
                    # Strategy 2: If Alpaca fails, use FREE supplemental data sources
                    if not bars or len(bars) < 5:
                        self.logger.info(f"📊 Alpaca data insufficient for {opportunity.symbol}, trying free sources...")
                        
                        # Yahoo Finance + Alpha Vantage (FREE)
                        supplement_bars = await self.supplemental_data.get_historical_data(
                            opportunity.symbol, days=30, min_bars=10
                        )
                        
                        if supplement_bars and len(supplement_bars) > len(bars or []):
                            bars = supplement_bars
                            data_sources_tried.append(f"Free-sources ({len(bars)} bars)")
                            
                        # Get real-time quote from Yahoo Finance (FREE)
                        if not quote_data:
                            quote_data = await self.supplemental_data.get_real_time_quote(opportunity.symbol)
                            if quote_data:
                                data_sources_tried.append("Yahoo-quote")
                    
                    # Strategy 3: Fallback to Alpaca intraday if free sources fail
                    if not bars or len(bars) < 5:
                        self.logger.info(f"📊 Free sources insufficient, trying Alpaca intraday...")
                        
                        # Try hourly data from Alpaca
                        bars_1h = await self.gateway.get_bars(opportunity.symbol, '1Hour', limit=50)
                        data_sources_tried.append(f"Alpaca-hourly ({len(bars_1h) if bars_1h else 0} bars)")
                        
                        if bars_1h and len(bars_1h) >= 6:  # Reduced requirement
                            # Convert hourly to daily equivalent
                            daily_equiv = self._aggregate_intraday_to_daily(bars_1h, hours_per_day=6)
                            if daily_equiv and len(daily_equiv) >= 2:
                                bars = daily_equiv
                                data_sources_tried.append(f"hourly-aggregated ({len(bars)} bars)")
                            else:
                                # Use raw hourly data if aggregation fails
                                bars = bars_1h[:20]  # Limit to prevent over-analysis
                                data_sources_tried.append(f"raw-hourly ({len(bars)} bars)")
                        elif bars_1h and len(bars_1h) >= 3:
                            # Use minimal hourly data
                            bars = bars_1h
                            data_sources_tried.append(f"minimal-hourly ({len(bars)} bars)")
                    
                    # Strategy 4: Get real-time quote from Alpaca if Yahoo failed
                    if not quote_data and bars and len(bars) > 0:
                        current_quote = await self.gateway.get_latest_quote(opportunity.symbol)
                        if current_quote:
                            quote_data = {
                                'current_price': float(current_quote.get('ask_price', 0)) or float(current_quote.get('bid_price', 0)),
                                'bid_ask_spread': abs(float(current_quote.get('ask_price', 0)) - float(current_quote.get('bid_price', 0))),
                                'timestamp': current_quote.get('timestamp', '')
                            }
                            data_sources_tried.append("Alpaca-quote")
                    
                    self.logger.info(f"📊 {opportunity.symbol} data acquisition: {' + '.join(data_sources_tried)}")
                    if not bars:
                        self.logger.info(f"📊 No bars data returned for {opportunity.symbol}")
                        continue
                    else:
                        self.logger.info(f"📊 Retrieved {len(bars)} bars for {opportunity.symbol}")
                        
                    # Generate technical signal with enhanced data context and market intelligence
                    technical_signal = await self.strategy_engine.analyze_symbol(
                        opportunity.symbol, bars, quote_data=quote_data, 
                        data_sources=data_sources_tried, market_intelligence=self.current_intelligence
                    )
                    
                    if technical_signal:
                        self.logger.info(f"📈 Technical signal generated for {opportunity.symbol}: {technical_signal.action}")
                        
                        # AI validation of signal against market context
                        try:
                            ai_evaluation = await self.ai_assistant.evaluate_opportunity_with_context(
                                opportunity, self.current_intelligence
                            )
                            
                            # Log AI evaluation results
                            self.logger.info(f"🧠 AI evaluation for {opportunity.symbol}: score={ai_evaluation.get('overall_score', 0):.2f}, "
                                           f"confidence={ai_evaluation.get('confidence', 0):.2f}, "
                                           f"recommendation={ai_evaluation.get('entry_recommendation', 'NONE')}")
                            
                        except Exception as ai_error:
                            self.logger.warning(f"⚠️ AI EVALUATION FAILURE for {opportunity.symbol}: {ai_error}")
                            self.logger.warning(f"⚠️ Using fallback evaluation for this opportunity")
                            ai_evaluation = {
                                'overall_score': 0.6,  # Neutral fallback score
                                'confidence': 0.5,     # Lower confidence
                                'entry_recommendation': 'PATIENT',
                                'reasoning': f'AI evaluation failed: {ai_error}'
                            }
                        
                        # Check AI confidence and recommendation
                        if (ai_evaluation.get('overall_score', 0) >= 0.7 and
                            ai_evaluation.get('entry_recommendation') in ['IMMEDIATE', 'PATIENT'] and
                            ai_evaluation.get('confidence', 0) >= AI_CONFIG['confidence_threshold']):
                            
                            # Execute trade
                            success = await self._execute_validated_signal(technical_signal, ai_evaluation, opportunity)
                            
                            if success:
                                signals_generated += 1
                                self.session_stats['signals_generated'] += 1
                                self.session_stats['trades_executed'] += 1
                                
                                self.logger.info(f"✅ TRADE EXECUTED: {opportunity.symbol} "
                                               f"(AI Score: {ai_evaluation['overall_score']:.2f}, "
                                               f"Expected: {ai_evaluation.get('expected_return_pct', 0):.1f}%)")
                        else:
                            # Determine if this is an AI failure vs. legitimate rejection
                            score = ai_evaluation.get('overall_score', 0)
                            confidence = ai_evaluation.get('confidence', 0)
                            reasoning = ai_evaluation.get('reasoning', 'No reasoning provided')
                            
                            if 'failed' in reasoning.lower() or 'error' in reasoning.lower():
                                self.logger.warning(f"⚠️ {opportunity.symbol}: AI SYSTEM FAILURE during evaluation")
                                self.logger.warning(f"⚠️ AI error details: {reasoning}")
                                self.logger.warning(f"⚠️ Opportunity skipped due to AI failure, not rejection")
                            else:
                                self.logger.info(f"⚠️ {opportunity.symbol}: AI validation failed - "
                                               f"score={score:.2f} (need ≥0.7), confidence={confidence:.2f} "
                                               f"(need ≥{AI_CONFIG['confidence_threshold']:.2f}), "
                                               f"recommendation={ai_evaluation.get('entry_recommendation', 'NONE')}")
                    else:
                        self.logger.info(f"📊 No technical signal for {opportunity.symbol}")
                        continue
                            
                except Exception as e:
                    self.logger.error(f"Signal processing failed for {opportunity.symbol}: {e}")
                    
            if signals_generated > 0:
                self.logger.info(f"📈 Generated {signals_generated} validated trading signals")
                
        except Exception as e:
            self.logger.error(f"Signal generation failed: {e}")
            
    async def _execute_validated_signal(self, signal: TradingSignal, ai_evaluation: Dict, 
                                      opportunity: MarketOpportunity) -> bool:
        """Execute trading signal with comprehensive validation"""
        try:
            # Final risk check
            account = await self.gateway.get_account_safe()
            if not account:
                return False
                
            # Calculate position size based on AI recommendation
            base_position_size = RISK_CONFIG['max_position_risk_pct'] / 100
            
            # Adjust size based on AI confidence and recommendation
            size_multiplier = {
                'FULL': 1.0,
                'REDUCED': 0.5,
                'MINIMAL': 0.25
            }.get(ai_evaluation.get('position_size_recommendation', 'REDUCED'), 0.5)
            
            adjusted_position_size = base_position_size * size_multiplier
            
            # Update signal with AI insights
            signal.stop_loss_price = signal.entry_price * (1 - RISK_CONFIG['stop_loss_pct'] / 100)
            signal.take_profit_price = signal.entry_price * (1 + ai_evaluation.get('expected_return_pct', 10) / 100)
            signal.confidence = ai_evaluation.get('confidence', signal.confidence)
            signal.reasoning = f"AI: {ai_evaluation.get('reasoning', 'No reasoning')}"
            
            # Execute trade
            success = await self.order_executor.execute_signal(signal)
            
            if success:
                # Log comprehensive trade details
                trade_log = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': signal.symbol,
                    'action': signal.action,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss_price,
                    'take_profit': signal.take_profit_price,
                    'position_size_pct': adjusted_position_size * 100,
                    'ai_score': ai_evaluation.get('overall_score'),
                    'ai_confidence': ai_evaluation.get('confidence'),
                    'expected_return': ai_evaluation.get('expected_return_pct'),
                    'market_regime': self.current_intelligence.market_regime,
                    'discovery_source': opportunity.discovery_source,
                    'opportunity_score': opportunity.opportunity_score
                }
                
                self.logger.info(f"📝 TRADE LOG: {json.dumps(trade_log, indent=2)}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Trade execution failed: {e}")
            return False
            
    async def _manage_existing_positions(self):
        """Comprehensive autonomous position management"""
        try:
            # Get all current positions
            positions = await self.gateway.get_all_positions()
            active_positions = [pos for pos in positions if float(pos.qty) != 0]
            
            if not active_positions:
                self.logger.debug("No active positions to manage")
                return
                
            self.logger.info(f"📊 Managing {len(active_positions)} active positions...")
            
            for position in active_positions:
                try:
                    await self._manage_individual_position(position)
                except Exception as e:
                    self.logger.error(f"Position management failed for {position.symbol}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Position management system failed: {e}")
            
    async def _manage_individual_position(self, position):
        """Manage individual position with autonomous decision making"""
        try:
            symbol = position.symbol
            qty = float(position.qty)
            current_value = float(position.market_value)
            unrealized_pl = float(position.unrealized_pl)
            unrealized_pct = float(position.unrealized_plpc) * 100
            avg_entry = float(position.avg_entry_price)
            
            # SWING TRADING ENFORCEMENT - Check minimum holding period
            # Find when this position was opened by checking executed trades
            position_entry_time = None
            for trade in self.order_executor.executed_trades:
                if trade['signal'].symbol == symbol and trade['status'] == 'EXECUTED':
                    position_entry_time = trade.get('entry_timestamp', trade.get('execution_time'))
                    break
            
            if position_entry_time:
                hours_held = (datetime.now() - position_entry_time).total_seconds() / 3600
                min_hold_hours = RISK_CONFIG['min_holding_period_hours']
                
                if hours_held < min_hold_hours:
                    self.logger.info(f"🕐 {symbol}: Swing trading hold - {hours_held:.1f}h/{min_hold_hours}h minimum")
                    return  # Skip position management - enforce swing trading
            else:
                # If we can't find entry time, assume it's been held long enough (existing position)
                self.logger.debug(f"📊 {symbol}: No entry time found, assuming swing trade eligible")
            
            self.logger.debug(f"📊 {symbol}: {qty} shares, {unrealized_pct:.1f}% P&L")
            
            # Get current market data for analysis
            bars = await self.gateway.get_bars(symbol, '1Day', limit=10)
            current_quote = await self.gateway.get_latest_quote(symbol)
            
            if not current_quote:
                self.logger.warning(f"No current quote for {symbol}, skipping management")
                return
                
            current_price = float(current_quote.get('ask_price', 0)) or float(current_quote.get('bid_price', 0))
            
            # Analyze position against current market intelligence
            position_analysis = await self._analyze_position_context(
                symbol, current_price, unrealized_pct, bars
            )
            
            # Make autonomous management decisions
            management_action = await self._determine_position_action(
                symbol, qty, unrealized_pct, current_price, avg_entry, position_analysis
            )
            
            # Execute management action
            if management_action['action'] != 'HOLD':
                await self._execute_position_management(position, management_action, current_price)
                
        except Exception as e:
            self.logger.error(f"Individual position management failed for {position.symbol}: {e}")
            
    async def _analyze_position_context(self, symbol: str, current_price: float, 
                                       unrealized_pct: float, bars: List) -> Dict:
        """Analyze position against current market context"""
        try:
            analysis = {
                'trend_strength': 'NEUTRAL',
                'momentum': 'NEUTRAL', 
                'volume_profile': 'NORMAL',
                'technical_outlook': 'NEUTRAL',
                'regime_alignment': True,
                'risk_level': 'MEDIUM'
            }
            
            if bars and len(bars) >= 3:
                # Simple trend analysis
                recent_prices = [float(bar.get('c', 0)) for bar in bars[-3:]]
                if len(recent_prices) == 3:
                    if recent_prices[2] > recent_prices[1] > recent_prices[0]:
                        analysis['trend_strength'] = 'STRONG_UP'
                    elif recent_prices[2] < recent_prices[1] < recent_prices[0]:
                        analysis['trend_strength'] = 'STRONG_DOWN'
                    elif recent_prices[2] > recent_prices[0]:
                        analysis['trend_strength'] = 'WEAK_UP'
                    else:
                        analysis['trend_strength'] = 'WEAK_DOWN'
                        
                # Volume analysis
                recent_volumes = [int(bar.get('v', 0)) for bar in bars[-3:]]
                if recent_volumes and len(recent_volumes) >= 2:
                    avg_volume = sum(recent_volumes[:-1]) / len(recent_volumes[:-1])
                    latest_volume = recent_volumes[-1]
                    if latest_volume > avg_volume * 1.5:
                        analysis['volume_profile'] = 'HIGH'
                    elif latest_volume < avg_volume * 0.7:
                        analysis['volume_profile'] = 'LOW'
                        
            # Market regime alignment check
            if self.current_intelligence:
                if (self.current_intelligence.market_regime in ['BEAR_TRENDING', 'VOLATILE_RANGE'] and 
                    unrealized_pct > 5):
                    analysis['regime_alignment'] = False
                    analysis['risk_level'] = 'HIGH'
                elif (self.current_intelligence.volatility_environment == 'HIGH' and 
                      abs(unrealized_pct) > 10):
                    analysis['risk_level'] = 'HIGH'
                    
            return analysis
            
        except Exception as e:
            self.logger.error(f"Position context analysis failed for {symbol}: {e}")
            return {'trend_strength': 'NEUTRAL', 'risk_level': 'HIGH'}
            
    async def _determine_position_action(self, symbol: str, qty: float, unrealized_pct: float,
                                        current_price: float, avg_entry: float, 
                                        analysis: Dict) -> Dict:
        """Determine autonomous position management action"""
        try:
            action = {
                'action': 'HOLD',
                'quantity': 0,
                'reason': 'No action needed',
                'urgency': 'LOW'
            }
            
            # === STOP LOSS TRIGGERS ===
            if unrealized_pct <= -8.0:  # Hard stop loss
                action = {
                    'action': 'SELL_ALL',
                    'quantity': abs(qty),
                    'reason': f'Stop loss triggered: {unrealized_pct:.1f}% loss',
                    'urgency': 'IMMEDIATE'
                }
                
            elif unrealized_pct <= -5.0 and analysis['trend_strength'] in ['STRONG_DOWN', 'WEAK_DOWN']:
                action = {
                    'action': 'SELL_HALF',
                    'quantity': abs(qty) / 2,
                    'reason': f'Trend deterioration with {unrealized_pct:.1f}% loss',
                    'urgency': 'HIGH'
                }
                
            # === PROFIT TAKING TRIGGERS ===
            elif unrealized_pct >= 20.0:  # Strong profits
                if analysis['trend_strength'] in ['STRONG_DOWN', 'WEAK_DOWN']:
                    action = {
                        'action': 'SELL_HALF',
                        'quantity': abs(qty) / 2,
                        'reason': f'Profit taking: {unrealized_pct:.1f}% gain with weakening trend',
                        'urgency': 'MEDIUM'
                    }
                elif analysis['volume_profile'] == 'LOW':
                    action = {
                        'action': 'SELL_QUARTER',
                        'quantity': abs(qty) / 4,
                        'reason': f'Partial profit taking: {unrealized_pct:.1f}% gain with low volume',
                        'urgency': 'LOW'
                    }
                    
            elif unrealized_pct >= 15.0 and not analysis['regime_alignment']:
                action = {
                    'action': 'SELL_HALF',
                    'quantity': abs(qty) / 2,
                    'reason': f'Market regime risk: {unrealized_pct:.1f}% gain in unfavorable regime',
                    'urgency': 'MEDIUM'
                }
                
            elif unrealized_pct >= 10.0 and analysis['risk_level'] == 'HIGH':
                action = {
                    'action': 'SELL_QUARTER',
                    'quantity': abs(qty) / 4,
                    'reason': f'Risk reduction: {unrealized_pct:.1f}% gain in high-risk environment',
                    'urgency': 'MEDIUM'
                }
                
            # === POSITION SCALING TRIGGERS ===
            elif (unrealized_pct >= 5.0 and unrealized_pct <= 8.0 and 
                  analysis['trend_strength'] == 'STRONG_UP' and 
                  analysis['volume_profile'] == 'HIGH'):
                
                # Add to winning position if we have capacity
                account = await self.gateway.get_account_safe()
                if account:
                    account_value = float(account.equity)
                    current_position_pct = (abs(qty) * current_price) / account_value
                    
                    if current_position_pct < 0.08:  # Don't exceed 8% in single position
                        add_quantity = max(1, int(abs(qty) * 0.25))  # Add 25% more
                        action = {
                            'action': 'BUY_MORE',
                            'quantity': add_quantity,
                            'reason': f'Scaling winner: {unrealized_pct:.1f}% gain with strong momentum',
                            'urgency': 'LOW'
                        }
                        
            # === RISK MANAGEMENT OVERRIDES ===
            if analysis['risk_level'] == 'HIGH' and abs(unrealized_pct) > 15:
                if action['action'] == 'HOLD':
                    action = {
                        'action': 'SELL_QUARTER',
                        'quantity': abs(qty) / 4,
                        'reason': 'High-risk position size reduction',
                        'urgency': 'MEDIUM'
                    }
                    
            return action
            
        except Exception as e:
            self.logger.error(f"Position action determination failed for {symbol}: {e}")
            return {'action': 'HOLD', 'quantity': 0, 'reason': 'Error in analysis', 'urgency': 'LOW'}
            
    async def _execute_position_management(self, position, action: Dict, current_price: float):
        """Execute position management action"""
        try:
            symbol = position.symbol
            current_qty = float(position.qty)
            action_type = action['action']
            quantity = int(action['quantity'])
            
            if quantity == 0:
                self.logger.warning(f"Zero quantity calculated for {symbol} {action_type}")
                return False
                
            self.logger.info(f"🎯 POSITION ACTION: {symbol} {action_type} {quantity} shares - {action['reason']}")
            
            # Determine order side and type
            if action_type in ['SELL_ALL', 'SELL_HALF', 'SELL_QUARTER']:
                side = 'sell'
                order_type = 'market' if action['urgency'] == 'IMMEDIATE' else 'limit'
                limit_price = current_price * 0.995 if order_type == 'limit' else None
                
            elif action_type == 'BUY_MORE':
                side = 'buy' 
                order_type = 'limit'  # Always use limit for adding positions
                limit_price = current_price * 1.005  # Slight premium acceptable
                
            else:
                self.logger.warning(f"Unknown action type: {action_type}")
                return False
                
            # Construct order
            order_data = {
                'symbol': symbol,
                'qty': str(quantity),
                'side': side,
                'type': order_type,
                'time_in_force': 'day'
            }
            
            if limit_price:
                order_data['limit_price'] = str(round(limit_price, 2))
                
            # Submit order
            order_response = await self.gateway.submit_order(order_data)
            
            if order_response:
                # Log comprehensive management action
                management_log = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': action_type,
                    'quantity': quantity,
                    'side': side,
                    'order_type': order_type,
                    'price': limit_price or current_price,
                    'reason': action['reason'],
                    'urgency': action['urgency'],
                    'original_qty': current_qty,
                    'order_id': order_response.id
                }
                
                self.logger.info(f"📝 POSITION MANAGEMENT: {json.dumps(management_log, indent=2)}")
                
                # Update session stats
                self.session_stats['trades_executed'] += 1
                
                return True
            else:
                self.logger.error(f"❌ Position management order failed for {symbol}")
                return False
                
        except Exception as e:
            self.logger.error(f"Position management execution failed: {e}")
            return False

    async def _monitor_system_risk(self):
        """Comprehensive system risk monitoring"""
        try:
            # Get current portfolio data
            account = await self.gateway.get_account_safe()
            if not account:
                return
                
            current_equity = float(account.equity)
            
            # Check daily drawdown
            if await self.risk_manager.check_daily_drawdown(current_equity):
                self.logger.critical("🚨 DAILY DRAWDOWN LIMIT EXCEEDED")
                await self.alerter.send_critical_alert(
                    "Daily drawdown limit exceeded",
                    f"Current equity: ${current_equity:,.2f} - Emergency shutdown initiated"
                )
                await self._emergency_shutdown("Daily drawdown limit exceeded")
                return
            
            # Check circuit breaker (flash crash protection)
            if await self.risk_manager.check_circuit_breaker(current_equity):
                self.logger.critical("⚡ CIRCUIT BREAKER TRIGGERED - FLASH CRASH PROTECTION")
                await self.alerter.send_critical_alert(
                    "CIRCUIT BREAKER: Flash crash protection activated",
                    f"Account equity dropped to ${current_equity:,.2f} - Emergency liquidation initiated"
                )
                await self._emergency_shutdown("Circuit breaker triggered - flash crash protection")
                return
                
            # Portfolio risk analysis
            if self.current_intelligence:
                portfolio_data = {
                    'total_value': current_equity,
                    'cash': float(account.cash),
                    'positions': await self._get_portfolio_positions(),
                    'daily_pnl': float(account.equity) - float(account.last_equity)
                }
                
                try:
                    risk_analysis = await self.ai_assistant.analyze_portfolio_risk(
                        portfolio_data, self.current_intelligence
                    )
                except Exception as ai_risk_error:
                    self.logger.warning(f"⚠️ AI PORTFOLIO RISK ANALYSIS FAILURE: {ai_risk_error}")
                    self.logger.warning(f"⚠️ Using fallback risk assessment")
                    risk_analysis = {
                        'overall_risk_score': 0.5,
                        'risk_level': 'MODERATE',
                        'recommendations': ['AI risk analysis unavailable - monitor manually']
                    }
                
                # Check for high-risk conditions
                if risk_analysis.get('risk_level') == 'HIGH':
                    self.logger.warning(f"⚠️ HIGH PORTFOLIO RISK: {risk_analysis.get('key_risks', [])}")
                    
                # Log risk metrics
                self.logger.debug(f"📊 Portfolio Risk Score: {risk_analysis.get('overall_risk_score', 0):.2f}")
                
        except Exception as e:
            self.logger.error(f"Risk monitoring failed: {e}")
    
    async def _monitor_pdt_status(self):
        """Monitor and report PDT status and blocked symbols"""
        try:
            # Log PDT-blocked symbols if any
            pdt_blocked = self.gateway.get_pdt_blocked_symbols()
            if pdt_blocked:
                self.logger.info(f"🚫 PDT-blocked symbols: {', '.join(pdt_blocked)}")
                
                # If we have too many blocked symbols, consider resetting older ones
                if len(pdt_blocked) > 10:
                    self.logger.warning(f"⚠️ High number of PDT-blocked symbols ({len(pdt_blocked)}) - consider manual review")
                    
        except Exception as e:
            self.logger.error(f"PDT status monitoring failed: {e}")
    
    async def _extended_hours_monitoring_loop(self):
        """Monitor positions during pre-market and after-hours for gap risk"""
        try:
            is_extended, period = self.market_status.is_extended_hours()
            if not is_extended:
                return
            
            self.logger.info(f"🌙 Extended hours monitoring active: {period}")
            
            # Get current positions
            positions = await self.gateway.get_all_positions()
            active_positions = [pos for pos in positions if float(pos.qty) != 0]
            
            if not active_positions:
                self.logger.info("✅ No positions to monitor during extended hours")
                await asyncio.sleep(300)  # Sleep 5 minutes and recheck
                return
            
            # Monitor each position for gap risk
            gap_risk_alerts = []
            
            for position in active_positions:
                try:
                    symbol = position.symbol
                    qty = float(position.qty)
                    current_value = float(position.market_value)
                    unrealized_pct = float(position.unrealized_plpc) * 100
                    
                    # Get current extended hours quote if available
                    try:
                        current_quote = await self.gateway.get_latest_quote(symbol) 
                        if current_quote:
                            current_price = float(current_quote.get('ask_price', 0)) or float(current_quote.get('bid_price', 0))
                            if current_price > 0:
                                # Check for significant moves during extended hours
                                entry_price = float(position.avg_entry_price)
                                current_move_pct = ((current_price - entry_price) / entry_price) * 100
                                
                                # Alert on large extended hours moves
                                if abs(current_move_pct) > 5:  # More than 5% move
                                    gap_risk_alerts.append({
                                        'symbol': symbol,
                                        'move_pct': current_move_pct,
                                        'current_price': current_price,
                                        'entry_price': entry_price,
                                        'position_value': abs(qty) * current_price
                                    })
                    except Exception as quote_error:
                        self.logger.debug(f"Could not get extended hours quote for {symbol}: {quote_error}")
                    
                    # Check for positions approaching dangerous loss levels
                    if unrealized_pct < -7:  # Approaching our -8% stop loss
                        self.logger.warning(f"⚠️ EXTENDED HOURS RISK: {symbol} at {unrealized_pct:.1f}% loss")
                        
                except Exception as pos_error:
                    self.logger.error(f"Extended hours monitoring failed for {position.symbol}: {pos_error}")
            
            # Send alerts for significant gap moves
            if gap_risk_alerts:
                for alert in gap_risk_alerts:
                    self.logger.critical(f"🚨 GAP RISK: {alert['symbol']} moved {alert['move_pct']:+.1f}% to ${alert['current_price']:.2f} in {period}")
                
                symbols_with_gaps = [alert['symbol'] for alert in gap_risk_alerts]
                await self.alerter.send_critical_alert(
                    f"Extended hours gap risk detected in {period}",
                    f"Significant moves detected: {', '.join(symbols_with_gaps)}"
                )
            
            # Sleep for 5 minutes before next extended hours check
            self.logger.debug(f"🔄 Extended hours monitoring cycle complete - sleeping 5 minutes")
            await asyncio.sleep(300)
            
        except Exception as e:
            self.logger.error(f"Extended hours monitoring failed: {e}")
            await asyncio.sleep(300)  # Sleep and retry
    
    async def _record_market_close_positions(self):
        """Record position prices at market close for gap risk monitoring"""
        try:
            # Only record closes near end of trading day (after 3:45 PM)
            current_time = datetime.now().time()
            if current_time >= time(15, 45):  # 3:45 PM ET
                positions = await self.gateway.get_all_positions()
                self.gap_risk_manager.record_market_close_positions(positions)
        except Exception as e:
            self.logger.error(f"Failed to record market close positions: {e}")
            
    async def _update_performance_metrics(self):
        """Update comprehensive performance tracking"""
        try:
            await self.performance_tracker.update_performance()
            
            # Get daily summary
            daily_performance = await self.performance_tracker.get_daily_summary()
            
            if daily_performance.get('return_pct', 0) != 0:
                self.logger.info(f"📊 Daily Performance: {daily_performance['return_pct']:.2%} "
                               f"| Total: ${daily_performance['total_value']:,.2f}")
                               
        except Exception as e:
            self.logger.error(f"Performance tracking failed: {e}")
            
    async def _system_health_check(self):
        """Comprehensive system health monitoring"""
        try:
            # Check API rate limits
            funnel_stats = await self.market_funnel.get_funnel_statistics()
            api_budget_status = funnel_stats.get('api_budget_remaining', {})
            
            # Warn if any budget category is low
            for category, remaining in api_budget_status.items():
                if remaining < 5:
                    self.logger.warning(f"⚠️ Low API budget: {category} ({remaining} remaining)")
                    
            # Log system statistics
            uptime = (datetime.now() - self.session_stats['system_uptime_start']).total_seconds() / 3600
            
            health_report = {
                'system_uptime_hours': uptime,
                'opportunities_discovered': self.session_stats['opportunities_discovered'],
                'signals_generated': self.session_stats['signals_generated'],
                'trades_executed': self.session_stats['trades_executed'],
                'current_watchlist_size': len(self.active_opportunities),
                'market_regime': self.current_intelligence.market_regime if self.current_intelligence else 'UNKNOWN',
                'api_budget_status': api_budget_status
            }
            
            self.logger.debug(f"💓 System Health: {json.dumps(health_report, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"System health check failed: {e}")
            
    async def _emergency_shutdown(self, reason: str):
        """Emergency shutdown with position protection"""
        try:
            self.logger.critical(f"🚨 EMERGENCY SHUTDOWN: {reason}")
            
            # Send critical alert immediately
            await self.alerter.send_critical_alert(
                f"EMERGENCY SHUTDOWN: {reason}",
                "Trading system is shutting down immediately. All positions being closed."
            )
            
            # Close all positions immediately
            await self.order_executor.emergency_close_all()
            
            # Cancel all pending orders
            await self.gateway.cancel_all_orders()
            
            # Generate emergency report
            emergency_report = await self._generate_emergency_report(reason)
            self.logger.critical(f"📊 EMERGENCY REPORT: {json.dumps(emergency_report, indent=2)}")
            
            self.running = False
            
        except Exception as e:
            self.logger.critical(f"Emergency shutdown failed: {e}")
            await self.alerter.send_critical_alert(
                "Emergency shutdown system failure",
                f"Shutdown procedure encountered error: {e}"
            )
            
    async def _graceful_shutdown(self):
        """Graceful system shutdown"""
        try:
            self.logger.info("🛑 GRACEFUL SHUTDOWN INITIATED")
            
            # Close AI assistant
            if self.ai_assistant:
                try:
                    await self.ai_assistant.shutdown()
                    self.logger.info("✅ AI Assistant shutdown completed")
                except Exception as shutdown_error:
                    self.logger.warning(f"⚠️ AI ASSISTANT SHUTDOWN WARNING: {shutdown_error}")
                    self.logger.warning(f"⚠️ AI session may not have closed cleanly")
                
            # Close API gateway
            if self.gateway:
                await self.gateway.shutdown()
                
            # Close supplemental data provider
            if self.supplemental_data:
                await self.supplemental_data.shutdown()
                
            # Generate final performance report
            final_report = await self.performance_tracker.generate_final_report()
            self.logger.info(f"📊 FINAL PERFORMANCE: {json.dumps(final_report, indent=2)}")
            
            self.logger.info("✅ SYSTEM SHUTDOWN COMPLETE")
            
        except Exception as e:
            self.logger.error(f"Graceful shutdown error: {e}")
    
    async def test_tiered_analysis_with_hot_stocks(self):
        """
        Test the tiered analysis system with the hot stocks mentioned by day traders
        This method demonstrates comprehensive analysis regardless of rate limits/data issues
        """
        try:
            self.logger.info("🔥 Testing Tiered Analysis with Day Trader Hot Stocks")
            
            # Hot stocks mentioned by day traders (from your example)
            hot_stocks = [
                'CWD', 'SMXT', 'RKLB', 'IONQ', 'OKLO', 'QBTS', 'SOFI', 'PLTR', 
                'MEIP', 'AUUD', 'AIP', 'IDXX'
            ]
            
            self.logger.info(f"🎯 Analyzing {len(hot_stocks)} hot stocks with comprehensive tiered approach")
            
            # Use the tiered analysis system
            results = await self.market_funnel.analyze_hot_stocks(hot_stocks)
            
            # Process and log results
            actionable_results = []
            all_results_summary = []
            
            for result in results:
                result_summary = {
                    'symbol': result.symbol,
                    'tier_completed': result.tier_completed.name,
                    'recommendation': result.recommendation,
                    'signal_strength': f"{result.signal_strength:.2f}",
                    'confidence': f"{result.confidence:.2f}",
                    'data_quality': result.data_quality,
                    'reasoning': result.reasoning
                }
                all_results_summary.append(result_summary)
                
                if result.recommendation in ['BUY', 'SELL']:
                    actionable_results.append(result)
            
            # Log comprehensive results
            self.logger.info(f"✅ TIERED ANALYSIS RESULTS:")
            self.logger.info(f"   - Total stocks analyzed: {len(hot_stocks)}")
            self.logger.info(f"   - Results generated: {len(results)}")
            self.logger.info(f"   - Actionable signals: {len(actionable_results)}")
            
            # Log detailed results for each stock
            for summary in all_results_summary:
                tier_icon = "🔬" if summary['tier_completed'] == "DEEP_DIVE" else "🔍" if summary['tier_completed'] == "PRIORITY_ANALYSIS" else "⚡"
                quality_icon = "🟢" if summary['data_quality'] == "EXCELLENT" else "🟡" if summary['data_quality'] == "GOOD" else "🟠" if summary['data_quality'] == "LIMITED" else "🔴"
                
                self.logger.info(f"   {tier_icon} {summary['symbol']}: {summary['recommendation']} "
                                f"(str:{summary['signal_strength']}, conf:{summary['confidence']}) "
                                f"{quality_icon} {summary['data_quality']} - {summary['reasoning']}")
            
            # Return actionable results for potential execution
            return actionable_results
            
        except Exception as e:
            self.logger.error(f"Hot stocks tiered analysis test failed: {e}")
            return []
            
    # Helper methods
    async def _collect_initial_market_data(self) -> Dict:
        """Collect initial market data for intelligence generation"""
        try:
            market_data = {}
            
            # Get SPY data (S&P 500 proxy)
            spy_bars = await self.gateway.get_bars('SPY', '1Day', limit=2)
            if spy_bars and len(spy_bars) >= 2:
                current_price = float(spy_bars[-1].get('c', 0))
                prev_price = float(spy_bars[-2].get('c', current_price))
                change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                
                market_data['SPY'] = {
                    'price': current_price,
                    'change_pct': change_pct
                }
            else:
                # Fallback: get current quote
                spy_quote = await self.gateway.get_latest_quote('SPY')
                if spy_quote:
                    price = float(spy_quote.get('ask_price', 0)) or float(spy_quote.get('bid_price', 0))
                    market_data['SPY'] = {'price': price, 'change_pct': 0.0}
                    
            # Try to get VIX data (volatility index) - not available on free tier
            try:
                vix_quote = await self.gateway.get_latest_quote('VIX')
                if vix_quote:
                    vix_level = float(vix_quote.get('ask_price', 0)) or float(vix_quote.get('bid_price', 0))
                    if vix_level > 0:
                        market_data['VIX'] = {'level': vix_level}
                        self.logger.info(f"📊 VIX Level: {vix_level}")
                else:
                    self.logger.debug("VIX data not available (expected on free tier)")
            except Exception as e:
                self.logger.debug(f"VIX data not available (expected on free tier): {e}")
                
            # Analyze volume profile from major ETFs
            volume_profile = 'NORMAL'
            try:
                etf_volumes = []
                for etf in ['SPY', 'QQQ', 'IWM']:
                    bars = await self.gateway.get_bars(etf, '1Day', limit=1)
                    if bars:
                        volume = int(bars[0].get('v', 0))
                        if volume > 0:
                            etf_volumes.append(volume)
                            
                if etf_volumes:
                    avg_volume = sum(etf_volumes) / len(etf_volumes)
                    if avg_volume > 75000000:  # High volume threshold
                        volume_profile = 'HIGH'
                    elif avg_volume < 25000000:  # Low volume threshold
                        volume_profile = 'LOW'
            except Exception as e:
                self.logger.debug(f"Volume profile analysis failed: {e}")
                
            market_data['volume_profile'] = volume_profile
            
            return market_data
            
        except Exception as e:
            self.logger.warning(f"⚠️ INITIAL MARKET DATA COLLECTION FAILURE: {e}")
            self.logger.warning(f"⚠️ Market intelligence will have limited context")
            # Return minimal fallback data
            return {'volume_profile': 'UNKNOWN'}
        
    async def _collect_current_market_data(self) -> Dict:
        """Collect current market data"""
        return await self._collect_initial_market_data()
        
    async def _get_portfolio_positions(self) -> List[Dict]:
        """Get current portfolio positions"""
        try:
            positions = await self.gateway.get_all_positions()
            return [
                {
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'market_value': float(pos.market_value),
                    'unrealized_pl': float(pos.unrealized_pl)
                }
                for pos in positions
            ]
        except:
            return []
            
    def _aggregate_intraday_to_daily(self, intraday_bars: List[Dict], hours_per_day: int = 6) -> List[Dict]:
        """Aggregate intraday bars to daily equivalents for better analysis"""
        try:
            if not intraday_bars or len(intraday_bars) < hours_per_day:
                return []
                
            daily_bars = []
            
            # Group bars by day and aggregate
            for i in range(0, len(intraday_bars), hours_per_day):
                day_group = intraday_bars[i:i + hours_per_day]
                
                if len(day_group) < hours_per_day // 2:  # Need at least half the expected bars
                    continue
                    
                # Aggregate OHLCV data
                open_price = float(day_group[0].get('o', 0))
                close_price = float(day_group[-1].get('c', 0))
                high_price = max(float(bar.get('h', 0)) for bar in day_group)
                low_price = min(float(bar.get('l', 0)) for bar in day_group if float(bar.get('l', 0)) > 0)
                total_volume = sum(int(bar.get('v', 0)) for bar in day_group)
                
                if open_price > 0 and close_price > 0 and high_price > 0 and low_price > 0:
                    daily_bars.append({
                        't': day_group[-1].get('t'),  # Use latest timestamp
                        'o': open_price,
                        'h': high_price,
                        'l': low_price,
                        'c': close_price,
                        'v': total_volume
                    })
                    
            self.logger.info(f"📊 Aggregated {len(intraday_bars)} intraday bars to {len(daily_bars)} daily equivalents")
            return daily_bars
            
        except Exception as e:
            self.logger.error(f"Intraday aggregation failed: {e}")
            return []
    
    async def _generate_emergency_report(self, reason: str) -> Dict:
        """Generate comprehensive emergency report"""
        return {
            'shutdown_reason': reason,
            'shutdown_time': datetime.now().isoformat(),
            'session_statistics': self.session_stats,
            'final_account_status': 'UNKNOWN'  # Would get actual account data
        }

# Signal handlers for graceful shutdown
def setup_signal_handlers(trading_system, loop):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler():
        print("\n🛑 Ctrl+C detected - initiating graceful shutdown...")
        trading_system.running = False
        # Cancel all running tasks to force immediate shutdown
        for task in asyncio.all_tasks(loop):
            if not task.done():
                task.cancel()
        
    # Use loop.add_signal_handler for proper async integration
    try:
        loop.add_signal_handler(signal.SIGINT, signal_handler)
        loop.add_signal_handler(signal.SIGTERM, signal_handler)
    except NotImplementedError:
        # Fallback for Windows or other systems that don't support add_signal_handler
        def sync_signal_handler(signum, frame):
            print("\n🛑 Ctrl+C detected - initiating graceful shutdown...")
            trading_system.running = False
            # Force exit if graceful shutdown takes too long
            import threading
            def force_exit():
                import time
                time.sleep(5)  # Wait 5 seconds for graceful shutdown
                print("🚨 Force exiting...")
                import os
                os._exit(1)
            threading.Thread(target=force_exit, daemon=True).start()
            
        signal.signal(signal.SIGINT, sync_signal_handler)
        signal.signal(signal.SIGTERM, sync_signal_handler)

async def main():
    """Main entry point"""
    try:
        # Initialize trading system
        trading_system = IntelligentTradingSystem()
        
        # Get the current event loop
        loop = asyncio.get_event_loop()
        
        # Setup signal handlers
        setup_signal_handlers(trading_system, loop)
        
        # Initialize system
        if not await trading_system.initialize_system():
            print("❌ System initialization failed")
            return 1
            
        # Start intelligent trading
        await trading_system.run_intelligent_trading_loop()
        
        return 0
        
    except asyncio.CancelledError:
        print("🛑 System shutdown completed")
        return 0
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))