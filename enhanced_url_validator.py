#!/usr/bin/env python3
"""
Enhanced URL Validator with Database Integration

This module validates URLs before saving articles and marks broken URLs for cleanup.
"""

import sqlite3
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, List
from urllib.parse import urlparse
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "articles.db"
if not DB_PATH.exists():
    DB_PATH = BASE_DIR / "db" / "articles.db"

class EnhancedURLValidator:
    """Enhanced URL validator with database integration"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Known problematic URL patterns to avoid
        self.blacklisted_patterns = [
            'javascript:', 'mailto:', 'tel:', 'ftp:',
            'data:', 'blob:', '#', 'about:',
            'chrome:', 'edge:', 'safari:'
        ]
        
        # Trusted health domains
        self.trusted_domains = [
            'who.int', 'nih.gov', 'cdc.gov', 'fda.gov',
            'webmd.com', 'healthline.com', 'mayoclinic.org',
            'medicalnewstoday.com', 'health.com', 'everydayhealth.com',
            'reuters.com', 'cnn.com', 'bbc.com', 'npr.org',
            'news18.com', 'thehindu.com', 'indiatoday.in',
            'sciencedaily.com', 'pubmed.ncbi.nlm.nih.gov',
            'nejm.org', 'thelancet.com', 'bmj.com'
        ]
    
    def is_valid_url_format(self, url: str) -> Tuple[bool, str]:
        """Check if URL has valid format"""
        if not url or not isinstance(url, str):
            return False, "Empty or invalid URL"
        
        url = url.strip()
        
        # Check for blacklisted patterns
        if any(pattern in url.lower() for pattern in self.blacklisted_patterns):
            return False, "URL contains blacklisted pattern"
        
        # Check URL format
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format - missing scheme or domain"
            
            if parsed.scheme not in ['http', 'https']:
                return False, f"Invalid scheme: {parsed.scheme}"
            
            # Check for suspicious URLs
            if len(url) > 2000:
                return False, "URL too long"
            
            return True, "Valid format"
            
        except Exception as e:
            return False, f"URL parsing error: {e}"
    
    def check_url_accessibility(self, url: str, timeout: int = 10) -> Tuple[bool, Dict]:
        """Check if URL is accessible"""
        try:
            # Start with HEAD request (faster)
            response = self.session.head(url, timeout=timeout, allow_redirects=True)
            
            # If HEAD fails, try GET with limited content
            if response.status_code == 405:  # Method not allowed
                response = self.session.get(url, timeout=timeout, allow_redirects=True, stream=True)
                # Stop after getting headers
                response.close()
            
            status_info = {
                'status_code': response.status_code,
                'final_url': response.url,
                'content_type': response.headers.get('content-type', ''),
                'content_length': response.headers.get('content-length', ''),
                'redirects': len(response.history)
            }
            
            # Success codes
            if response.status_code in [200, 201, 202]:
                return True, {**status_info, 'status': 'accessible'}
            
            # Redirect codes (usually fine)
            elif response.status_code in [301, 302, 303, 307, 308]:
                return True, {**status_info, 'status': 'redirect'}
            
            # Client errors
            elif response.status_code in [404, 403, 410]:
                return False, {**status_info, 'status': 'not_found'}
            
            # Server errors (might be temporary)
            elif response.status_code >= 500:
                return False, {**status_info, 'status': 'server_error'}
            
            # Other codes
            else:
                return False, {**status_info, 'status': 'unknown_error'}
                
        except requests.exceptions.Timeout:
            return False, {'status': 'timeout', 'error': 'Request timed out'}
        
        except requests.exceptions.ConnectionError:
            return False, {'status': 'connection_error', 'error': 'Connection failed'}
        
        except requests.exceptions.RequestException as e:
            return False, {'status': 'request_error', 'error': str(e)}
        
        except Exception as e:
            logger.warning(f"Unexpected error checking URL {url}: {e}")
            return False, {'status': 'unknown_error', 'error': str(e)}
    
    def is_trusted_domain(self, url: str) -> bool:
        """Check if URL is from a trusted domain"""
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '')
            
            return any(trusted in domain for trusted in self.trusted_domains)
        except:
            return False
    
    def validate_article_url(self, url: str, check_accessibility: bool = True) -> Tuple[bool, Dict]:
        """Comprehensive URL validation for articles"""
        # Step 1: Format validation
        format_valid, format_msg = self.is_valid_url_format(url)
        if not format_valid:
            return False, {
                'status': 'invalid_format',
                'error': format_msg,
                'url': url
            }
        
        # Step 2: Trust check
        is_trusted = self.is_trusted_domain(url)
        
        # Step 3: Accessibility check (if requested)
        if check_accessibility:
            accessible, access_info = self.check_url_accessibility(url)
            
            return accessible or is_trusted, {
                'status': 'validated',
                'accessible': accessible,
                'trusted_domain': is_trusted,
                'validation_result': access_info,
                'url': url
            }
        else:
            return True, {
                'status': 'format_valid',
                'trusted_domain': is_trusted,
                'url': url
            }
    
    def validate_articles_batch(self, articles: List[Dict], max_workers: int = 5) -> List[Dict]:
        """Validate a batch of articles and filter out invalid ones"""
        valid_articles = []
        
        for i, article in enumerate(articles):
            url = article.get('url', '')
            
            if not url:
                logger.warning(f"Article {i+1} has no URL: {article.get('title', 'Unknown')[:50]}")
                continue
            
            # Quick format check first
            format_valid, _ = self.is_valid_url_format(url)
            if not format_valid:
                logger.warning(f"Article {i+1} has invalid URL format: {url[:100]}")
                continue
            
            # For batch processing, skip accessibility check for trusted domains
            # to speed up the process
            if self.is_trusted_domain(url):
                valid_articles.append(article)
                continue
            
            # For non-trusted domains, do accessibility check
            try:
                valid, info = self.validate_article_url(url, check_accessibility=True)
                if valid:
                    valid_articles.append(article)
                else:
                    logger.warning(f"Article {i+1} failed validation: {info.get('error', 'Unknown error')}")
            except Exception as e:
                logger.warning(f"Error validating article {i+1}: {e}")
                # In case of validation error, include the article (fail-safe)
                valid_articles.append(article)
            
            # Rate limiting
            if i % 10 == 0:
                time.sleep(0.5)
        
        logger.info(f"✅ Validated articles: {len(valid_articles)}/{len(articles)} passed")
        return valid_articles
    
    def cleanup_broken_urls(self) -> int:
        """Clean up broken URLs from database"""
        if not DB_PATH.exists():
            logger.error("Database not found")
            return 0
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Find articles with potentially broken URLs
        cursor.execute("""
            SELECT id, url, title FROM articles 
            WHERE url LIKE '%error%' 
               OR url LIKE '%404%' 
               OR url LIKE '%not-found%'
               OR url = ''
               OR url IS NULL
        """)
        
        broken_articles = cursor.fetchall()
        
        if not broken_articles:
            logger.info("✅ No broken URLs found in database")
            conn.close()
            return 0
        
        logger.info(f"🔍 Found {len(broken_articles)} articles with potentially broken URLs")
        
        fixed_count = 0
        removed_count = 0
        
        for article_id, url, title in broken_articles:
            logger.info(f"🔧 Checking article {article_id}: {title[:50]}...")
            
            if not url or url in ['', 'NULL']:
                # Remove articles without URLs
                cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
                removed_count += 1
                logger.info(f"   ❌ Removed (no URL)")
                continue
            
            # Try to validate the URL
            valid, info = self.validate_article_url(url)
            
            if not valid:
                # Remove invalid articles
                cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
                removed_count += 1
                logger.info(f"   ❌ Removed (invalid URL): {info.get('error', 'Unknown')}")
            else:
                # Mark as accessible
                cursor.execute("""
                    UPDATE articles 
                    SET url_accessible = 1, last_checked = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), article_id))
                fixed_count += 1
                logger.info(f"   ✅ Fixed (URL is valid)")
        
        conn.commit()
        conn.close()
        
        logger.info(f"🎉 Cleanup complete: {fixed_count} fixed, {removed_count} removed")
        return fixed_count + removed_count

def main():
    """Test the enhanced URL validator"""
    validator = EnhancedURLValidator()
    
    print("🔍 Enhanced URL Validator Test")
    print("=" * 40)
    
    # Test URLs
    test_urls = [
        "https://www.who.int/news",
        "https://www.nih.gov/news-events",
        "invalid-url",
        "https://httpstat.us/404",
        "https://example.com/non-existent",
        ""
    ]
    
    print("\n📝 Testing individual URLs:")
    for url in test_urls:
        valid, info = validator.validate_article_url(url)
        status = "✅ VALID" if valid else "❌ INVALID"
        print(f"   {status}: {url}")
        print(f"           {info.get('error', info.get('status', 'OK'))}")
    
    print("\n🧹 Running database cleanup:")
    cleaned = validator.cleanup_broken_urls()
    print(f"   Processed {cleaned} articles")

if __name__ == "__main__":
    main()
