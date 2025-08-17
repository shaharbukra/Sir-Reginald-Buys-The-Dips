#!/usr/bin/env python3
"""
Sir Reginald Buys The Dips - Main Entry Point
Intelligent AI Trading System
"""

import asyncio
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main trading system
from src.core.main import main

if __name__ == "__main__":
    asyncio.run(main());
