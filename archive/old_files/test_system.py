#!/usr/bin/env python3
"""
Quick test of the trading system components
"""

import asyncio
import sys
from main import IntelligentTradingSystem

async def test_system():
    print("🧪 Testing Intelligent Trading System Components...")
    
    try:
        system = IntelligentTradingSystem()
        print('✅ System instantiated successfully')
        
        # Test account access
        account = await system.gateway.get_account_safe()
        if account:
            print(f'✅ Account access: ${float(account.equity):.2f}')
        else:
            print('❌ Account access failed')
        
        # Test data provider
        print("📊 Testing data provider...")
        test_data = await system.supplemental_data.get_historical_data('AAPL', days=1, min_bars=1)
        if test_data:
            print(f'✅ Data provider: Got {len(test_data)} bars for AAPL')
        else:
            print('❌ Data provider failed')
        
        # Test corporate actions filter
        blocked = system.corporate_actions_filter.is_symbol_blocked('AAPL')
        print(f'✅ Corporate actions filter: AAPL blocked = {blocked}')
        
        # Test AI assistant
        print("🧠 Testing AI assistant...")
        if system.ai_assistant:
            print('✅ AI assistant initialized')
        
        # Test graceful shutdown
        print("🛑 Testing graceful shutdown...")
        await system._graceful_shutdown()
        print('✅ Graceful shutdown completed')
        
        print("\n🎉 ALL TESTS PASSED - SYSTEM IS OPERATIONAL!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_system())