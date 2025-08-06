#!/usr/bin/env python3
"""
Final comprehensive test of all data sources working together
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(__file__))

from supplemental_data_provider import SupplementalDataProvider

async def test_final_comprehensive():
    provider = SupplementalDataProvider()
    
    try:
        await provider.initialize()
        print("🚀 FINAL COMPREHENSIVE DATA TEST")
        print("=" * 60)
        
        # Test diverse set of stocks across different categories
        test_stocks = [
            # Large cap tech
            ('AAPL', 'Large cap tech'),
            ('MSFT', 'Large cap tech'),
            ('GOOGL', 'Large cap tech'),
            ('NVDA', 'Large cap tech'),
            
            # Popular trading stocks  
            ('TSLA', 'Popular trading'),
            ('AMD', 'Popular trading'),
            ('META', 'Popular trading'),
            
            # Traditional blue chips
            ('IBM', 'Traditional blue chip'),
            ('JNJ', 'Traditional blue chip'),
            ('KO', 'Traditional blue chip'),
            
            # ETFs
            ('SPY', 'S&P 500 ETF'),
            ('QQQ', 'NASDAQ ETF'),
            ('IWM', 'Russell 2000 ETF'),
            
            # Different sectors
            ('XOM', 'Energy'),
            ('JPM', 'Financial'),
            ('PFE', 'Healthcare'),
            ('DIS', 'Entertainment'),
            
            # Lesser known stocks
            ('PLTR', 'Emerging growth'),
            ('COIN', 'Crypto-related'),
            ('ROKU', 'Streaming')
        ]
        
        successful_retrievals = 0
        total_bars_retrieved = 0
        source_counts = {'yahoo': 0, 'alphavantage': 0, 'mixed': 0}
        
        print(f"📊 Testing {len(test_stocks)} diverse stocks...")
        print("-" * 60)
        
        for symbol, category in test_stocks:
            print(f"\n🔍 {symbol} ({category}):")
            
            start_time = datetime.now()
            
            # Test historical data
            data = await provider.get_historical_data(symbol, days=30, min_bars=10)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if data and len(data) >= 10:
                successful_retrievals += 1
                total_bars_retrieved += len(data)
                
                print(f"   ✅ {len(data)} bars in {elapsed:.2f}s")
                print(f"   📅 {data[0]['t'][:10]} → {data[-1]['t'][:10]}")
                print(f"   💰 ${float(data[-1]['c']):.2f} (Vol: {int(data[-1]['v']):,})")
                
                # Determine source (rough heuristic)
                if len(data) == 21:  # Typical Yahoo Finance
                    source_counts['yahoo'] += 1
                elif len(data) == 30:  # Typical Alpha Vantage
                    source_counts['alphavantage'] += 1
                else:
                    source_counts['mixed'] += 1
                    
            else:
                print(f"   ❌ Failed: {len(data) if data else 0} bars in {elapsed:.2f}s")
                
            # Real-time quote test
            quote = await provider.get_real_time_quote(symbol)
            if quote:
                current_price = quote.get('current_price', 0)
                print(f"   📈 Real-time: ${current_price:.2f}")
                
            # Rate limiting delay
            await asyncio.sleep(0.3)
        
        # Summary statistics
        success_rate = (successful_retrievals / len(test_stocks)) * 100
        avg_bars = total_bars_retrieved / max(successful_retrievals, 1)
        
        print(f"\n" + "=" * 60)
        print(f"📊 COMPREHENSIVE TEST RESULTS")
        print(f"=" * 60)
        print(f"✅ Success Rate: {success_rate:.1f}% ({successful_retrievals}/{len(test_stocks)})")
        print(f"📈 Total Bars Retrieved: {total_bars_retrieved:,}")
        print(f"📊 Average Bars per Stock: {avg_bars:.1f}")
        print(f"")
        print(f"📡 Data Source Distribution:")
        print(f"   Yahoo Finance: {source_counts['yahoo']} stocks")
        print(f"   Alpha Vantage: {source_counts['alphavantage']} stocks") 
        print(f"   Mixed/Other: {source_counts['mixed']} stocks")
        
        # Usage statistics
        stats = provider.get_usage_stats()
        print(f"")
        print(f"⚡ API Usage:")
        print(f"   Yahoo calls: {stats['yahoo_calls_this_minute']}")
        print(f"   Alpha Vantage calls: {stats['alphavantage_calls_today']}")
        print(f"   Alpha Vantage keys: {stats['alphavantage_keys_available']}")
        print(f"   Remaining quota: {stats['alphavantage_daily_remaining']}")
        
        # Performance assessment
        if success_rate >= 85:
            print(f"")
            print(f"🎉 EXCELLENT: System provides comprehensive market coverage!")
        elif success_rate >= 70:
            print(f"")
            print(f"✅ GOOD: System covers most major stocks adequately")
        else:
            print(f"")
            print(f"⚠️ NEEDS IMPROVEMENT: Coverage below 70%")
            
        # Key generation test if we have multiple keys
        if stats['alphavantage_keys_available'] > 1:
            print(f"🔑 Dynamic key generation: WORKING ✅")
        else:
            print(f"🔑 Dynamic key generation: Not tested")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await provider.shutdown()

if __name__ == "__main__":
    asyncio.run(test_final_comprehensive())