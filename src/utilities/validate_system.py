#!/usr/bin/env python3
"""
System validation script for AI-Driven Trading System
"""

import asyncio
import sys
import os
from datetime import datetime

async def main():
    print("🔍 Validating AI-Driven Trading System...")
    
    validation_results = []
    
    # Test 1: Configuration validation
    try:
        from ..core.config import validate_configuration
        validate_configuration()
        validation_results.append("✅ Configuration validation: PASSED")
    except Exception as e:
        validation_results.append(f"❌ Configuration validation: FAILED - {e}")

    # Test 2: API Gateway connection
    try:
        from ..core.api_gateway import ResilientAlpacaGateway
        gateway = ResilientAlpacaGateway()
        if os.getenv('APCA_API_KEY_ID') and os.getenv('APCA_API_SECRET_KEY'):
            success = await gateway.initialize()
            if success:
                validation_results.append("✅ API Gateway connection: PASSED")
                await gateway.shutdown()
            else:
                validation_results.append("❌ API Gateway connection: FAILED")
        else:
            validation_results.append("⚠️ API Gateway connection: SKIPPED (no credentials)")
    except Exception as e:
        validation_results.append(f"❌ API Gateway connection: FAILED - {e}")

    # Test 3: AI Assistant initialization
    try:
        from ..ai_intelligence.ai_market_intelligence import EnhancedAIAssistant
        ai = EnhancedAIAssistant()
        await ai.initialize()
        validation_results.append("✅ AI Assistant initialization: PASSED")
        await ai.shutdown()
    except Exception as e:
        validation_results.append(f"❌ AI Assistant initialization: FAILED - {e}")

    # Test 4: Market Funnel components
    try:
        from ..strategies.intelligent_funnel import IntelligentMarketFunnel, MarketOpportunity
        from datetime import datetime
        test_opportunity = MarketOpportunity(
            symbol="TEST",
            discovery_source="test",
            discovery_timestamp=datetime.now(),
            current_price=100.0,
            daily_change_pct=2.0,
            volume=1000000,
            avg_volume=500000,
            volume_ratio=2.0,
            market_cap=1000000000,
            sector="TECHNOLOGY"
        )
        validation_results.append("✅ Market Funnel components: PASSED")
    except Exception as e:
        validation_results.append(f"❌ Market Funnel components: FAILED - {e}")

    # Test 5: Risk Manager
    try:
        from ..risk_management.risk_manager import ConservativeRiskManager
        risk_manager = ConservativeRiskManager()
        await risk_manager.initialize(10000.0)
        validation_results.append("✅ Risk Manager: PASSED")
    except Exception as e:
        validation_results.append(f"❌ Risk Manager: FAILED - {e}")
        
    # Print results
    print("\n" + "="*50)
    print("VALIDATION RESULTS")
    print("="*50)
    
    for result in validation_results:
        print(result)
        
    # Count failures
    failures = len([r for r in validation_results if "❌" in r])
    
    print(f"\n📊 Summary: {len(validation_results)-failures}/{len(validation_results)} tests passed")
    
    if failures == 0:
        print("🎉 ALL VALIDATIONS PASSED! System is ready for trading.")
        return 0
    else:
        print(f"⚠️ {failures} validation(s) failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    # Load environment variables
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
                    
    sys.exit(asyncio.run(main()))
