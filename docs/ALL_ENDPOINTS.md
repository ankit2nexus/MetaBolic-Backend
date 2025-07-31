# 🚀 Metabolical Backend API - Complete Endpoints Reference

## 📍 Base URL
```
http://localhost:8000
```

## 🔗 All Available Endpoints

### 🏠 **Homepage & Documentation**
```
GET /                           # API homepage with documentation
GET /docs                       # Interactive Swagger documentation  
GET /redoc                      # ReDoc documentation
```

### 🩺 **Health & Status**
```
GET /api/v1/health              # Health check and database status
GET /api/v1/stats               # API statistics and metrics
```

### 📄 **Article Endpoints**

#### Main Data Retrieval
```
GET /api/v1/                    # Get all articles with pagination
GET /api/v1/latest              # Get latest articles
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Articles per page (1-100, default: 20)
- `sort_by` (string): "asc" or "desc" (default: "desc")
- `start_date` (string): Filter from date (YYYY-MM-DD)
- `end_date` (string): Filter to date (YYYY-MM-DD)

#### Search
```
GET /api/v1/search              # Search articles by title/summary
```

**Parameters:**
- `q` (string): Search query (required, min 2 characters)
- `page` (int): Page number (default: 1)
- `limit` (int): Articles per page (1-100, default: 20)
- `sort_by` (string): "asc" or "desc" (default: "desc")

### 🏷️ **Category Filtering**

#### Direct Category Access
```
GET /api/v1/{category}          # Filter by category (generic pattern)
GET /api/v1/news                # News articles
GET /api/v1/diseases            # Disease-related articles
GET /api/v1/food                # Food and nutrition articles
GET /api/v1/solutions           # Solution-focused articles
GET /api/v1/audience            # Audience-specific articles
GET /api/v1/blogs_and_opinions  # Blog posts and opinion pieces
```

#### Alternative Category Access
```
GET /api/v1/category/{category} # Alternative category endpoint
GET /api/v1/category/news       # News articles (alternative)
GET /api/v1/category/diseases   # Disease articles (alternative)
```

#### Subcategory Access
```
GET /api/v1/{category}/{subcategory}  # Filter by category and subcategory
```

**Parameters for all category endpoints:**
- `page` (int): Page number (default: 1)
- `limit` (int): Articles per page (1-100, default: 20)
- `sort_by` (string): "asc" or "desc" (default: "desc")

### 🏷️ **Tag Filtering**
```
GET /api/v1/tag/{tag}           # Filter articles by specific tag
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Articles per page (1-100, default: 20)
- `sort_by` (string): "asc" or "desc" (default: "desc")

### 📋 **Metadata Endpoints**
```
GET /api/v1/categories          # List all available categories with counts
GET /api/v1/tags                # List all available tags
```

### 🐛 **Debug Endpoints**
```
GET /api/v1/debug/categories    # Debug category information
```

### 🔄 **Redirects & Legacy Support**

#### Automatic Redirects (301)
```
GET /articles/                  # → /api/v1/
GET /articles                   # → /api/v1/
GET /artciles/                  # → /api/v1/ (typo handling)
GET /artciles                   # → /api/v1/ (typo handling)
GET /health                     # → /api/v1/health
GET /api/v1/articles/           # → /api/v1/
GET /api/v1/articles/latest     # → /api/v1/latest
GET /api/v1/articles/search     # → /api/v1/search
```

---

## 📊 **Response Format**

### Article List Response
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Article Title",
      "summary": "Article summary...",
      "content": null,
      "url": "https://source.com/article",
      "source": "Source Name",
      "date": "2025-07-30T10:00:00",
      "category": "news",
      "subcategory": null,
      "tags": ["health", "nutrition"],
      "image_url": null,
      "author": "Author Name"
    }
  ],
  "total": 649,
  "page": 1,
  "limit": 20,
  "total_pages": 33,
  "has_next": true,
  "has_previous": false
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-07-30T10:00:00",
  "database_status": "connected",
  "total_articles": 649
}
```

### Categories Response
```json
{
  "categories": [
    {
      "name": "news",
      "subcategories": ["breaking", "updates"],
      "article_count": 96
    }
  ],
  "total_categories": 7
}
```

### Tags Response
```json
{
  "tags": ["health", "nutrition", "diabetes", "exercise"],
  "total_tags": 54
}
```

---

## 💡 **Usage Examples**

### Get Articles
```bash
# Get first 10 articles
curl "http://localhost:8000/api/v1/?page=1&limit=10"

# Get latest 5 articles
curl "http://localhost:8000/api/v1/latest?limit=5"
```

### Search Articles
```bash
# Search for diabetes articles
curl "http://localhost:8000/api/v1/search?q=diabetes&limit=10"

# Search with pagination
curl "http://localhost:8000/api/v1/search?q=nutrition&page=2&limit=20"
```

### Filter by Category
```bash
# Get news articles (method 1)
curl "http://localhost:8000/api/v1/news?limit=20"

# Get news articles (method 2)
curl "http://localhost:8000/api/v1/category/news?limit=20"

# Get disease articles
curl "http://localhost:8000/api/v1/diseases?page=1&limit=15"
```

### Filter by Tag
```bash
# Get articles tagged with 'exercise'
curl "http://localhost:8000/api/v1/tag/exercise?limit=10"
```

### Get Metadata
```bash
# List all categories
curl "http://localhost:8000/api/v1/categories"

# List all tags
curl "http://localhost:8000/api/v1/tags"

# Health check
curl "http://localhost:8000/api/v1/health"

# Statistics
curl "http://localhost:8000/api/v1/stats"
```

### Date Filtering
```bash
# Articles from specific date range
curl "http://localhost:8000/api/v1/?start_date=2025-07-01&end_date=2025-07-30"

# Recent articles with date filter
curl "http://localhost:8000/api/v1/latest?limit=10&start_date=2025-07-25"
```

---

## 🎯 **Quick Reference**

### Most Used Endpoints
1. **Get Articles**: `/api/v1/?page=1&limit=20`
2. **Search**: `/api/v1/search?q=your_query`
3. **News Category**: `/api/v1/news`
4. **Health Check**: `/api/v1/health`
5. **Categories List**: `/api/v1/categories`

### Available Categories
- `news` (96 articles)
- `diseases` (402 articles)  
- `food` (59 articles)
- `solutions`
- `audience`
- `blogs_and_opinions`

### Current Stats
- **Total Articles**: 649
- **Total Categories**: 7
- **Total Tags**: 54
- **Database**: SQLite with 649 health articles

---

## ⚠️ **Important Notes**

1. **All API endpoints require the `/api/v1/` prefix**
2. **Pagination**: Default limit is 20, maximum is 100
3. **Error Handling**: 404 for non-existent endpoints, 500 for server errors
4. **CORS**: Enabled for all origins
5. **Rate Limiting**: None currently implemented
6. **Authentication**: None required

## 🔧 **Development Tools**

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health
- **Debug Categories**: http://localhost:8000/api/v1/debug/categories

---

**Total Endpoints**: 25+ (including redirects and category variations)
