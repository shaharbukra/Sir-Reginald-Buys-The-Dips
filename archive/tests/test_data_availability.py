#!/usr/bin/env python3
import asyncio
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(__file__))

from api_gateway import ResilientAlpacaGateway

async def test_data_availability():
    gateway = ResilientAlpacaGateway()
    try:
        await gateway.initialize()
        
        # Test symbol with good volume
        test_symbol = 'AAPL'
        
        print(f"Testing data availability for {test_symbol}...")
        print("=" * 60)
        
        # Test different timeframes
        timeframes = ['1Day', '1Hour', '30Min', '15Min', '5Min', '1Min']
        
        for timeframe in timeframes:
            print(f"\n📊 {timeframe} data:")
            bars = await gateway.get_bars(test_symbol, timeframe, limit=100)
            if bars:
                print(f"   ✅ Got {len(bars)} bars")
                if len(bars) > 0:
                    latest = bars[-1]
                    earliest = bars[0]
                    print(f"   📅 Latest: {latest.get('t', 'N/A')}")
                    print(f"   📅 Earliest: {earliest.get('t', 'N/A')}")
                    print(f"   💰 Latest close: ${float(latest.get('c', 0)):.2f}")
                    print(f"   📈 Volume: {int(latest.get('v', 0)):,}")
            else:
                print(f"   ❌ No data returned")
        
        # Test with date ranges
        print(f"\n📅 Testing with date ranges:")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        bars_with_dates = await gateway.get_bars(
            test_symbol, '1Day', limit=100, 
            start=start_date, end=end_date
        )
        
        if bars_with_dates:
            print(f"   ✅ 30-day range: {len(bars_with_dates)} bars")
        else:
            print(f"   ❌ Date range query failed")
            
        # Test fundamental data alternatives
        print(f"\n🔍 Testing quote data:")
        quote = await gateway.get_latest_quote(test_symbol)
        if quote:
            print(f"   ✅ Quote available:")
            print(f"   💰 Bid: ${quote.get('bid_price', 0):.2f}")
            print(f"   💰 Ask: ${quote.get('ask_price', 0):.2f}")
        else:
            print(f"   ❌ No quote data")
            
        # Test news data
        print(f"\n📰 Testing news data:")
        news = await gateway.get_news(symbols=[test_symbol], limit=10)
        if news:
            print(f"   ✅ Got {len(news)} news articles")
            if len(news) > 0:
                article = news[0]
                print(f"   📰 Latest: {article.get('headline', 'N/A')[:50]}...")
                print(f"   📅 Published: {article.get('created_at', 'N/A')}")
        else:
            print(f"   ❌ No news data")
            
        # Test different symbols
        print(f"\n🔄 Testing other symbols:")
        test_symbols = ['SPY', 'QQQ', 'TSLA', 'MSFT', 'NVDA']
        
        for symbol in test_symbols:
            bars = await gateway.get_bars(symbol, '1Day', limit=30)
            bars_hour = await gateway.get_bars(symbol, '1Hour', limit=50)
            print(f"   {symbol}: {len(bars) if bars else 0} daily, {len(bars_hour) if bars_hour else 0} hourly")
            
    finally:
        await gateway.shutdown()

if __name__ == "__main__":
    asyncio.run(test_data_availability())