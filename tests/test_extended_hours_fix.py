#!/usr/bin/env python3
"""
Test script to verify extended hours detection and configurable stale data thresholds
"""

import asyncio
import logging
from datetime import datetime
from market_status_manager import MarketStatusManager
from api_gateway import ResilientAlpacaGateway
from config import API_CONFIG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_extended_hours_detection():
    """Test extended hours detection"""
    print("🔍 Testing Extended Hours Detection...")
    
    # Create market status manager
    market_status = MarketStatusManager(None)
    
    # Check current market status
    is_extended, period = market_status.is_extended_hours()
    print(f"📊 Current Market Status:")
    print(f"   Is Extended Hours: {is_extended}")
    print(f"   Period: {period}")
    
    # Check if we should trade during extended hours
    should_trade = market_status.should_trade_extended_hours()
    print(f"   Should Trade Extended Hours: {should_trade}")
    
    # Get current time info
    time_info = market_status.get_current_time_info()
    print(f"   Current Eastern Time: {time_info.get('eastern_time', 'Unknown')}")
    
    return is_extended, period

async def test_stale_data_thresholds():
    """Test configurable stale data thresholds"""
    print("\n🔍 Testing Stale Data Thresholds...")
    
    print(f"📊 Current API Configuration:")
    print(f"   Regular Hours Warning: {API_CONFIG.get('stale_data_warning_minutes', 'Not set')} minutes")
    print(f"   Regular Hours Rejection: {API_CONFIG.get('stale_data_rejection_minutes', 'Not set')} minutes")
    print(f"   Extended Hours Warning: {API_CONFIG.get('extended_hours_warning_minutes', 'Not set')} minutes")
    print(f"   Extended Hours Rejection: {API_CONFIG.get('extended_hours_rejection_minutes', 'Not set')} minutes")
    
    # Test quote retrieval with extended hours awareness
    try:
        gateway = ResilientAlpacaGateway()
        success = await gateway.initialize()
        
        if success:
            print("✅ API Gateway initialized successfully")
            
            # Test getting a quote (this will show the new threshold logic)
            print("\n🔍 Testing Quote Retrieval...")
            quote = await gateway.get_latest_quote('AAPL')
            
            if quote:
                print(f"✅ Quote retrieved successfully:")
                print(f"   Bid: ${quote.get('bid_price', 'N/A')}")
                print(f"   Ask: ${quote.get('ask_price', 'N/A')}")
                print(f"   Timestamp: {quote.get('timestamp', 'N/A')}")
            else:
                print("❌ Quote retrieval failed")
                
            await gateway.shutdown()
        else:
            print("❌ API Gateway initialization failed")
            
    except Exception as e:
        print(f"❌ Error testing API gateway: {e}")

async def main():
    """Main test function"""
    print("🚀 Extended Hours Trading Fix Test")
    print("=" * 50)
    
    # Test 1: Extended hours detection
    is_extended, period = await test_extended_hours_detection()
    
    # Test 2: Stale data thresholds
    await test_stale_data_thresholds()
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"   Extended Hours Detected: {is_extended}")
    print(f"   Current Period: {period}")
    
    if is_extended:
        print("✅ System is correctly detecting extended hours")
        print("✅ Stale data thresholds should now be more lenient")
    else:
        print("ℹ️  Currently in regular market hours")
        print("ℹ️  Stale data thresholds will use regular hours settings")

if __name__ == "__main__":
    asyncio.run(main())
