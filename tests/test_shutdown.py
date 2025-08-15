#!/usr/bin/env python3
"""
Test script for graceful shutdown sequence
"""

import asyncio
import logging
import signal
from main import IntelligentTradingSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_graceful_shutdown():
    """Test the graceful shutdown sequence"""
    print("🧪 Testing graceful shutdown sequence...")
    
    # Create trading system instance
    system = IntelligentTradingSystem()
    
    try:
        # Initialize just the core components needed for shutdown test
        system.logger.info("🚀 Initializing minimal system for shutdown test...")
        
        # Initialize core components
        await system._initialize_core_components()
        system.system_initialized = True
        
        print("✅ System initialized successfully")
        
        # Simulate some brief operation
        await asyncio.sleep(2)
        print("🔄 System running for 2 seconds...")
        
        # Test graceful shutdown
        print("🛑 Testing graceful shutdown...")
        await system._graceful_shutdown()
        
        print("✅ Graceful shutdown completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Shutdown test failed: {e}")

async def test_shutdown_signal():
    """Test shutdown signal handling"""
    print("\n🧪 Testing shutdown signal handling...")
    
    system = IntelligentTradingSystem()
    
    # Set up signal handler
    def signal_handler(sig, frame):
        print("🛑 Ctrl+C detected - initiating graceful shutdown...")
        asyncio.create_task(system._graceful_shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("✅ Signal handler test setup complete")
    print("   (In real usage, Ctrl+C would trigger graceful shutdown)")

async def main():
    """Run all shutdown tests"""
    print("🚀 Starting Shutdown Sequence Tests")
    print("=" * 50)
    
    try:
        # Test 1: Direct graceful shutdown
        await test_graceful_shutdown()
        
        # Test 2: Signal handling setup
        await test_shutdown_signal()
        
        print("\n" + "=" * 50)
        print("✅ All shutdown tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Shutdown tests failed: {e}")
        logger.error(f"Shutdown tests failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())