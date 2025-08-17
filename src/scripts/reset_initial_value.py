#!/usr/bin/env python3
"""
Simple utility to reset the initial account value
Useful for fixing incorrect P&L calculations
"""

import json
import sys
import os
from datetime import datetime

def reset_initial_value(new_value: float):
    """Reset the initial account value in the JSON file"""
    try:
        initial_value_file = "initial_account_value.json"
        
        # Check if file exists
        if not os.path.exists(initial_value_file):
            print(f"❌ Initial value file not found: {initial_value_file}")
            print(f"   This suggests the system hasn't been run yet")
            return False
        
        # Read current value
        with open(initial_value_file, 'r') as f:
            current_data = json.load(f)
            old_value = current_data['initial_value']
            old_date = current_data.get('date_started', 'Unknown')
        
        print(f"📊 Current Initial Value: ${old_value:,.2f} (set on {old_date})")
        print(f"🔄 Resetting to: ${new_value:,.2f}")
        
        # Confirm with user
        confirm = input(f"\nAre you sure you want to change the initial value from ${old_value:,.2f} to ${new_value:,.2f}? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Reset cancelled")
            return False
        
        # Update the file
        new_data = {
            'initial_value': new_value,
            'date_started': datetime.now().isoformat(),
            'reset_reason': 'Manual reset by user',
            'previous_value': old_value,
            'previous_date': old_date
        }
        
        with open(initial_value_file, 'w') as f:
            json.dump(new_data, f, indent=2)
        
        print(f"✅ Initial account value successfully reset!")
        print(f"   Old value: ${old_value:,.2f}")
        print(f"   New value: ${new_value:,.2f}")
        print(f"   Reset time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show what this means for P&L calculations
        print(f"\n📈 P&L Impact:")
        print(f"   This will fix incorrect percentage calculations")
        print(f"   Your P&L should now show realistic values")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting initial value: {e}")
        return False

def main():
    """Main entry point"""
    print("🔄 Initial Account Value Reset Utility")
    print("=" * 50)
    
    if len(sys.argv) != 2:
        print("Usage: python reset_initial_value.py <new_initial_value>")
        print("Example: python reset_initial_value.py 35000.00")
        print("\nThis utility fixes incorrect P&L calculations by resetting")
        print("the initial account value that the system uses as a baseline.")
        sys.exit(1)
    
    try:
        new_value = float(sys.argv[1])
        if new_value <= 0:
            print("❌ Initial value must be positive")
            sys.exit(1)
    except ValueError:
        print("❌ Invalid number format. Please use a decimal number (e.g., 35000.00)")
        sys.exit(1)
    
    success = reset_initial_value(new_value)
    if success:
        print(f"\n🎯 Reset completed successfully!")
        print(f"   Next time you run the trading system, P&L calculations should be correct")
    else:
        print(f"\n❌ Reset failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
