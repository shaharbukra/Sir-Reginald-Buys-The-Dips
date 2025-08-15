#!/bin/bash

echo "🔧 Installing timezone dependencies for extended hours trading..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
    PIP_CMD="pip"
else
    echo "⚠️  No virtual environment detected, using system pip"
    PIP_CMD="pip3"
fi

# Install pytz for timezone handling
echo "📦 Installing pytz..."
$PIP_CMD install pytz

# Verify installation
echo "🔍 Verifying pytz installation..."
python3 -c "import pytz; print('✅ pytz version:', pytz.__version__)"

# Test timezone functionality
echo "🧪 Testing timezone functionality..."
python3 -c "
import pytz
from datetime import datetime

# Test UTC time
utc_now = datetime.now(pytz.UTC)
print('✅ UTC time:', utc_now.strftime('%Y-%m-%d %H:%M:%S %Z'))

# Test Eastern time
eastern_tz = pytz.timezone('US/Eastern')
eastern_now = utc_now.astimezone(eastern_tz)
print('✅ Eastern time:', eastern_now.strftime('%Y-%m-%d %H:%M:%S %Z'))

print('✅ Timezone functionality working correctly!')
"

echo ""
echo "🎉 Timezone dependencies installed successfully!"
echo ""
echo "💡 Next steps:"
echo "   1. Run: python3 check_market_status.py"
echo "   2. Run: python3 test_timezone.py"
echo "   3. Start your trading system: python3 main.py"
