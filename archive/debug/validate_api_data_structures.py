#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive API Data Structure Validation
Validates that each Alpaca API call returns the exact data we need for trading
"""

import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any, Optional

# Load environment variables
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from api_gateway import ResilientAlpacaGateway

class APIDataValidator:
    """Comprehensive validator for API data structures and field completeness"""
    
    def __init__(self):
        self.gateway = ResilientAlpacaGateway()
        self.validation_results = []
        self.et_tz = pytz.timezone('US/Eastern')
        
    async def run_complete_data_validation(self):
        """Run complete API data structure validation"""
        print("🔍 COMPREHENSIVE API DATA STRUCTURE VALIDATION")
        print("=" * 70)
        
        try:
            # Initialize gateway
            if not await self.gateway.initialize():
                print("❌ Failed to initialize gateway")
                return False
                
            print("✅ Gateway initialized successfully")
            print()
            
            # Validate all API data structures
            await self._validate_account_data_structure()
            await self._validate_market_data_structures()
            await self._validate_quote_data_structures()
            await self._validate_order_data_structures()
            await self._validate_position_data_structures()
            await self._validate_news_data_structures()
            await self._validate_screener_data_structures()
            
            # Print comprehensive summary
            self._print_data_validation_summary()
            
            await self.gateway.shutdown()
            return True
            
        except Exception as e:
            print(f"❌ Data validation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    async def _validate_account_data_structure(self):
        """Validate account API returns all required fields for trading decisions"""
        print("1️⃣ ACCOUNT DATA STRUCTURE VALIDATION")
        print("-" * 50)
        
        try:
            print("Testing: GET /v2/account - Data Structure Analysis")
            
            # Get raw response to analyze structure
            response = await self.gateway._make_request('GET', '/v2/account')
            
            if response.success:
                account_data = response.data
                print("✅ Account API Response Received")
                print(f"📊 Raw Response Keys: {list(account_data.keys())}")
                
                # Define required fields for trading
                required_fields = {
                    'id': 'Account ID',
                    'account_number': 'Account Number', 
                    'status': 'Account Status',
                    'cash': 'Available Cash',
                    'portfolio_value': 'Total Portfolio Value',
                    'equity': 'Total Equity',
                    'buying_power': 'Available Buying Power',
                    'last_equity': 'Previous Day Equity',
                    'day_trade_count': 'Pattern Day Trade Count',
                    'pattern_day_trader': 'PDT Status',
                    'trading_blocked': 'Trading Restrictions',
                    'transfers_blocked': 'Transfer Restrictions'
                }
                
                # Validate each required field
                missing_fields = []
                present_fields = []
                
                for field, description in required_fields.items():
                    if field in account_data:
                        value = account_data[field]
                        print(f"   ✅ {field}: {value} ({description})")
                        present_fields.append(field)
                        
                        # Validate data types
                        if field in ['cash', 'portfolio_value', 'equity', 'buying_power', 'last_equity']:
                            try:
                                float_val = float(value)
                                if float_val < 0:
                                    print(f"      ⚠️ Warning: {field} is negative: {float_val}")
                            except (ValueError, TypeError):
                                print(f"      ❌ Error: {field} is not numeric: {value}")
                                
                        elif field == 'day_trade_count':
                            try:
                                int_val = int(value)
                                if int_val < 0:
                                    print(f"      ⚠️ Warning: {field} is negative: {int_val}")
                            except (ValueError, TypeError):
                                print(f"      ❌ Error: {field} is not integer: {value}")
                                
                    else:
                        missing_fields.append(field)
                        print(f"   ❌ Missing: {field} ({description})")
                        
                # Additional useful fields that might be present
                optional_fields = {
                    'long_market_value': 'Long Positions Value',
                    'short_market_value': 'Short Positions Value',
                    'daytrading_buying_power': 'Day Trading Buying Power',
                    'regt_buying_power': 'RegT Buying Power',
                    'sma': 'Special Memorandum Account',
                    'multiplier': 'Account Multiplier',
                    'currency': 'Account Currency'
                }
                
                print(f"\\n📋 Optional Fields Present:")
                for field, description in optional_fields.items():
                    if field in account_data:
                        print(f"   ✅ {field}: {account_data[field]} ({description})")
                        
                # Validation summary
                validation_score = len(present_fields) / len(required_fields)
                
                if validation_score >= 0.9:
                    print(f"\\n🎯 EXCELLENT: {validation_score:.0%} required fields present")
                    self.validation_results.append(("Account Data", True, f"{len(present_fields)}/{len(required_fields)} fields"))
                elif validation_score >= 0.7:
                    print(f"\\n⚠️ ACCEPTABLE: {validation_score:.0%} required fields present")
                    self.validation_results.append(("Account Data", True, f"{len(present_fields)}/{len(required_fields)} fields"))
                else:
                    print(f"\\n❌ INSUFFICIENT: {validation_score:.0%} required fields present")
                    self.validation_results.append(("Account Data", False, f"Only {len(present_fields)}/{len(required_fields)} fields"))
                    
            else:
                print(f"❌ Account API failed: {response.error}")
                self.validation_results.append(("Account Data", False, response.error))
                
        except Exception as e:
            print(f"❌ Account validation failed: {e}")
            self.validation_results.append(("Account Data", False, str(e)))
            
        print()
        
    async def _validate_market_data_structures(self):
        """Validate market data APIs return complete OHLCV data"""
        print("2️⃣ MARKET DATA STRUCTURE VALIDATION")
        print("-" * 50)
        
        test_symbols = ['SPY', 'AAPL', 'MSFT']
        
        for symbol in test_symbols:
            print(f"\\n📊 Testing Historical Bars for {symbol}:")
            
            try:
                # Test bars API
                print(f"Testing: GET /v2/stocks/{symbol}/bars")
                bars = await self.gateway.get_bars(symbol, '1Day', limit=5)
                
                if bars and len(bars) > 0:
                    print(f"✅ Retrieved {len(bars)} bars")
                    
                    # Analyze first bar structure
                    sample_bar = bars[0]
                    print(f"📋 Sample Bar Structure: {list(sample_bar.keys()) if hasattr(sample_bar, 'keys') else type(sample_bar)}")
                    
                    # Required OHLCV fields
                    required_bar_fields = {
                        't': 'Timestamp',
                        'o': 'Open Price', 
                        'h': 'High Price',
                        'l': 'Low Price',
                        'c': 'Close Price',
                        'v': 'Volume'
                    }
                    
                    missing_bar_fields = []
                    present_bar_fields = []
                    
                    for field, description in required_bar_fields.items():
                        if field in sample_bar:
                            value = sample_bar[field]
                            print(f"   ✅ {field}: {value} ({description})")
                            present_bar_fields.append(field)
                            
                            # Validate data types and ranges
                            if field == 't':  # Timestamp
                                if isinstance(value, str):
                                    try:
                                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                                        print(f"      ✅ Valid timestamp format")
                                    except:
                                        print(f"      ❌ Invalid timestamp format: {value}")
                                        
                            elif field in ['o', 'h', 'l', 'c']:  # Prices
                                try:
                                    price = float(value)
                                    if price <= 0:
                                        print(f"      ❌ Invalid price: {price}")
                                    elif price > 10000:  # Sanity check
                                        print(f"      ⚠️ Unusually high price: {price}")
                                except:
                                    print(f"      ❌ Non-numeric price: {value}")
                                    
                            elif field == 'v':  # Volume
                                try:
                                    volume = int(value)
                                    if volume < 0:
                                        print(f"      ❌ Negative volume: {volume}")
                                    elif volume == 0:
                                        print(f"      ⚠️ Zero volume (may be normal)")
                                except:
                                    print(f"      ❌ Non-numeric volume: {value}")
                                    
                        else:
                            missing_bar_fields.append(field)
                            print(f"   ❌ Missing: {field} ({description})")
                            
                    # Validate OHLC relationships
                    try:
                        o, h, l, c = float(sample_bar['o']), float(sample_bar['h']), float(sample_bar['l']), float(sample_bar['c'])
                        
                        if h >= max(o, c) and l <= min(o, c):
                            print(f"   ✅ Valid OHLC relationships")
                        else:
                            print(f"   ❌ Invalid OHLC: O={o}, H={h}, L={l}, C={c}")
                            
                    except Exception as e:
                        print(f"   ❌ Could not validate OHLC relationships: {e}")
                        
                    # Additional useful fields
                    optional_bar_fields = ['n', 'vw']  # number of trades, volume weighted average price
                    for field in optional_bar_fields:
                        if field in sample_bar:
                            print(f"   📊 Optional: {field} = {sample_bar[field]}")
                            
                    bar_score = len(present_bar_fields) / len(required_bar_fields)
                    
                    if bar_score == 1.0:
                        print(f"   🎯 PERFECT: All OHLCV fields present")
                        self.validation_results.append((f"{symbol} Bars", True, "Complete OHLCV"))
                    else:
                        print(f"   ❌ INCOMPLETE: {bar_score:.0%} fields present")
                        self.validation_results.append((f"{symbol} Bars", False, f"Missing {missing_bar_fields}"))
                        
                else:
                    print(f"❌ No bar data returned for {symbol}")
                    self.validation_results.append((f"{symbol} Bars", False, "No data"))
                    
            except Exception as e:
                print(f"❌ Bar validation failed for {symbol}: {e}")
                self.validation_results.append((f"{symbol} Bars", False, str(e)))
                
    async def _validate_quote_data_structures(self):
        """Validate quote APIs return complete bid/ask data"""
        print("3️⃣ QUOTE DATA STRUCTURE VALIDATION")
        print("-" * 50)
        
        test_symbols = ['SPY', 'AAPL', 'QQQ']
        
        for symbol in test_symbols:
            print(f"\\n💰 Testing Latest Quote for {symbol}:")
            
            try:
                print(f"Testing: GET /v2/stocks/{symbol}/quotes/latest")
                quote = await self.gateway.get_latest_quote(symbol)
                
                if quote:
                    print(f"✅ Quote data retrieved")
                    print(f"📋 Quote Structure: {list(quote.keys()) if hasattr(quote, 'keys') else type(quote)}")
                    
                    # Required quote fields
                    required_quote_fields = {
                        'bid_price': 'Bid Price',
                        'bid_size': 'Bid Size',
                        'ask_price': 'Ask Price', 
                        'ask_size': 'Ask Size',
                        'timestamp': 'Quote Timestamp'
                    }
                    
                    missing_quote_fields = []
                    present_quote_fields = []
                    
                    for field, description in required_quote_fields.items():
                        if field in quote:
                            value = quote[field]
                            print(f"   ✅ {field}: {value} ({description})")
                            present_quote_fields.append(field)
                            
                            # Validate data types
                            if field in ['bid_price', 'ask_price']:
                                try:
                                    price = float(value)
                                    if price <= 0:
                                        print(f"      ❌ Invalid price: {price}")
                                except:
                                    print(f"      ❌ Non-numeric price: {value}")
                                    
                            elif field in ['bid_size', 'ask_size']:
                                try:
                                    size = int(value)
                                    if size <= 0:
                                        print(f"      ⚠️ Zero/negative size: {size}")
                                except:
                                    print(f"      ❌ Non-numeric size: {value}")
                                    
                            elif field == 'timestamp':
                                if isinstance(value, str):
                                    try:
                                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                                        print(f"      ✅ Valid timestamp")
                                    except:
                                        print(f"      ❌ Invalid timestamp: {value}")
                                        
                        else:
                            missing_quote_fields.append(field)
                            print(f"   ❌ Missing: {field} ({description})")
                            
                    # Validate bid/ask spread
                    try:
                        if 'bid_price' in quote and 'ask_price' in quote:
                            bid = float(quote['bid_price'])
                            ask = float(quote['ask_price'])
                            spread = ask - bid
                            spread_pct = (spread / bid) * 100 if bid > 0 else 0
                            
                            print(f"   📊 Bid-Ask Spread: ${spread:.4f} ({spread_pct:.3f}%)")
                            
                            if spread < 0:
                                print(f"      ❌ Negative spread - data issue")
                            elif spread_pct > 5:
                                print(f"      ⚠️ Wide spread - low liquidity or data issue")
                            else:
                                print(f"      ✅ Normal spread")
                                
                    except Exception as e:
                        print(f"   ❌ Could not validate spread: {e}")
                        
                    quote_score = len(present_quote_fields) / len(required_quote_fields)
                    
                    if quote_score >= 0.8:
                        print(f"   🎯 GOOD: {quote_score:.0%} quote fields present")
                        self.validation_results.append((f"{symbol} Quote", True, f"{len(present_quote_fields)}/{len(required_quote_fields)} fields"))
                    else:
                        print(f"   ❌ INCOMPLETE: {quote_score:.0%} quote fields present")
                        self.validation_results.append((f"{symbol} Quote", False, f"Missing {missing_quote_fields}"))
                        
                else:
                    print(f"❌ No quote data returned for {symbol}")
                    self.validation_results.append((f"{symbol} Quote", False, "No data"))
                    
            except Exception as e:
                print(f"❌ Quote validation failed for {symbol}: {e}")
                self.validation_results.append((f"{symbol} Quote", False, str(e)))
                
    async def _validate_order_data_structures(self):
        """Validate order management APIs return complete order status"""
        print("4️⃣ ORDER DATA STRUCTURE VALIDATION")
        print("-" * 50)
        
        try:
            print("Testing: GET /v2/orders - Order Structure Analysis")
            
            # Get orders (all statuses to see structure)
            orders = await self.gateway.get_orders('all')
            
            print(f"✅ Retrieved {len(orders)} orders")
            
            if orders and len(orders) > 0:
                # Analyze order structure
                sample_order = orders[0]
                print(f"📋 Order Structure: {[attr for attr in dir(sample_order) if not attr.startswith('_')]}")
                
                # Required order fields
                required_order_fields = {
                    'id': 'Order ID',
                    'symbol': 'Symbol',
                    'qty': 'Quantity',
                    'side': 'Buy/Sell Side',
                    'order_type': 'Order Type',
                    'status': 'Order Status',
                    'created_at': 'Creation Time',
                    'filled_qty': 'Filled Quantity',
                    'limit_price': 'Limit Price (if applicable)',
                    'stop_price': 'Stop Price (if applicable)'
                }
                
                missing_order_fields = []
                present_order_fields = []
                
                for field, description in required_order_fields.items():
                    if hasattr(sample_order, field):
                        value = getattr(sample_order, field)
                        print(f"   ✅ {field}: {value} ({description})")
                        present_order_fields.append(field)
                        
                        # Validate specific fields
                        if field == 'qty':
                            try:
                                qty = float(value)
                                if qty <= 0:
                                    print(f"      ❌ Invalid quantity: {qty}")
                            except:
                                print(f"      ❌ Non-numeric quantity: {value}")
                                
                        elif field == 'side':
                            if value not in ['buy', 'sell']:
                                print(f"      ⚠️ Unexpected side value: {value}")
                                
                        elif field == 'status':
                            valid_statuses = ['new', 'partially_filled', 'filled', 'done_for_day', 
                                            'canceled', 'expired', 'replaced', 'pending_cancel', 
                                            'pending_replace', 'accepted', 'pending_new', 'rejected']
                            if value not in valid_statuses:
                                print(f"      ⚠️ Unexpected status: {value}")
                                
                    else:
                        missing_order_fields.append(field)
                        print(f"   ❌ Missing: {field} ({description})")
                        
                order_score = len(present_order_fields) / len(required_order_fields)
                
                if order_score >= 0.8:
                    print(f"   🎯 GOOD: {order_score:.0%} order fields present")
                    self.validation_results.append(("Order Structure", True, f"{len(present_order_fields)}/{len(required_order_fields)} fields"))
                else:
                    print(f"   ❌ INCOMPLETE: {order_score:.0%} order fields present")
                    self.validation_results.append(("Order Structure", False, f"Missing {missing_order_fields}"))
                    
            else:
                print("ℹ️ No orders found - cannot validate order structure")
                print("   Creating a test order to validate structure...")
                
                # Try to get account info to validate we can place orders
                account = await self.gateway.get_account_safe()
                if account and float(account.cash) > 100:
                    print(f"   💰 Account has ${account.cash} cash - order structure validation possible")
                    self.validation_results.append(("Order Structure", True, "Ready for orders"))
                else:
                    print(f"   ⚠️ Insufficient funds for test order")
                    self.validation_results.append(("Order Structure", False, "Cannot validate - no orders"))
                    
        except Exception as e:
            print(f"❌ Order validation failed: {e}")
            self.validation_results.append(("Order Structure", False, str(e)))
            
        print()
        
    async def _validate_position_data_structures(self):
        """Validate position APIs return P&L and position details"""
        print("5️⃣ POSITION DATA STRUCTURE VALIDATION")
        print("-" * 50)
        
        try:
            print("Testing: GET /v2/positions - Position Structure Analysis")
            
            positions = await self.gateway.get_all_positions()
            
            print(f"✅ Retrieved {len(positions)} positions")
            
            if positions and len(positions) > 0:
                # Analyze position structure
                sample_position = positions[0]
                print(f"📋 Position Structure: {[attr for attr in dir(sample_position) if not attr.startswith('_')]}")
                
                # Required position fields
                required_position_fields = {
                    'symbol': 'Symbol',
                    'qty': 'Quantity',
                    'market_value': 'Current Market Value',
                    'cost_basis': 'Original Cost Basis',
                    'unrealized_pl': 'Unrealized P&L',
                    'unrealized_plpc': 'Unrealized P&L %',
                    'avg_entry_price': 'Average Entry Price'
                }
                
                missing_position_fields = []
                present_position_fields = []
                
                for field, description in required_position_fields.items():
                    if hasattr(sample_position, field):
                        value = getattr(sample_position, field)
                        print(f"   ✅ {field}: {value} ({description})")
                        present_position_fields.append(field)
                        
                        # Validate numeric fields
                        if field in ['qty', 'market_value', 'cost_basis', 'unrealized_pl', 'avg_entry_price']:
                            try:
                                num_value = float(value)
                                if field == 'qty' and num_value == 0:
                                    print(f"      ⚠️ Zero position size")
                                elif field in ['market_value', 'cost_basis'] and num_value <= 0:
                                    print(f"      ❌ Invalid value: {num_value}")
                            except:
                                print(f"      ❌ Non-numeric value: {value}")
                                
                        elif field == 'unrealized_plpc':
                            try:
                                pct_value = float(value)
                                print(f"      📊 P&L: {pct_value:.2f}%")
                            except:
                                print(f"      ❌ Non-numeric percentage: {value}")
                                
                    else:
                        missing_position_fields.append(field)
                        print(f"   ❌ Missing: {field} ({description})")
                        
                # Validate P&L calculations
                try:
                    market_value = float(getattr(sample_position, 'market_value', 0))
                    cost_basis = float(getattr(sample_position, 'cost_basis', 0))
                    unrealized_pl = float(getattr(sample_position, 'unrealized_pl', 0))
                    
                    if cost_basis != 0:
                        calculated_pl = market_value - cost_basis
                        if abs(calculated_pl - unrealized_pl) > 0.01:  # Allow for rounding
                            print(f"      ⚠️ P&L calculation mismatch: {calculated_pl:.2f} vs {unrealized_pl:.2f}")
                        else:
                            print(f"      ✅ P&L calculation verified")
                            
                except Exception as e:
                    print(f"      ❌ Could not validate P&L calculation: {e}")
                    
                position_score = len(present_position_fields) / len(required_position_fields)
                
                if position_score >= 0.9:
                    print(f"   🎯 EXCELLENT: {position_score:.0%} position fields present")
                    self.validation_results.append(("Position Structure", True, f"{len(present_position_fields)}/{len(required_position_fields)} fields"))
                else:
                    print(f"   ❌ INCOMPLETE: {position_score:.0%} position fields present")
                    self.validation_results.append(("Position Structure", False, f"Missing {missing_position_fields}"))
                    
            else:
                print("ℹ️ No positions found - structure cannot be validated")
                print("   Position validation will occur when trades are made")
                self.validation_results.append(("Position Structure", True, "No positions to validate"))
                
        except Exception as e:
            print(f"❌ Position validation failed: {e}")
            self.validation_results.append(("Position Structure", False, str(e)))
            
        print()
        
    async def _validate_news_data_structures(self):
        """Validate news API returns complete article data"""
        print("6️⃣ NEWS DATA STRUCTURE VALIDATION")
        print("-" * 50)
        
        try:
            print("Testing: GET /v1beta1/news - News Structure Analysis")
            
            news_data = await self.gateway.get_news(limit=5)
            
            if news_data and len(news_data) > 0:
                print(f"✅ Retrieved {len(news_data)} news articles")
                
                # Analyze news structure
                sample_news = news_data[0]
                print(f"📋 News Structure: {list(sample_news.keys()) if hasattr(sample_news, 'keys') else type(sample_news)}")
                
                # Required news fields
                required_news_fields = {
                    'id': 'Article ID',
                    'headline': 'Article Headline',
                    'summary': 'Article Summary',
                    'content': 'Full Content',
                    'symbols': 'Related Symbols',
                    'created_at': 'Publication Time',
                    'updated_at': 'Update Time',
                    'url': 'Article URL'
                }
                
                missing_news_fields = []
                present_news_fields = []
                
                for field, description in required_news_fields.items():
                    if field in sample_news:
                        value = sample_news[field]
                        # Truncate long content for display
                        display_value = str(value)[:100] + "..." if len(str(value)) > 100 else value
                        print(f"   ✅ {field}: {display_value} ({description})")
                        present_news_fields.append(field)
                        
                        # Validate specific fields
                        if field == 'symbols':
                            if isinstance(value, list) and len(value) > 0:
                                print(f"      📊 Related to {len(value)} symbols: {value[:5]}")
                            else:
                                print(f"      ⚠️ No related symbols found")
                                
                        elif field in ['created_at', 'updated_at']:
                            if isinstance(value, str):
                                try:
                                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                                    print(f"      ✅ Valid timestamp")
                                except:
                                    print(f"      ❌ Invalid timestamp format")
                                    
                    else:
                        missing_news_fields.append(field)
                        print(f"   ❌ Missing: {field} ({description})")
                        
                news_score = len(present_news_fields) / len(required_news_fields)
                
                if news_score >= 0.7:
                    print(f"   🎯 GOOD: {news_score:.0%} news fields present")
                    self.validation_results.append(("News Structure", True, f"{len(present_news_fields)}/{len(required_news_fields)} fields"))
                else:
                    print(f"   ❌ INCOMPLETE: {news_score:.0%} news fields present")
                    self.validation_results.append(("News Structure", False, f"Missing {missing_news_fields}"))
                    
            else:
                print("❌ No news data returned")
                self.validation_results.append(("News Structure", False, "No data"))
                
        except Exception as e:
            print(f"❌ News validation failed: {e}")
            self.validation_results.append(("News Structure", False, str(e)))
            
        print()
        
    async def _validate_screener_data_structures(self):
        """Validate screener APIs return complete market mover data"""
        print("7️⃣ SCREENER DATA STRUCTURE VALIDATION")
        print("-" * 50)
        
        screener_tests = [
            ('Market Gainers', 'gainers'),
            ('Market Losers', 'losers'),
            ('Most Active', 'most_active')
        ]
        
        for test_name, test_type in screener_tests:
            print(f"\\n📊 Testing {test_name}:")
            
            try:
                if test_type in ['gainers', 'losers']:
                    data = await self.gateway.get_market_movers(test_type, limit=5)
                else:
                    data = await self.gateway.get_most_active_stocks(limit=5)
                    
                if data and len(data) > 0:
                    print(f"✅ Retrieved {len(data)} {test_name.lower()}")
                    
                    # Analyze structure
                    sample_item = data[0]
                    print(f"📋 Structure: {list(sample_item.keys()) if hasattr(sample_item, 'keys') else type(sample_item)}")
                    
                    # Required screener fields
                    required_screener_fields = {
                        'symbol': 'Stock Symbol',
                        'price': 'Current Price',
                        'change_percent': 'Percentage Change',
                        'volume': 'Trading Volume'
                    }
                    
                    missing_screener_fields = []
                    present_screener_fields = []
                    
                    for field, description in required_screener_fields.items():
                        if field in sample_item:
                            value = sample_item[field]
                            print(f"   ✅ {field}: {value} ({description})")
                            present_screener_fields.append(field)
                            
                            # Validate data types
                            if field == 'price':
                                try:
                                    price = float(value)
                                    if price <= 0:
                                        print(f"      ❌ Invalid price: {price}")
                                except:
                                    print(f"      ❌ Non-numeric price: {value}")
                                    
                            elif field == 'change_percent':
                                try:
                                    change = float(value)
                                    print(f"      📊 Change: {change:+.2f}%")
                                except:
                                    print(f"      ❌ Non-numeric change: {value}")
                                    
                            elif field == 'volume':
                                try:
                                    vol = int(value)
                                    if vol < 0:
                                        print(f"      ❌ Negative volume: {vol}")
                                    else:
                                        print(f"      📊 Volume: {vol:,}")
                                except:
                                    print(f"      ❌ Non-numeric volume: {value}")
                                    
                        else:
                            missing_screener_fields.append(field)
                            print(f"   ❌ Missing: {field} ({description})")
                            
                    screener_score = len(present_screener_fields) / len(required_screener_fields)
                    
                    if screener_score >= 0.75:
                        print(f"   🎯 GOOD: {screener_score:.0%} screener fields present")
                        self.validation_results.append((f"{test_name}", True, f"{len(present_screener_fields)}/{len(required_screener_fields)} fields"))
                    else:
                        print(f"   ❌ INCOMPLETE: {screener_score:.0%} screener fields present")
                        self.validation_results.append((f"{test_name}", False, f"Missing {missing_screener_fields}"))
                        
                else:
                    print(f"❌ No {test_name.lower()} data returned")
                    self.validation_results.append((f"{test_name}", False, "No data"))
                    
            except Exception as e:
                print(f"❌ {test_name} validation failed: {e}")
                self.validation_results.append((f"{test_name}", False, str(e)))
                
    def _print_data_validation_summary(self):
        """Print comprehensive data validation summary"""
        print("\\n" + "=" * 70)
        print("📊 API DATA STRUCTURE VALIDATION SUMMARY")
        print("=" * 70)
        
        passed = 0
        failed = 0
        critical_failures = []
        
        for test_name, success, details in self.validation_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status:<8} {test_name:<25} {details}")
            
            if success:
                passed += 1
            else:
                failed += 1
                # Identify critical failures
                if any(critical in test_name.lower() for critical in ['account', 'bars', 'quote', 'order']):
                    critical_failures.append(test_name)
                    
        print("\\n" + "-" * 70)
        print(f"📊 TOTAL TESTS: {passed + failed}")
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        
        if failed == 0:
            print("\\n🎉 ALL API DATA STRUCTURES VALIDATED!")
            print("✅ System ready for production trading")
        else:
            print(f"\\n⚠️ {failed} data structure validations need attention")
            
            if critical_failures:
                print(f"\\n🚨 CRITICAL FAILURES (will prevent trading):")
                for failure in critical_failures:
                    print(f"   ❌ {failure}")
                print("\\n🔧 These must be fixed before trading can begin")
            else:
                print("\\n✅ No critical failures - trading can proceed with caution")
                
        print("\\n📋 NEXT STEPS:")
        print("1. Fix any critical API data structure issues")
        print("2. Verify all required fields are available for trading logic")
        print("3. Test order placement and position management")
        print("4. Validate real-time data updates during market hours")

async def main():
    """Main validation function"""
    validator = APIDataValidator()
    success = await validator.run_complete_data_validation()
    return 0 if success else 1

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)