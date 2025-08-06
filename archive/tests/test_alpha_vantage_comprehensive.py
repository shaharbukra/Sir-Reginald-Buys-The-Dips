#!/usr/bin/env python3
"""
Comprehensive test of Alpha Vantage integration with dynamic key generation
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(__file__))

from supplemental_data_provider import SupplementalDataProvider

async def test_alpha_vantage_comprehensive():
    provider = SupplementalDataProvider()
    
    try:
        await provider.initialize()
        print("🔑 COMPREHENSIVE ALPHA VANTAGE TEST")
        print("=" * 60)
        
        # Test 1: Basic Alpha Vantage functionality with demo key
        print("\n📊 Test 1: Alpha Vantage with demo key")
        print("-" * 40)
        
        av_data = await provider._get_alphavantage_data('AAPL')
        if av_data:
            print(f"✅ Alpha Vantage AAPL: {len(av_data)} bars")
            print(f"   Latest: {av_data[-1]['t'][:10]} @ ${float(av_data[-1]['c']):.2f}")
        else:
            print("❌ Alpha Vantage AAPL: No data returned")
            
        # Test 2: Dynamic key generation
        print("\n🔑 Test 2: Dynamic key generation")
        print("-" * 40)
        
        # Save original state
        original_calls = provider.alphavantage_calls_today
        original_keys = len(provider.alphavantage_keys)
        
        # Simulate exhausted key to trigger generation
        provider.alphavantage_calls_today = 450
        print(f"🔄 Simulating exhausted key ({provider.alphavantage_calls_today} calls)")
        
        # Test key generation
        new_key = await provider._generate_alphavantage_key()
        if new_key and len(new_key) > 10:
            print(f"✅ Generated new key: {new_key[:8]}...")
            print(f"   Key length: {len(new_key)} characters")
            
            # Test with new key
            provider.alphavantage_keys.append(new_key)
            provider.current_key_index = len(provider.alphavantage_keys) - 1
            provider.alphavantage_calls_today = 0
            
            test_data = await provider._get_alphavantage_data('MSFT')
            if test_data:
                print(f"✅ New key works: Got {len(test_data)} bars for MSFT")
            else:
                print("❌ New key failed to get data")
                
        else:
            print("❌ Key generation failed or returned invalid key")
            if new_key:
                print(f"   Returned: '{new_key}' (len: {len(new_key)})")
        
        # Test 3: Full historical data method integration
        print("\n📊 Test 3: Full integration test")
        print("-" * 40)
        
        # Reset to normal state
        provider.alphavantage_calls_today = 0
        
        # Test symbols that should work with different sources
        test_symbols = [
            ('AAPL', 'Major stock - should work with Yahoo'),
            ('TSLA', 'Popular stock - should work with Yahoo'), 
            ('IBM', 'Traditional stock - might need Alpha Vantage'),
            ('XOM', 'Energy stock - test coverage')
        ]
        
        for symbol, description in test_symbols:
            print(f"\n🔍 Testing {symbol} ({description}):")
            
            # Test full historical data method
            data = await provider.get_historical_data(symbol, days=30, min_bars=10)
            
            if data and len(data) >= 10:
                print(f"   ✅ Got {len(data)} bars")
                print(f"   📅 Range: {data[0]['t'][:10]} to {data[-1]['t'][:10]}")
                print(f"   💰 Latest: ${float(data[-1]['c']):.2f}")
                
                # Check volume data
                latest_vol = int(data[-1].get('v', 0))
                print(f"   📊 Volume: {latest_vol:,}")
                
            else:
                print(f"   ❌ Insufficient data: {len(data) if data else 0} bars")
                
            # Small delay to respect rate limits
            await asyncio.sleep(1)
        
        # Test 4: Usage statistics and limits
        print(f"\n📈 Test 4: Usage Statistics")
        print("-" * 40)
        
        stats = provider.get_usage_stats()
        print(f"📊 Current Usage:")
        print(f"   Yahoo calls this minute: {stats['yahoo_calls_this_minute']}")
        print(f"   Alpha Vantage calls today: {stats['alphavantage_calls_today']}")
        print(f"   Alpha Vantage daily remaining: {stats['alphavantage_daily_remaining']}")
        print(f"   Alpha Vantage keys available: {stats['alphavantage_keys_available']}")
        print(f"   Current key index: {stats['current_key_index']}")
        
        # Test 5: Rate limiting behavior
        print(f"\n⏱️ Test 5: Rate limiting test")
        print("-" * 40)
        
        # Make several rapid requests to test rate limiting
        rapid_test_symbols = ['GOOGL', 'AMZN', 'META']
        start_time = datetime.now()
        
        for symbol in rapid_test_symbols:
            data = await provider.get_historical_data(symbol, days=5, min_bars=5)
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"   {symbol}: {len(data) if data else 0} bars in {elapsed:.2f}s")
            
        print(f"\n✅ Rate limiting test completed in {elapsed:.2f}s")
        
        # Final status
        final_stats = provider.get_usage_stats()
        print(f"\n📊 FINAL STATUS:")
        print(f"   Total Alpha Vantage keys: {final_stats['alphavantage_keys_available']}")
        print(f"   Total calls made: {final_stats['alphavantage_calls_today']}")
        print(f"   Yahoo calls: {final_stats['yahoo_calls_this_minute']}")
        
        if final_stats['alphavantage_keys_available'] > 1:
            print("✅ Dynamic key generation system working")
        else:
            print("⚠️ Key generation not tested/working")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await provider.shutdown()

if __name__ == "__main__":
    asyncio.run(test_alpha_vantage_comprehensive())