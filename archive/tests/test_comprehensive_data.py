#!/usr/bin/env python3
"""
Test comprehensive data acquisition with Yahoo Finance and Alpha Vantage
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(__file__))

from supplemental_data_provider import SupplementalDataProvider

async def test_comprehensive_data():
    provider = SupplementalDataProvider()
    
    try:
        await provider.initialize()
        print("📊 Testing Comprehensive Data Acquisition")
        print("=" * 60)
        
        # Test with popular symbols that should have data
        test_symbols = ['AAPL', 'TSLA', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'SPY', 'QQQ']
        
        for symbol in test_symbols:
            print(f"\n🔍 Testing {symbol}:")
            
            # Test historical data (should get from Yahoo Finance)
            historical = await provider.get_historical_data(symbol, days=30, min_bars=10)
            if historical and len(historical) >= 10:
                print(f"   ✅ Historical: {len(historical)} bars")
                print(f"   📅 Date range: {historical[0]['t'][:10]} to {historical[-1]['t'][:10]}")
                print(f"   💰 Latest close: ${float(historical[-1]['c']):.2f}")
            else:
                print(f"   ❌ Historical: {len(historical) if historical else 0} bars (insufficient)")
            
            # Test real-time quote
            quote = await provider.get_real_time_quote(symbol)
            if quote:
                print(f"   ✅ Real-time: ${quote['current_price']:.2f}")
            else:
                print(f"   ❌ Real-time: No quote available")
                
            # Small delay to respect rate limits
            await asyncio.sleep(0.5)
        
        # Test usage statistics
        stats = provider.get_usage_stats()
        print(f"\n📊 Usage Statistics:")
        print(f"   Yahoo calls this minute: {stats['yahoo_calls_this_minute']}")
        print(f"   Alpha Vantage calls today: {stats['alphavantage_calls_today']}")
        print(f"   Alpha Vantage keys available: {stats['alphavantage_keys_available']}")
        
        # Test edge cases
        print(f"\n🧪 Testing Edge Cases:")
        
        # Test with invalid symbol
        invalid_data = await provider.get_historical_data('INVALIDTICKER123', days=30, min_bars=10)
        print(f"   Invalid ticker: {len(invalid_data) if invalid_data else 0} bars")
        
        # Test with very small data requirement
        small_data = await provider.get_historical_data('AAPL', days=5, min_bars=3)
        print(f"   Small requirement (3+ bars): {len(small_data) if small_data else 0} bars")
        
    finally:
        await provider.shutdown()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_data())