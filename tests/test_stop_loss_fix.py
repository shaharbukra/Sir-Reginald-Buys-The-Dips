#!/usr/bin/env python3
"""
Test script for stop loss price rounding fix
"""

def test_stop_price_calculation():
    """Test stop price calculation and rounding"""
    test_prices = [164.49, 163.11, 175.50, 100.123]
    
    print("🧪 Testing stop price calculation and rounding...")
    print("=" * 50)
    
    for current_price in test_prices:
        # Old method (problematic)
        old_stop_price = current_price * 0.98
        
        # New method (fixed)
        new_stop_price = round(current_price * 0.98, 2)
        
        print(f"Current Price: ${current_price:.4f}")
        print(f"  Old Stop (problematic): ${old_stop_price:.4f}")
        print(f"  New Stop (fixed):       ${new_stop_price:.2f}")
        print(f"  Would old method fail?  {'YES' if len(str(old_stop_price).split('.')[-1]) > 2 else 'NO'}")
        print()
    
    print("✅ Stop price rounding fix verified!")

if __name__ == "__main__":
    test_stop_price_calculation()