#!/usr/bin/env python3
"""
Install basic dependencies for the trading system
"""

import subprocess
import sys

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Install required packages"""
    print("📦 Installing basic dependencies...")
    
    basic_packages = [
        'pandas',
        'numpy', 
        'aiohttp',
        'requests',
        'python-dateutil'
    ]
    
    for package in basic_packages:
        print("Installing {}...".format(package))
        if install_package(package):
            print("✅ {} installed successfully".format(package))
        else:
            print("❌ Failed to install {}".format(package))
            
    print("🎉 Basic dependencies installation complete!")
    print("💡 For full functionality, run the complete setup.sh script")

if __name__ == "__main__":
    main()