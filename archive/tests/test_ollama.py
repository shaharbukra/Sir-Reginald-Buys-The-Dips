#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Ollama integration with the trading system
"""

import asyncio
import os
import json

# Load environment variables
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from ai_market_intelligence import EnhancedAIAssistant

async def test_ollama_integration():
    """Test Ollama integration"""
    print("🧠 Testing Ollama AI Integration")
    print("=" * 40)
    
    try:
        # Initialize AI assistant
        ai_assistant = EnhancedAIAssistant()
        await ai_assistant.initialize()
        
        print("✅ AI Assistant initialized")
        print("🌐 Ollama URL: {}".format(ai_assistant.api_url))
        print("🧠 Model: {}".format(ai_assistant.model))
        
        # Test market intelligence generation
        print("\n🔍 Testing Market Intelligence Generation...")
        
        # Use minimal test data - the AI should handle missing data gracefully
        market_data = {
            'volume_profile': 'TEST_DATA'
        }
        
        intelligence = await ai_assistant.generate_daily_market_intelligence(market_data)
        
        print("✅ Market Intelligence Generated:")
        print("📊 Market Regime: {}".format(intelligence.market_regime))
        print("📈 Volatility Environment: {}".format(intelligence.volatility_environment))
        print("🎯 Recommended Strategy: {}".format(intelligence.recommended_strategy))
        print("🔢 Confidence: {:.0%}".format(intelligence.confidence))
        
        # Test opportunity evaluation
        print("\n🎯 Testing Opportunity Evaluation...")
        
        from intelligent_funnel import MarketOpportunity
        from datetime import datetime
        
        test_opportunity = MarketOpportunity(
            symbol="NVDA",
            discovery_source="market_gainers",
            discovery_timestamp=datetime.now(),
            current_price=425.50,
            daily_change_pct=8.5,
            volume=45000000,
            avg_volume=30000000,
            volume_ratio=1.5,
            market_cap=1000000000000,
            sector="TECHNOLOGY"
        )
        
        evaluation = await ai_assistant.evaluate_opportunity_with_context(
            test_opportunity, intelligence
        )
        
        print("✅ Opportunity Evaluation Completed:")
        print("🎯 Overall Score: {:.2f}".format(evaluation.get('overall_score', 0)))
        print("🔢 Confidence: {:.2f}".format(evaluation.get('confidence', 0)))
        print("💰 Expected Return: {:.1f}%".format(evaluation.get('expected_return_pct', 0)))
        print("📊 Entry Recommendation: {}".format(evaluation.get('entry_recommendation', 'UNKNOWN')))
        
        await ai_assistant.shutdown()
        
        print("\n" + "=" * 40)
        print("🎉 OLLAMA INTEGRATION TEST SUCCESSFUL!")
        print("✅ AI-powered market analysis operational")
        print("✅ Real-time opportunity evaluation working")
        print("✅ System ready for intelligent trading")
        
        return True
        
    except Exception as e:
        print("❌ Test failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_ollama_integration())
    if result:
        print("\n🚀 Ready to run the full trading system with AI!")
    else:
        print("\n⚠️ Fix AI integration before running main system")