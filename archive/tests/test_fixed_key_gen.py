#!/usr/bin/env python3
"""
Test the fixed Alpha Vantage key generation
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from supplemental_data_provider import SupplementalDataProvider

async def test_fixed_key_generation():
    provider = SupplementalDataProvider()
    
    try:
        await provider.initialize()
        print("🔑 TESTING FIXED KEY GENERATION")
        print("=" * 50)
        
        # Test key generation
        print("🔄 Generating new Alpha Vantage key...")
        new_key = await provider._generate_alphavantage_key()
        
        if new_key and len(new_key) > 10:
            print(f"✅ Successfully generated key: {new_key}")
            
            # Test the new key by making a request
            print(f"\n📊 Testing new key with AAPL data...")
            
            # Add the new key to the provider
            provider.alphavantage_keys.append(new_key)
            provider.current_key_index = len(provider.alphavantage_keys) - 1
            provider.alphavantage_calls_today = 0
            
            # Test with the new key
            test_data = await provider._get_alphavantage_data('AAPL')
            
            if test_data and len(test_data) > 0:
                print(f"✅ New key works! Got {len(test_data)} bars")
                print(f"   Latest: {test_data[-1]['t'][:10]} @ ${float(test_data[-1]['c']):.2f}")
                print(f"   Volume: {int(test_data[-1]['v']):,}")
            else:
                print("❌ New key failed to retrieve data")
                
            # Test full integration
            print(f"\n🔄 Testing full integration...")
            provider.alphavantage_calls_today = 445  # Near limit
            
            historical = await provider.get_historical_data('MSFT', days=30, min_bars=10)
            if historical and len(historical) >= 10:
                print(f"✅ Full integration: {len(historical)} bars for MSFT")
            else:
                print(f"❌ Full integration failed: {len(historical) if historical else 0} bars")
                
        else:
            print(f"❌ Key generation failed. Returned: {new_key}")
            
        # Show final statistics
        stats = provider.get_usage_stats()
        print(f"\n📊 FINAL STATS:")
        print(f"   Keys available: {stats['alphavantage_keys_available']}")
        print(f"   Current key index: {stats['current_key_index']}")
        print(f"   Calls today: {stats['alphavantage_calls_today']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await provider.shutdown()

if __name__ == "__main__":
    asyncio.run(test_fixed_key_generation())