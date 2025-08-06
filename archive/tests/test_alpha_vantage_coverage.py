#!/usr/bin/env python3
"""
Test Alpha Vantage coverage with working keys
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from supplemental_data_provider import SupplementalDataProvider

async def test_alpha_vantage_coverage():
    provider = SupplementalDataProvider()
    
    try:
        await provider.initialize()
        print("🔑 TESTING ALPHA VANTAGE COVERAGE")
        print("=" * 50)
        
        # Generate a few working keys first
        working_keys = []
        for i in range(3):
            print(f"🔄 Generating Alpha Vantage key {i+1}/3...")
            key = await provider._generate_alphavantage_key()
            if key and len(key) > 10:
                working_keys.append(key)
                print(f"   ✅ Generated: {key[:8]}...")
            else:
                print(f"   ❌ Failed to generate key {i+1}")
            await asyncio.sleep(2)  # Rate limiting
        
        print(f"\n📊 Generated {len(working_keys)} working keys")
        
        if len(working_keys) == 0:
            print("❌ No working keys available for testing")
            return
            
        # Add keys to provider
        for key in working_keys:
            provider.alphavantage_keys.append(key)
        provider.current_key_index = 1  # Use first generated key
        provider.alphavantage_calls_today = 0
        
        # Test stocks that failed with Yahoo Finance
        failed_stocks = [
            'AMD', 'META', 'IBM', 'JNJ', 'KO', 
            'SPY', 'QQQ', 'XOM', 'JPM', 'DIS'
        ]
        
        print(f"\n📊 Testing {len(failed_stocks)} stocks with Alpha Vantage...")
        print("-" * 50)
        
        successful_av = 0
        
        for symbol in failed_stocks:
            print(f"\n🔍 Testing {symbol} with Alpha Vantage:")
            
            # Test Alpha Vantage directly
            av_data = await provider._get_alphavantage_data(symbol)
            
            if av_data and len(av_data) >= 10:
                successful_av += 1
                print(f"   ✅ Alpha Vantage: {len(av_data)} bars")
                print(f"   📅 {av_data[0]['t'][:10]} → {av_data[-1]['t'][:10]}")
                print(f"   💰 ${float(av_data[-1]['c']):.2f}")
            else:
                print(f"   ❌ Alpha Vantage: {len(av_data) if av_data else 0} bars")
                
            # Test full integration
            full_data = await provider.get_historical_data(symbol, days=30, min_bars=10)
            if full_data and len(full_data) >= 10:
                print(f"   ✅ Full integration: {len(full_data)} bars")
            else:
                print(f"   ❌ Full integration: {len(full_data) if full_data else 0} bars")
                
            await asyncio.sleep(1)  # Rate limiting
        
        # Summary
        av_success_rate = (successful_av / len(failed_stocks)) * 100
        print(f"\n" + "=" * 50)
        print(f"📊 ALPHA VANTAGE RESULTS")
        print(f"=" * 50)
        print(f"✅ Alpha Vantage Success: {av_success_rate:.1f}% ({successful_av}/{len(failed_stocks)})")
        
        # Usage stats
        stats = provider.get_usage_stats()
        print(f"📊 API Usage:")
        print(f"   Alpha Vantage calls: {stats['alphavantage_calls_today']}")
        print(f"   Keys available: {stats['alphavantage_keys_available']}")
        print(f"   Current key: {stats['current_key_index']}")
        
        # Combined coverage estimate
        yahoo_coverage = 5  # From previous test
        total_tested = 20
        combined_coverage = ((yahoo_coverage + successful_av) / total_tested) * 100
        
        print(f"\n🎯 COMBINED COVERAGE ESTIMATE:")
        print(f"   Yahoo Finance: {yahoo_coverage} stocks (25.0%)")
        print(f"   Alpha Vantage: {successful_av} stocks ({av_success_rate:.1f}%)")
        print(f"   Combined: {yahoo_coverage + successful_av} stocks ({combined_coverage:.1f}%)")
        
        if combined_coverage >= 85:
            print(f"🎉 EXCELLENT: Comprehensive coverage achieved!")
        elif combined_coverage >= 70:
            print(f"✅ GOOD: Strong market coverage")
        else:
            print(f"⚠️ Fair coverage, but room for improvement")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await provider.shutdown()

if __name__ == "__main__":
    asyncio.run(test_alpha_vantage_coverage())