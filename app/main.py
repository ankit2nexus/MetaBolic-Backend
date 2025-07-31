"""
Metabolical Backend API - Clean and Simplified
Health articles API with search, categorization, and pagination.
"""

from fastapi import FastAPI, HTTPException, Query, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import utilities
try:
    from .utils import *
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from utils import *

# FastAPI app
app = FastAPI(
    title="Metabolical Backend API",
    description="Clean and simplified health articles API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
v1_router = APIRouter(prefix="/api/v1", tags=["API v1"])

# Load categories on startup
try:
    CATEGORY_KEYWORDS = get_cached_category_keywords()
    CATEGORIES = list(CATEGORY_KEYWORDS.keys())
except Exception as e:
    logger.warning(f"Could not load categories: {e}")
    CATEGORIES = ["diseases", "news", "solutions", "food", "audience", "blogs_and_opinions"]

# Pydantic Models
class ArticleSchema(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str
    source: Optional[str] = None
    date: datetime
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = []
    image_url: Optional[str] = None
    author: Optional[str] = None

class PaginatedArticleResponse(BaseModel):
    articles: List[ArticleSchema]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_previous: bool

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database_status: str
    total_articles: Optional[int] = None

# === CORE ENDPOINTS ===

@v1_router.get("/health", response_model=HealthResponse)
def health_check():
    """API health check"""
    try:
        total_articles = get_total_articles_count()
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            database_status="connected",
            total_articles=total_articles
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "database_status": "error",
                "error": str(e)
            }
        )

@v1_router.get("/", response_model=PaginatedArticleResponse)
def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles per page"),
    sort_by: str = Query("desc", enum=["asc", "desc"], description="Sort order"),
    start_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)")
):
    """Get paginated articles"""
    try:
        result = get_articles_paginated_optimized(
            page=page,
            limit=limit,
            sort_by=sort_by,
            start_date=start_date,
            end_date=end_date
        )
        return PaginatedArticleResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/latest", response_model=PaginatedArticleResponse)
def get_latest_articles(
    limit: int = Query(20, ge=1, le=100, description="Number of articles")
):
    """Get latest articles"""
    try:
        result = get_articles_paginated_optimized(page=1, limit=limit, sort_by="desc")
        return PaginatedArticleResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_latest_articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/search", response_model=PaginatedArticleResponse)
def search_articles(
    q: str = Query(..., description="Search query", min_length=2),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles per page"),
    sort_by: str = Query("desc", enum=["asc", "desc"], description="Sort order")
):
    """Search articles (primary endpoint)"""
    try:
        result = get_articles_paginated_optimized(
            page=page,
            limit=limit,
            sort_by=sort_by,
            search_query=q.strip()
        )
        return PaginatedArticleResponse(**result)
    except Exception as e:
        logger.error(f"Error in search_articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/debug/categories")
