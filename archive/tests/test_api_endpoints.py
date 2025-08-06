#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test various API endpoint variations to find the correct ones
"""

import asyncio
import os
import aiohttp
from datetime import datetime, timedelta

# Load environment variables
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

async def test_endpoint_variations():
    """Test different endpoint variations to find working ones"""
    
    # Setup headers
    headers = {
        'APCA-API-KEY-ID': os.environ.get('APCA_API_KEY_ID'),
        'APCA-API-SECRET-KEY': os.environ.get('APCA_API_SECRET_KEY'),
        'Content-Type': 'application/json'
    }
    
    base_url = "https://data.alpaca.markets"
    
    # Endpoint variations to test
    endpoint_tests = [
        # News endpoints
        ("News v1beta1", "/v1beta1/news", {"limit": 5}),
        ("News v2", "/v2/news", {"limit": 5}),
        ("News v1", "/v1/news", {"limit": 5}),
        
        # Screener endpoints  
        ("Screener Movers", "/v1beta1/screener/stocks/movers", {"top": 10}),
        ("Screener Most Active", "/v1beta1/screener/stocks/mostactives", {"top": 10}),
        ("Screener Most Active v2", "/v1beta1/screener/stocks/most-actives", {"top": 10}),
        ("Market Movers", "/v1beta1/movers", {"market_type": "stocks"}),
        ("Most Actives", "/v1beta1/mostactives", {"market_type": "stocks"}),
        
        # Bars endpoints (with recent dates)
        ("Bars SPY", "/v2/stocks/SPY/bars", {
            "timeframe": "1Day", 
            "limit": 5,
            "start": (datetime.now() - timedelta(days=10)).isoformat(),
            "end": datetime.now().isoformat()
        }),
    ]
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for test_name, endpoint, params in endpoint_tests:
            print(f"\n🔍 Testing {test_name}: {endpoint}")
            
            try:
                url = f"{base_url}{endpoint}"
                async with session.get(url, params=params) as response:
                    
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"   ✅ SUCCESS")
                            print(f"   📊 Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Array/Other'}")
                            
                            # Show sample data structure
                            if isinstance(data, dict):
                                for key, value in list(data.items())[:3]:  # First 3 keys
                                    if isinstance(value, list) and len(value) > 0:
                                        print(f"      {key}: [{len(value)} items] - Sample: {list(value[0].keys()) if isinstance(value[0], dict) else type(value[0])}")
                                    else:
                                        print(f"      {key}: {type(value)} = {str(value)[:100]}")
                            elif isinstance(data, list) and len(data) > 0:
                                print(f"   📋 Array of {len(data)} items - Sample: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}")
                                
                        except Exception as e:
                            print(f"   ⚠️ Could not parse JSON: {e}")
                            text = await response.text()
                            print(f"   📄 Raw response (first 200 chars): {text[:200]}")
                            
                    elif response.status == 404:
                        print(f"   ❌ NOT FOUND - Endpoint doesn't exist")
                        
                    elif response.status == 400:
                        error_text = await response.text()
                        print(f"   ❌ BAD REQUEST: {error_text}")
                        
                    elif response.status == 401:
                        print(f"   ❌ UNAUTHORIZED - Check API keys")
                        
                    elif response.status == 403:
                        print(f"   ❌ FORBIDDEN - Check permissions")
                        
                    else:
                        error_text = await response.text()
                        print(f"   ❌ ERROR {response.status}: {error_text}")
                        
            except Exception as e:
                print(f"   💥 EXCEPTION: {e}")
                
    print(f"\n" + "="*60)
    print("🎯 ENDPOINT TESTING COMPLETE")
    print("✅ Look for successful endpoints above")
    print("🔧 Update api_gateway.py with working endpoints")

if __name__ == "__main__":
    asyncio.run(test_endpoint_variations())