#!/usr/bin/env python3
"""
Test script for AI-powered critical alerts
"""

import asyncio
import logging
from alerter import CriticalAlerter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ai_gap_risk_decision():
    """Test AI decision making for gap risk with enhanced data"""
    print("🧪 Testing AI-powered gap risk alerts with comprehensive data...")
    
    # Initialize the alerter
    alerter = CriticalAlerter()
    
    # Test scenario: AMD dropping 7.1% after hours
    test_context = {
        "market_session": "After-hours (4:00 PM - 8:00 PM ET)",
        "position_value": 160,
        "account_equity": 1978
    }
    
    # Enhanced market data for AI analysis
    enhanced_data = {
        # Position details
        "position_qty": 1.0,
        "position_avg_cost": 175.50,
        "position_current_pnl": -12.39,
        "position_pnl_percent": -7.1,
        "account_allocation_percent": 8.8,
        "days_held": "3 days",
        
        # Market context
        "market_regime": "SECTOR_ROTATION",
        "market_volatility": "LOW",
        "spy_performance_today": "-0.3%",
        "sector_performance": "Technology -1.2%",
        
        # Technical analysis
        "volume_vs_average": "2.1x",
        "price_vs_ma20": "-5.2%",
        "rsi": "32.4",
        "support_level": 158.50,
        "resistance_level": 185.20,
        
        # Risk metrics
        "max_loss_from_here": "8.8%",
        "correlation_with_market": "high",
        
        # News & events
        "earnings_date": "3 weeks away",
        "news_sentiment": "mixed",
        "insider_trading": "none recent",
        
        # Historical context
        "similar_gaps_outcome": "recovered 60% within 2 days",
        "stock_gap_history": "typically bounces from oversold",
        "recovery_probability": "moderate-high"
    }
    
    print(f"🤖 Testing AI decision for AMD -7.1% gap with comprehensive data...")
    
    # Get AI decision with rich data
    ai_decision = await alerter.send_gap_risk_alert_with_ai(
        symbol="AMD",
        gap_percent=-7.1,
        current_price=163.11,
        context=test_context,
        enhanced_data=enhanced_data
    )
    
    print(f"\n✅ Enhanced AI Decision Result:")
    print(f"   Decision: {ai_decision['decision']}")
    print(f"   Reasoning: {ai_decision['reasoning']}")
    print(f"   Confidence: {ai_decision['confidence']:.1%}")
    print(f"   Risk Level: {ai_decision['risk_level']}")
    
    return ai_decision

async def test_direct_ai_query():
    """Test direct AI query without full alert system"""
    print("\n🧪 Testing direct AI query...")
    
    alerter = CriticalAlerter()
    
    context = {
        "symbol": "AMD",
        "gap_percent": -7.1,
        "current_price": 163.11,
        "alert_type": "extended_hours_gap_risk",
        "market_session": "after_hours",
        "position_value": 160,
        "account_equity": 1978
    }
    
    ai_decision = await alerter.get_ai_decision("gap_risk", context)
    
    print(f"✅ Direct AI Query Result:")
    print(f"   Decision: {ai_decision['decision']}")
    print(f"   Reasoning: {ai_decision['reasoning']}")
    print(f"   Confidence: {ai_decision['confidence']}")
    print(f"   Risk Level: {ai_decision['risk_level']}")
    
    return ai_decision

async def main():
    """Run all tests"""
    print("🚀 Starting AI Alert System Tests")
    print("=" * 50)
    
    try:
        # Test 1: Full gap risk alert with AI
        decision1 = await test_ai_gap_risk_decision()
        
        # Test 2: Direct AI query
        decision2 = await test_direct_ai_query()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        
        # Summary
        print(f"\n📊 Test Summary:")
        print(f"   Full Alert Decision: {decision1['decision']}")
        print(f"   Direct Query Decision: {decision2['decision']}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())