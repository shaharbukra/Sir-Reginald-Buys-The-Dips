#!/usr/bin/env python3
"""
Test the dynamic Alpha Vantage key generation system
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(__file__))

from supplemental_data_provider import SupplementalDataProvider

async def test_dynamic_keys():
    provider = SupplementalDataProvider()
    
    try:
        await provider.initialize()
        print("🔑 Testing Dynamic Alpha Vantage Key Generation")
        print("=" * 60)
        
        # Test initial state
        stats = provider.get_usage_stats()
        print(f"📊 Initial state:")
        print(f"   Keys available: {stats['alphavantage_keys_available']}")
        print(f"   Current key index: {stats['current_key_index']}")
        print(f"   Calls today: {stats['alphavantage_calls_today']}")
        
        # Test key generation by simulating high usage
        print(f"\n🔄 Simulating key exhaustion...")
        provider.alphavantage_calls_today = 450  # Simulate exhausted key
        
        # Request data - should trigger key generation
        print(f"📊 Requesting data for AAPL (should generate new key)...")
        data = await provider._get_alphavantage_data('AAPL')
        
        if data:
            print(f"✅ Got {len(data)} bars with new key")
        else:
            print(f"❌ No data returned")
            
        # Check final state
        final_stats = provider.get_usage_stats()
        print(f"\n📊 Final state:")
        print(f"   Keys available: {final_stats['alphavantage_keys_available']}")
        print(f"   Current key index: {final_stats['current_key_index']}")
        print(f"   Calls today: {final_stats['alphavantage_calls_today']}")
        
        # Test the full historical data method
        print(f"\n🔍 Testing full historical data retrieval...")
        historical_data = await provider.get_historical_data('TSLA', days=30, min_bars=10)
        
        if historical_data:
            print(f"✅ Retrieved {len(historical_data)} historical bars for TSLA")
            print(f"   Latest close: ${float(historical_data[-1].get('c', 0)):.2f}")
        else:
            print(f"❌ No historical data retrieved")
            
    finally:
        await provider.shutdown()

if __name__ == "__main__":
    asyncio.run(test_dynamic_keys())