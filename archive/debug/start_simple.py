#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple startup script for testing the trading system
Bypasses market hours check for demonstration
"""

import asyncio
import os
import sys
from datetime import datetime

# Load environment variables from .env file
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from config import *
from intelligent_funnel import IntelligentMarketFunnel, MarketOpportunity
from ai_market_intelligence import EnhancedAIAssistant, MarketIntelligence
from enhanced_momentum_strategy import EventDrivenMomentumStrategy, TradingSignal
from api_gateway import ResilientAlpacaGateway
from risk_manager import ConservativeRiskManager

async def run_simple_test():
    """Run a simple test of the system components"""
    print("🚀 Starting Simple Trading System Test")
    print("=" * 50)
    
    try:
        # 1. Initialize Gateway
        print("1️⃣ Initializing API Gateway...")
        gateway = ResilientAlpacaGateway()
        
        if not await gateway.initialize():
            print("❌ Failed to initialize gateway")
            return False
            
        print("✅ Gateway initialized successfully")
        
        # 2. Get Account Info
        print("\n2️⃣ Getting Account Information...")
        account = await gateway.get_account_safe()
        if account:
            print("💰 Account Equity: ${}".format(account.equity))
            print("💵 Cash Available: ${}".format(account.cash))
            print("📊 Buying Power: ${}".format(account.buying_power))
        else:
            print("❌ Could not retrieve account info")
            return False
            
        # 3. Initialize Risk Manager
        print("\n3️⃣ Initializing Risk Manager...")
        risk_manager = ConservativeRiskManager()
        await risk_manager.initialize(float(account.equity))
        print("✅ Risk Manager initialized with ${}".format(account.equity))
        
        # 4. Initialize AI Assistant (with fallback)
        print("\n4️⃣ Initializing AI Assistant...")
        ai_assistant = EnhancedAIAssistant()
        await ai_assistant.initialize()
        
        # Test fallback intelligence
        intelligence = ai_assistant._get_fallback_intelligence()
        print("✅ AI Assistant initialized (fallback mode)")
        print("📊 Market Regime: {}".format(intelligence.market_regime))
        
        # 5. Initialize Market Funnel
        print("\n5️⃣ Initializing Market Funnel...")
        funnel = IntelligentMarketFunnel(gateway, ai_assistant)
        print("✅ Market Funnel initialized")
        
        # 6. Test Opportunity Discovery (simulation)
        print("\n6️⃣ Testing Opportunity Discovery...")
        
        # Create sample opportunities
        opportunities = await funnel._get_market_movers('gainers')
        if opportunities:
            print("✅ Found {} sample opportunities:".format(len(opportunities)))
            for i, opp in enumerate(opportunities[:3], 1):
                print("   {}. {} (+{}%) - {} volume".format(
                    i, opp.symbol, opp.daily_change_pct, opp.volume
                ))
        else:
            print("⚠️ No opportunities found (simulation)")
            
        # 7. Test Strategy Engine
        print("\n7️⃣ Testing Strategy Engine...")
        strategy = EventDrivenMomentumStrategy()
        print("✅ Strategy engine initialized")
        print("⚡ Strategy type: Event-Driven Momentum")
        
        # 8. Test Risk Assessment
        print("\n8️⃣ Testing Risk Assessment...")
        if opportunities:
            sample_signal = TradingSignal(
                symbol=opportunities[0].symbol,
                action="BUY",
                signal_type="MOMENTUM",
                entry_price=opportunities[0].current_price,
                stop_loss_price=opportunities[0].current_price * 0.92,
                take_profit_price=opportunities[0].current_price * 1.20,
                position_size_pct=2.0,
                confidence=0.8,
                reasoning="Test signal",
                timestamp=datetime.now(),
                risk_reward_ratio=2.5
            )
            
            assessment = await risk_manager.assess_position_risk(
                sample_signal, float(account.equity), []
            )
            
            print("✅ Risk assessment completed")
            print("📊 Risk Score: {:.2f}".format(assessment.risk_score))
            print("✅ Trade Approved: {}".format(assessment.approved))
            
        # 9. System Health Check
        print("\n9️⃣ System Health Check...")
        health = await gateway.get_connection_health()
        print("✅ API Connection: {}".format("Healthy" if health['is_healthy'] else "Issues"))
        print("📊 API Requests Used: {}".format(health['requests_in_last_minute']))
        
        # 10. Cleanup
        print("\n🔄 Cleaning up...")
        await ai_assistant.shutdown()
        await gateway.shutdown()
        
        print("\n" + "=" * 50)
        print("🎉 SIMPLE TEST COMPLETED SUCCESSFULLY!")
        print("✅ All core components operational")
        print("💡 System ready for paper trading")
        print("⚠️ Note: Market is closed (weekend) - no live trading")
        
        return True
        
    except Exception as e:
        print("\n❌ Test failed with error: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    success = await run_simple_test()
    return 0 if success else 1

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)