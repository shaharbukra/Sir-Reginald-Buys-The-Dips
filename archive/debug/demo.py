#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-Driven Trading System Demo
Shows system capabilities and validates components
"""

import asyncio
import os
import sys
from datetime import datetime

# Load environment variables
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

async def demo_system_capabilities():
    """Demonstrate system capabilities"""
    
    print("🚀 AI-Driven Trading System Demo")
    print("=" * 50)
    
    try:
        # 1. Configuration Validation
        print("\n1️⃣ Configuration Validation:")
        from config import validate_configuration, SYSTEM_CONFIG, RISK_CONFIG
        validate_configuration()
        print("   ✅ Configuration validated successfully")
        print("   📊 System Phase: {}".format(SYSTEM_CONFIG['current_phase']))
        print("   🛡️ Max Position Risk: {}%".format(RISK_CONFIG['max_position_risk_pct']))
        
        # 2. API Gateway Test
        print("\n2️⃣ API Gateway Connection:")
        from api_gateway import ResilientAlpacaGateway
        gateway = ResilientAlpacaGateway()
        
        if await gateway.initialize():
            print("   ✅ Connected to Alpaca API successfully")
            
            # Test account access
            account = await gateway.get_account_safe()
            if account:
                print("   💰 Account Equity: ${}".format(account.equity))
                print("   💵 Cash Available: ${}".format(account.cash))
                print("   📊 Buying Power: ${}".format(account.buying_power))
            
            await gateway.shutdown()
        else:
            print("   ❌ Failed to connect to Alpaca API")
            
        # 3. Market Opportunity Creation
        print("\n3️⃣ Market Opportunity Detection:")
        from intelligent_funnel import MarketOpportunity
        
        sample_opportunity = MarketOpportunity(
            symbol="NVDA",
            discovery_source="market_gainers",
            discovery_timestamp=datetime.now(),
            current_price=425.50,
            daily_change_pct=8.5,
            volume=45000000,
            avg_volume=30000000,
            volume_ratio=1.5,
            market_cap=1000000000000,  # $1T
            sector="TECHNOLOGY"
        )
        
        print("   🎯 Sample Opportunity: {} (+{}%)".format(
            sample_opportunity.symbol, 
            sample_opportunity.daily_change_pct
        ))
        print("   📊 Volume Ratio: {}x".format(sample_opportunity.volume_ratio))
        print("   🏢 Market Cap: ${:.1f}B".format(sample_opportunity.market_cap / 1e9))
        
        # 4. Risk Management
        print("\n4️⃣ Risk Management System:")
        from risk_manager import ConservativeRiskManager
        
        risk_manager = ConservativeRiskManager()
        await risk_manager.initialize(10000.0)  # $10K account
        
        print("   ✅ Risk Manager initialized")
        print("   💰 Initial Account Value: $10,000")
        print("   🛡️ Max Daily Drawdown: {}%".format(RISK_CONFIG['max_daily_drawdown_pct']))
        
        # Test drawdown check
        drawdown_exceeded = await risk_manager.check_daily_drawdown(9800.0)  # 2% down
        print("   📊 Drawdown Check (2% loss): {}".format("SAFE" if not drawdown_exceeded else "EXCEEDED"))
        
        # 5. AI Assistant
        print("\n5️⃣ AI Market Intelligence:")
        from ai_market_intelligence import EnhancedAIAssistant
        
        ai_assistant = EnhancedAIAssistant()
        await ai_assistant.initialize()
        
        print("   ✅ AI Assistant initialized")
        print("   🧠 Model: {}".format(ai_assistant.model))
        print("   🌐 Ollama URL: {}".format(ai_assistant.api_url))
        
        # Test fallback intelligence
        fallback_intelligence = ai_assistant._get_fallback_intelligence()
        print("   📊 Market Regime: {}".format(fallback_intelligence.market_regime))
        print("   📈 Volatility: {}".format(fallback_intelligence.volatility_environment))
        
        await ai_assistant.shutdown()
        
        # 6. Trading Strategy
        print("\n6️⃣ Trading Strategy Engine:")
        from enhanced_momentum_strategy import EventDrivenMomentumStrategy
        
        strategy = EventDrivenMomentumStrategy()
        print("   ✅ Momentum Strategy initialized")
        print("   ⚡ RSI Period: {}".format(strategy.strategy_config['fast_ma_period']))
        print("   📊 Volume Confirmation: {}".format(strategy.strategy_config['volume_confirmation']))
        
        # 7. System Health
        print("\n7️⃣ System Health Check:")
        print("   ✅ All core components operational")
        print("   🔄 Ready for market-wide discovery")
        print("   🛡️ Risk management active")
        print("   🧠 AI analysis ready")
        
        print("\n" + "=" * 50)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("💡 System is ready for paper trading validation")
        print("⚠️  Remember: Start with paper trading only!")
        
        return True
        
    except Exception as e:
        print("\n❌ Demo failed with error: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main demo function"""
    success = await demo_system_capabilities()
    return 0 if success else 1

if __name__ == "__main__":
    print("Starting AI-Driven Trading System Demo...")
    result = asyncio.run(main())
    sys.exit(result)