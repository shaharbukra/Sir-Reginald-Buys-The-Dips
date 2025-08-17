#!/bin/bash

# AI-Driven Trading System Startup Script

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting AI-Driven Trading System...${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found. Please copy .env.example to .env and configure your API keys.${NC}"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi


# Export environment variables (ignore comments and blank lines)
export $(grep -v '^#' .env | grep -v '^$' | xargs)


# Validate configuration
echo "Validating system configuration..."
python -c "from src.core.config import validate_configuration; validate_configuration()"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Configuration validation failed${NC}"
    exit 1
fi

# Start the trading system
echo -e "${GREEN}✅ Starting intelligent trading engine...${NC}"
python main.py

