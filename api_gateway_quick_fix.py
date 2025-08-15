"""
QUICK FIX ALTERNATIVE for extended hours stale data issue

This file shows the minimal changes needed to fix the stale data problem
without implementing the full configurable solution.

To use this fix, you would replace the hardcoded thresholds in api_gateway.py
with these more lenient values for extended hours trading.
"""

# === QUICK FIX: Extended Hours Stale Data Thresholds ===

# Original hardcoded thresholds (too strict for extended hours):
# if age_minutes > 5:      # Warning at 5 minutes
# if age_minutes > 15:     # Rejection at 15 minutes

# === RECOMMENDED FIXED THRESHOLDS ===

# For regular market hours (9:30 AM - 4:00 PM ET):
REGULAR_HOURS_WARNING = 5      # Warning at 5 minutes old
REGULAR_HOURS_REJECTION = 15   # Rejection at 15 minutes old

# For extended hours (4:00 AM - 9:30 AM ET and 4:00 PM - 8:00 PM ET):
EXTENDED_HOURS_WARNING = 30    # Warning at 30 minutes old  
EXTENDED_HOURS_REJECTION = 60  # Rejection at 60 minutes old

# === IMPLEMENTATION IN api_gateway.py ===

"""
Replace this section in api_gateway.py around line 509-511:

# OLD CODE (too strict):
if age_minutes > 5:
    logger.warning(f"⚠️ STALE DATA WARNING: {symbol} quote is {age_minutes:.1f} minutes old")
    if age_minutes > 15:
        logger.error(f"🚨 CRITICAL: {symbol} quote is {age_minutes:.1f} minutes old - rejecting")
        return None

# NEW CODE (extended hours aware):
# Simple check - if it's extended hours, use lenient thresholds
current_hour = datetime.now().hour
is_extended_hours = current_hour < 9 or current_hour >= 16

if is_extended_hours:
    warning_threshold = 30  # 30 minutes for extended hours
    rejection_threshold = 60  # 60 minutes for extended hours
else:
    warning_threshold = 5   # 5 minutes for regular hours
    rejection_threshold = 15 # 15 minutes for regular hours

if age_minutes > warning_threshold:
    logger.warning(f"⚠️ STALE DATA WARNING: {symbol} quote is {age_minutes:.1f} minutes old")
    if age_minutes > rejection_threshold:
        logger.error(f"🚨 CRITICAL: {symbol} quote is {age_minutes:.1f} minutes old - rejecting")
        return None
"""

# === WHY THIS FIXES THE ISSUE ===

"""
The problem occurs because:

1. During regular market hours (9:30 AM - 4:00 PM ET):
   - Data should be very fresh (< 5 minutes old)
   - Original thresholds are appropriate

2. During extended hours (4:00 AM - 9:30 AM ET and 4:00 PM - 8:00 PM ET):
   - Market data can be 20-60 minutes old and still be valid
   - Original thresholds are too strict and reject valid data
   - This causes the "STALE DATA WARNING" and rejection errors

3. The fix:
   - Detects if we're in extended hours
   - Uses appropriate thresholds for each period
   - Allows older data during extended hours when it's expected
   - Maintains strict data freshness during regular hours
"""

# === TESTING THE FIX ===

"""
To test if this fixes your issue:

1. Run the test script: python test_extended_hours_fix.py
2. Check the logs during extended hours
3. You should see:
   - "Extended hours mode - using thresholds: warning=30m, rejection=60m"
   - No more "CRITICAL: quote is X minutes old - rejecting" errors
   - Successful quote retrieval during extended hours

If you still see issues, the problem might be:
- Timezone detection issues
- API rate limiting
- Network connectivity problems
"""
