#!/usr/bin/env python3
"""
Demonstration of Smart Initial Value Setup
Shows how the system can intelligently suggest initial account values
"""

import asyncio
import json
from performance_tracker import PerformanceTracker
from api_gateway import ResilientAlpacaGateway

async def demo_smart_setup():
    """Demonstrate the smart initial value setup"""
    print("🤖 Smart Initial Value Setup Demonstration")
    print("=" * 60)
    
    try:
        # Initialize API gateway
        print("🔌 Initializing API Gateway...")
        gateway = ResilientAlpacaGateway()
        if not await gateway.initialize():
            print("❌ Failed to initialize API gateway")
            return
        
        # Initialize performance tracker
        print("📊 Initializing Performance Tracker...")
        tracker = PerformanceTracker(gateway)
        await tracker.initialize()
        
        print(f"✅ Performance Tracker Ready!")
        print(f"   Current Initial Value: ${tracker.initial_value:,.2f}")
        print("")
        
        # Show smart suggestions
        print("🧠 Getting Smart Suggestions...")
        suggestions = await tracker.suggest_initial_value()
        
        if 'error' in suggestions:
            print(f"❌ Error getting suggestions: {suggestions['error']}")
            return
        
        current_value = suggestions['current_value']
        print(f"📊 Current Account Value: ${current_value:,.2f}")
        print("")
        
        # Display all suggestions
        print("🎯 Available Initial Value Options:")
        print("-" * 40)
        
        for i, suggestion in enumerate(suggestions['suggestions'], 1):
            print(f"{i}. {suggestion['label']}")
            print(f"   💰 Value: ${suggestion['value']:,.2f}")
            print(f"   📝 {suggestion['description']}")
            print(f"   ✅ Pros: {', '.join(suggestion['pros'])}")
            print(f"   ⚠️  Cons: {', '.join(suggestion['cons'])}")
            print()
        
        # Show recommendation
        if suggestions['recommended']:
            recommended = suggestions['recommended']
            print(f"💡 RECOMMENDED OPTION:")
            print(f"   {recommended['label']}")
            print(f"   Value: ${recommended['value']:,.2f}")
            print(f"   {recommended['description']}")
            print(f"   {suggestions['explanation']}")
            print()
        
        # Demonstrate auto-setup
        print("🤖 Demonstrating Auto-Setup...")
        print("   (This would normally happen during system initialization)")
        
        success = await tracker.auto_setup_initial_value()
        if success:
            print("✅ Auto-setup completed successfully!")
            print(f"   New initial value: ${tracker.initial_value:,.2f}")
            
            # Show updated performance calculation
            print("\n📈 Updated Performance Calculation:")
            daily_summary = await tracker.get_daily_summary()
            print(f"   Current Equity: ${daily_summary.get('current_equity', 0):,.2f}")
            print(f"   Total P&L: ${daily_summary.get('total_pnl', 0):+.2f}")
            print(f"   Total P&L %: {daily_summary.get('total_pnl_pct', 0):+.2f}%")
            
            # Verify the calculation makes sense
            expected_pnl = daily_summary.get('current_equity', 0) - tracker.initial_value
            expected_pnl_pct = (expected_pnl / tracker.initial_value) * 100
            
            print(f"\n✅ Verification:")
            print(f"   Expected P&L: ${expected_pnl:+.2f}")
            print(f"   Expected P&L %: {expected_pnl_pct:+.2f}%")
            print(f"   Actual P&L: ${daily_summary.get('total_pnl', 0):+.2f}")
            print(f"   Actual P&L %: {daily_summary.get('total_pnl_pct', 0):+.2f}%")
            
            if abs(expected_pnl - daily_summary.get('total_pnl', 0)) < 0.01:
                print(f"   🎯 P&L calculation is now correct!")
            else:
                print(f"   ⚠️  P&L calculation still has issues")
        else:
            print("❌ Auto-setup failed")
        
        print("\n" + "=" * 60)
        print("💡 Key Benefits of Smart Setup:")
        print("   1. Automatically detects suspicious initial values")
        print("   2. Suggests multiple options based on your account")
        print("   3. Provides pros/cons for each option")
        print("   4. Auto-selects the best option for you")
        print("   5. Fixes incorrect P&L calculations automatically")
        
    except Exception as e:
        print(f"❌ Demonstration failed with error: {e}")
    finally:
        # Cleanup
        if 'gateway' in locals():
            await gateway.shutdown()

if __name__ == "__main__":
    asyncio.run(demo_smart_setup())
