import requests
import json

def test_search():
    base_url = 'http://localhost:8000'
    
    print('🔍 TESTING SEARCH ENDPOINTS')
    print('=' * 40)
    
    # Test cases
    test_cases = [
        'sleep%20health',
        'sexual%20wellness',
        'sleep',
        'sexual'
    ]
    
    for query in test_cases:
        try:
            url = f'{base_url}/api/v1/search?q={query}&limit=3'
            print(f'\n🔍 Testing: {query.replace("%20", " ")}')
            print(f'URL: {url}')
            
            response = requests.get(url, timeout=10)
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                articles = len(data.get('articles', []))
                print(f'✅ Total: {total}, Returned: {articles}')
                
                if data.get('articles'):
                    sample = data['articles'][0]
                    print(f'📰 Sample: {sample.get("title", "N/A")[:60]}...')
                    print(f'🏷️ Tags: {sample.get("tags", [])}')
            else:
                print(f'❌ Error: {response.text[:100]}')
                
        except Exception as e:
            print(f'❌ Exception: {e}')
    
    print('\n📋 SUMMARY:')
    print('If search is working, you should see articles for all queries')
    print('Especially "sleep health" and "sexual wellness" should return data now')

if __name__ == "__main__":
    test_search()
