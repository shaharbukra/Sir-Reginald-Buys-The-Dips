#!/usr/bin/env python3
"""
Debug Alpha Vantage key generation process
"""
import asyncio
import aiohttp
import random
import string

async def debug_alpha_vantage_key_generation():
    """Debug the Alpha Vantage key generation process step by step"""
    
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30),
        headers={'User-Agent': 'TradingBot/1.0'}
    )
    
    try:
        print("🔍 DEBUGGING ALPHA VANTAGE KEY GENERATION")
        print("=" * 60)
        
        # Step 1: Generate random email
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"trader{random_suffix}@tempmail{random.randint(1000,9999)}.com"
        print(f"📧 Generated email: {email}")
        
        # Step 2: Get the support page and extract CSRF token
        print(f"\n🔗 Fetching support page...")
        async with session.get("https://www.alphavantage.co/support/") as response:
            print(f"   Status: {response.status}")
            
            if response.status != 200:
                print(f"❌ Failed to get support page: {response.status}")
                return
                
            html_content = await response.text()
            print(f"   Page size: {len(html_content)} characters")
            
            # Debug: Look for CSRF patterns
            csrf_patterns = [
                ('csrfmiddlewaretoken', 'name="csrfmiddlewaretoken" value="'),
                ('meta_csrf', 'name="csrf-token" content="'), 
                ('csrftoken_meta', 'csrftoken" content="'),
                ('csrf_json', '"csrfToken":"')
            ]
            
            csrf_token = None
            found_pattern = None
            
            for pattern_name, pattern in csrf_patterns:
                if pattern in html_content:
                    start = html_content.find(pattern) + len(pattern)
                    end = html_content.find('"', start)
                    if start > len(pattern) - 1 and end > start:
                        csrf_token = html_content[start:end]
                        found_pattern = pattern_name
                        print(f"   ✅ Found CSRF token via {pattern_name}: {csrf_token[:16]}...")
                        break
                        
            # Also check cookies
            if not csrf_token:
                cookies = response.cookies
                if 'csrftoken' in cookies:
                    csrf_token = cookies['csrftoken'].value
                    found_pattern = "cookie"
                    print(f"   ✅ Found CSRF token in cookie: {csrf_token[:16]}...")
                    
            if not csrf_token:
                print("❌ No CSRF token found")
                # Debug: Show what we have
                print("\n🔍 Searching for potential CSRF patterns...")
                search_terms = ['csrf', 'token', 'csrfmiddlewaretoken']
                for term in search_terms:
                    if term in html_content.lower():
                        # Find context around the term
                        pos = html_content.lower().find(term)
                        start = max(0, pos - 50)
                        end = min(len(html_content), pos + 50)
                        context = html_content[start:end]
                        print(f"   Found '{term}': ...{context}...")
                return
        
        # Step 3: Create API key request
        print(f"\n🔑 Creating API key with CSRF token...")
        
        headers = {
            'X-CSRFToken': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://www.alphavantage.co/support/',
            'Origin': 'https://www.alphavantage.co',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        data = {
            'first_text': 'deprecated',
            'last_text': 'deprecated', 
            'occupation_text': 'Student',
            'organization_text': 'college',
            'email_text': email
        }
        
        print(f"   Headers: {headers}")
        print(f"   Data: {data}")
        
        async with session.post(
            "https://www.alphavantage.co/create_post/",
            headers=headers,
            data=data
        ) as response:
            
            print(f"   Response status: {response.status}")
            print(f"   Response headers: {dict(response.headers)}")
            
            if response.status == 200:
                try:
                    result = await response.json()
                    print(f"   ✅ JSON response: {result}")
                    
                    if 'text' in result and 'API key is:' in result['text']:
                        # Extract API key from response
                        text = result['text']
                        start = text.find('API key is: ') + 12
                        end = text.find('.', start)
                        if start > 11 and end > start:
                            new_key = text[start:end]
                            print(f"✅ EXTRACTED KEY: {new_key}")
                            return new_key
                        else:
                            print(f"❌ Could not extract key from: {text}")
                    else:
                        print(f"❌ Unexpected response format: {result}")
                        
                except Exception as e:
                    # Try as text
                    text_response = await response.text()
                    print(f"   📄 Text response: {text_response[:200]}...")
                    
            else:
                error_text = await response.text()
                print(f"❌ Failed to create key: {response.status}")
                print(f"   Error response: {error_text[:200]}...")
                
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(debug_alpha_vantage_key_generation())