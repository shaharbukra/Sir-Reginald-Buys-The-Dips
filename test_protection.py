#!/usr/bin/env python3
"""
Test script to verify position protection monitoring works
"""

import asyncio
import sys
from main import IntelligentTradingSystem

async def test_protection_monitoring():
    """Test the protection monitoring functionality"""
    print("🧪 Testing Position Protection System")
    print("=" * 50)
    
    # Initialize the system
    system = IntelligentTradingSystem()
    
    try:
        await system._initialize_core_systems()
        print("✅ System initialized")
        
        # Test startup position safety check
        print("\n🔍 Testing Startup Position Safety Check...")
        await system._startup_position_safety_check()
        
        # Test runtime position monitoring
        print("\n🔍 Testing Runtime Position Monitoring...")
        await system._monitor_position_protection()
        
        # Test periodic verification
        print("\n🔍 Testing Periodic Protection Verification...")
        await system._periodic_protection_verification()
        
        print("\n✅ All protection tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        try:
            await system._shutdown_gracefully()
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_protection_monitoring())
    sys.exit(0 if success else 1)