def debug_categories():
    """Debug endpoint to check what categories exist in database"""
    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all distinct categories with counts
            cursor.execute("SELECT DISTINCT categories, COUNT(*) as count FROM articles WHERE categories IS NOT NULL AND categories != '' GROUP BY categories ORDER BY count DESC")
            categories = cursor.fetchall()
            
            # Also check total articles
            cursor.execute("SELECT COUNT(*) FROM articles")
            total_articles = cursor.fetchone()[0]
            
            # Check for 'news' specifically
            cursor.execute("SELECT COUNT(*) FROM articles WHERE categories LIKE '%\"news\"%'")
            news_exact = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM articles WHERE LOWER(categories) LIKE '%news%'")
            news_like = cursor.fetchone()[0]
            
            return {
                "total_articles": total_articles,
                "categories": [{"name": cat[0], "count": cat[1]} for cat in categories],
                "news_exact_match": news_exact,
                "news_contains_match": news_like,
                "debug_time": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in debug_categories: {e}")
        return {"error": str(e)}

@v1_router.get("/categories")
def get_categories():
    """Get all categories with subcategories"""
    try:
        category_stats = get_category_stats_cached()
        categories = []
        
        for category_name in CATEGORIES:
            subcategories_dict = CATEGORY_KEYWORDS.get(category_name, {})
            subcategory_names = list(subcategories_dict.keys()) if isinstance(subcategories_dict, dict) else []
            article_count = category_stats.get(category_name, 0)
            
            categories.append({
                "name": category_name,
                "subcategories": subcategory_names,
                "article_count": article_count
            })
        
        return {
            "categories": categories,
            "total_categories": len(categories)
        }
    except Exception as e:
        logger.error(f"Error in get_categories: {e}")
        return {"categories": [], "total_categories": 0}

@v1_router.get("/tags")
def get_tags():
    """Get all available tags"""
    try:
        tags = get_tags_cached()
        return {
            "tags": tags,
            "total_tags": len(tags)
        }
    except Exception as e:
        logger.error(f"Error in get_tags: {e}")
        return {"tags": [], "total_tags": 0}

@v1_router.get("/category/{category}", response_model=PaginatedArticleResponse)
def get_articles_by_category_direct(
    category: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles per page"),
    sort_by: str = Query("desc", enum=["asc", "desc"], description="Sort order")
):
    """Get articles by category (direct category endpoint)"""
    try:
        logger.info(f"🔍 Category request: '{category}', page: {page}, limit: {limit}")
        
        result = get_articles_paginated_optimized(
            page=page,
            limit=limit,
            sort_by=sort_by,
            category=category
        )
        
        logger.info(f"📊 Category '{category}' result: {result['total']} total articles, {len(result['articles'])} returned")
        
        return PaginatedArticleResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_articles_by_category_direct: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/tag/{tag}", response_model=PaginatedArticleResponse)
def get_articles_by_tag(
    tag: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles per page"),
    sort_by: str = Query("desc", enum=["asc", "desc"], description="Sort order")
):
    """Get articles by tag"""
    try:
        logger.info(f"🏷️ Tag request: '{tag}', page: {page}, limit: {limit}")
        
        result = get_articles_paginated_optimized(
            page=page,
            limit=limit,
            sort_by=sort_by,
            tag=tag
        )
        
        logger.info(f"📊 Tag '{tag}' result: {result['total']} total articles, {len(result['articles'])} returned")
        
        return PaginatedArticleResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_articles_by_tag: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/stats")
def get_statistics():
    """Get API statistics"""
    try:
        stats = get_cached_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in get_statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/{category}", response_model=PaginatedArticleResponse)
def get_articles_by_category(
    category: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles per page"),
    sort_by: str = Query("desc", enum=["asc", "desc"], description="Sort order")
):
    """Get articles by category"""
    try:
        result = get_articles_paginated_optimized(
            page=page,
            limit=limit,
            sort_by=sort_by,
            category=category
        )
        return PaginatedArticleResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_articles_by_category: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/{category}/{subcategory}", response_model=PaginatedArticleResponse)
def get_articles_by_subcategory(
    category: str,
    subcategory: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles per page"),
    sort_by: str = Query("desc", enum=["asc", "desc"], description="Sort order")
):
    """Get articles by category and subcategory"""
    try:
        result = get_articles_paginated_optimized(
            page=page,
            limit=limit,
            sort_by=sort_by,
            category=category,
            subcategory=subcategory
        )
        return PaginatedArticleResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_articles_by_subcategory: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/debug/categories")
def debug_categories():
    """Debug endpoint to check what categories exist in database"""
    try:
        with connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all distinct categories with counts
            cursor.execute("SELECT DISTINCT categories, COUNT(*) as count FROM articles WHERE categories IS NOT NULL AND categories != '' GROUP BY categories ORDER BY count DESC")
            categories = cursor.fetchall()
            
            # Also check total articles
            cursor.execute("SELECT COUNT(*) FROM articles")
            total_articles = cursor.fetchone()[0]
            
            # Check for 'news' specifically
            cursor.execute("SELECT COUNT(*) FROM articles WHERE categories LIKE '%\"news\"%'")
            news_exact = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM articles WHERE LOWER(categories) LIKE '%news%'")
            news_like = cursor.fetchone()[0]
            
            return {
                "total_articles": total_articles,
                "categories": [{"name": cat[0], "count": cat[1]} for cat in categories],
                "news_exact_match": news_exact,
                "news_contains_match": news_like,
                "debug_time": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error in debug_categories: {e}")
        return {"error": str(e)}

@v1_router.get("/categories")
def get_categories():
    """Get all categories with subcategories"""
    try:
        category_stats = get_category_stats_cached()
        categories = []
        
        for category_name in CATEGORIES:
            subcategories_dict = CATEGORY_KEYWORDS.get(category_name, {})
            subcategory_names = list(subcategories_dict.keys()) if isinstance(subcategories_dict, dict) else []
            article_count = category_stats.get(category_name, 0)
            
            categories.append({
                "name": category_name,
                "subcategories": subcategory_names,
                "article_count": article_count
            })
        
        return {
            "categories": categories,
            "total_categories": len(categories)
        }
    except Exception as e:
        logger.error(f"Error in get_categories: {e}")
        return {"categories": [], "total_categories": 0}

@v1_router.get("/tags")
def get_tags():
    """Get all available tags"""
    try:
        tags = get_tags_cached()
        return {
            "tags": tags,
            "total_tags": len(tags)
        }
    except Exception as e:
        logger.error(f"Error in get_tags: {e}")
        return {"tags": [], "total_tags": 0}

@v1_router.get("/category/{category}", response_model=PaginatedArticleResponse)
def get_articles_by_category_direct(
    category: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles per page"),
    sort_by: str = Query("desc", enum=["asc", "desc"], description="Sort order")
):
    """Get articles by category (direct category endpoint)"""
    try:
        logger.info(f"🔍 Category request: '{category}', page: {page}, limit: {limit}")
        
        result = get_articles_paginated_optimized(
            page=page,
            limit=limit,
            sort_by=sort_by,
            category=category
        )
        
        logger.info(f"📊 Category '{category}' result: {result['total']} total articles, {len(result['articles'])} returned")
        
        return PaginatedArticleResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_articles_by_category_direct: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/tag/{tag}", response_model=PaginatedArticleResponse)
def get_articles_by_tag(
    tag: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles per page"),
    sort_by: str = Query("desc", enum=["asc", "desc"], description="Sort order")
):
    """Get articles by tag"""
    try:
        logger.info(f"🏷️ Tag request: '{tag}', page: {page}, limit: {limit}")
        
        result = get_articles_paginated_optimized(
            page=page,
            limit=limit,
            sort_by=sort_by,
            tag=tag
        )
        
        logger.info(f"📊 Tag '{tag}' result: {result['total']} total articles, {len(result['articles'])} returned")
        
        return PaginatedArticleResponse(**result)
    except Exception as e:
        logger.error(f"Error in get_articles_by_tag: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.get("/stats")
def get_statistics():
    """Get API statistics"""
    try:
        stats = get_cached_stats()
        return stats
    except Exception as e:
        logger.error(f"Error in get_statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



# Homepage
@app.get("/", response_class=HTMLResponse)
def homepage():
    """API homepage with documentation"""
    try:
        stats = get_statistics()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Metabolical Backend API</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stat {{ display: inline-block; margin: 10px; padding: 15px; background: #007bff; color: white; border-radius: 5px; }}
                .endpoint {{ margin: 8px 0; padding: 8px; background: #f8f9fa; border-left: 4px solid #007bff; }}
                h1 {{ color: #333; }}
                h2 {{ color: #007bff; }}
                a {{ color: #007bff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏥 Metabolical Backend API v2.0</h1>
                <p><strong>Status:</strong> ✅ Clean & Simplified Structure</p>
                
                <h2>📊 Statistics</h2>
                <div class="stat">📄 {stats.get('total_articles', 0)} Articles</div>
                <div class="stat">🆕 {stats.get('recent_articles_7_days', 0)} Recent</div>
                <div class="stat">📰 {stats.get('total_sources', 0)} Sources</div>
                <div class="stat">🏷️ {stats.get('total_categories', 0)} Categories</div>
                
                <h2>🚀 Main API Endpoints</h2>
                <p><strong>⚠️ Important:</strong> All API endpoints require the <code>/api/v1/</code> prefix</p>
                <div class="endpoint"><strong>GET /api/v1/</strong> - Get paginated articles</div>
                <div class="endpoint"><strong>GET /api/v1/latest</strong> - Get latest articles</div>
                <div class="endpoint"><strong>GET /api/v1/search?q={{query}}</strong> - Search articles</div>
                <div class="endpoint"><strong>GET /api/v1/{{category}}</strong> - Get articles by category</div>
                <div class="endpoint"><strong>GET /api/v1/{{category}}/{{subcategory}}</strong> - Get articles by subcategory</div>
                <div class="endpoint"><strong>GET /api/v1/category/{{category}}</strong> - Get articles by category (alternative)</div>
                <div class="endpoint"><strong>GET /api/v1/tag/{{tag}}</strong> - Get articles by tag</div>
                <div class="endpoint"><strong>GET /api/v1/categories</strong> - Get all categories</div>
                <div class="endpoint"><strong>GET /api/v1/tags</strong> - Get all tags</div>
                <div class="endpoint"><strong>GET /api/v1/stats</strong> - Get API statistics</div>
                <div class="endpoint"><strong>GET /api/v1/health</strong> - Health check</div>
                
                <h2>📚 Documentation</h2>
                <p><a href="/docs">📖 Interactive API Documentation (Swagger)</a></p>
                <p><a href="/redoc">📘 ReDoc Documentation</a></p>
                
                <p><small>🧹 Simplified structure - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
            </div>
        </body>
        </html>
        """
        return html_content
        
    except Exception as e:
        logger.error(f"Error in homepage: {e}")
        return HTMLResponse("""
        <html><body>
        <h1>Metabolical Backend API</h1>
        <p>Service temporarily unavailable. Please try again later.</p>
        </body></html>
        """, status_code=503)

# Include router
app.include_router(v1_router)

# Add redirects for common mistakes and missing API prefix
@app.get("/articles/")
async def redirect_articles():
    """Redirect /articles/ to /api/v1/"""
    return JSONResponse(
        status_code=301,
        content={
            "message": "Endpoint moved",
            "correct_url": "/api/v1/",
            "note": "All API endpoints are under /api/v1/ prefix, 'articles' removed from URLs"
        },
        headers={"Location": "/api/v1/"}
    )

@app.get("/articles")
async def redirect_articles_no_slash():
    """Redirect /articles to /api/v1/"""
    return JSONResponse(
        status_code=301,
        content={
            "message": "Endpoint moved",
            "correct_url": "/api/v1/",
            "note": "All API endpoints are under /api/v1/ prefix, 'articles' removed from URLs"
        },
        headers={"Location": "/api/v1/"}
    )

# Add redirects for old API paths with articles
@app.get("/api/v1/articles/")
async def redirect_old_api_articles():
    """Redirect old /api/v1/articles/ to /api/v1/"""
    return JSONResponse(
        status_code=301,
        content={
            "message": "Endpoint moved - 'articles' removed from URLs",
            "correct_url": "/api/v1/",
            "note": "Articles endpoints simplified - use /api/v1/ directly"
        },
        headers={"Location": "/api/v1/"}
    )

@app.get("/api/v1/articles/latest")
async def redirect_old_api_articles_latest():
    """Redirect old /api/v1/articles/latest to /api/v1/latest"""
    return JSONResponse(
        status_code=301,
        content={
            "message": "Endpoint moved - 'articles' removed from URLs",
            "correct_url": "/api/v1/latest",
            "note": "Articles endpoints simplified"
        },
        headers={"Location": "/api/v1/latest"}
    )

@app.get("/api/v1/articles/search")
async def redirect_old_api_articles_search():
    """Redirect old /api/v1/articles/search to /api/v1/search"""
    return JSONResponse(
        status_code=301,
        content={
            "message": "Endpoint moved - 'articles' removed from URLs",
            "correct_url": "/api/v1/search",
            "note": "Articles endpoints simplified"
        },
        headers={"Location": "/api/v1/search"}
    )

@app.get("/artciles/")  # Common typo
async def redirect_typo_articles():
    """Redirect common typo /artciles/ to /api/v1/"""
    return JSONResponse(
        status_code=301,
        content={
            "message": "Typo detected - did you mean the main endpoint?",
            "correct_url": "/api/v1/",
            "note": "All API endpoints are under /api/v1/ prefix, 'articles' removed from URLs"
        },
        headers={"Location": "/api/v1/"}
    )

@app.get("/artciles")  # Common typo without trailing slash
async def redirect_typo_articles_no_slash():
    """Redirect common typo /artciles to /api/v1/"""
    return JSONResponse(
        status_code=301,
        content={
            "message": "Typo detected - did you mean the main endpoint?",
            "correct_url": "/api/v1/",
            "note": "All API endpoints are under /api/v1/ prefix, 'articles' removed from URLs"
        },
        headers={"Location": "/api/v1/"}
    )

@app.get("/health")
async def redirect_health():
    """Redirect /health to /api/v1/health"""
    return JSONResponse(
        status_code=301,
        content={
            "message": "Endpoint moved",
            "correct_url": "/api/v1/health",
            "note": "All API endpoints are under /api/v1/ prefix"
        },
        headers={"Location": "/api/v1/health"}
    )

# Error handlers
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found",
            "requested_path": str(request.url.path),
            "available_endpoints": [
                "/api/v1/",
                "/api/v1/latest",
                "/api/v1/search?q=query",
                "/api/v1/{category}",
                "/api/v1/category/{category}",
                "/api/v1/tag/{tag}",
                "/api/v1/health",
                "/api/v1/categories",
                "/api/v1/tags",
                "/api/v1/stats"
            ],
            "documentation": "/docs",
            "note": "All API endpoints are under /api/v1/ prefix, 'articles' removed from URLs"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
