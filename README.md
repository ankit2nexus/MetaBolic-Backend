# 🏥 Metabolical Backend API - Clean & Simplified

A FastAPI-based backend for health articles with search, categorization, and pagination. 
**Simplified project structure for easy understanding and maintenance.**

## 📁 Project Structure

```
metabolical-backend/
├── app/                    # 🚀 Main application code
│   ├── main.py            # FastAPI application
│   ├── utils.py           # Database utilities
│   └── __init__.py        # Package initialization
├── config/                # ⚙️ Configuration files
│   └── category_keywords.yml
├── data/                  # 💾 Database and cache
│   └── articles.db        # SQLite database
├── scrapers/              # 🕷️ Web scrapers
├── tests/                 # 🧪 Test files
├── docs/                  # 📚 Documentation
├── start.py              # 🎯 Simple startup script
├── requirements-clean.txt # 📦 Clean dependencies
└── README.md             # 📖 This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-clean.txt
```

### 2. Start the Server
```bash
python start.py
```

### 3. Access the API
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 API Endpoints

All endpoints are under `/api/v1` prefix:

### Core Endpoints
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - API statistics

### Article Endpoints
- `GET /api/v1/articles/` - Get paginated articles
- `GET /api/v1/articles/latest` - Get latest articles
- `GET /api/v1/articles/search?q={query}` - **Search articles** (primary)
- `GET /api/v1/articles/{category}` - Get articles by category
- `GET /api/v1/articles/{category}/{subcategory}` - Get articles by subcategory

### Category & Organization
- `GET /api/v1/categories` - Get all categories
- `GET /api/v1/search?q={query}` - Search articles (legacy)

## 🔍 Search Examples

```bash
# Search for diabetes articles
curl "http://localhost:8000/api/v1/articles/search?q=diabetes&limit=10"

# Get articles by category
curl "http://localhost:8000/api/v1/articles/diseases?page=1&limit=20"

# Get latest articles
curl "http://localhost:8000/api/v1/articles/latest?limit=5"
```

## 📊 Response Format

```json
{
  "articles": [
    {
      "id": 123,
      "title": "Understanding Diabetes",
      "summary": "A comprehensive guide...",
      "url": "https://source.com/article",
      "source": "Health News",
      "date": "2025-07-30T10:00:00",
      "category": "diseases",
      "subcategory": "diabetes",
      "tags": ["health", "diabetes"]
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "total_pages": 8,
  "has_next": true,
  "has_previous": false
}
```

## 🛠️ Development

### Project Structure Benefits
✅ **Single main.py** - No confusion between multiple main files  
✅ **Single utils.py** - All utilities in one place  
✅ **Clear directories** - Organized by function  
✅ **Simple startup** - One command to run  
✅ **Clean dependencies** - Only essential packages  

### What Was Cleaned Up
❌ Removed: `main_fast.py`, `main_lightning.py`, `main_backup.py`  
❌ Removed: `utils_fast.py`, `utils_backup.py`, `utils_original.py`  
❌ Removed: `backup_20250729_145944/` folder  
❌ Removed: Multiple optimization and performance files  
❌ Removed: Complex startup scripts  

### Configuration
- **Database**: SQLite database in `data/articles.db`
- **Categories**: Configured in `config/category_keywords.yml`
- **Logging**: INFO level by default
- **CORS**: Enabled for all origins (development)

## 🧪 Testing

```bash
# Run tests
cd tests
python final_verification_test.py
python test_endpoints.py
```

## 📝 Available Categories

- `diseases` - Medical conditions and health issues
- `news` - Health news and recent developments  
- `solutions` - Treatment and prevention methods
- `food` - Nutrition and dietary information
- `audience` - Target demographic content
- `blogs_and_opinions` - Expert opinions and patient stories

## 🔧 Troubleshooting

### Common Issues

1. **Database not found**: Make sure `data/articles.db` exists
2. **Port already in use**: Change port in `start.py` or kill existing process
3. **Import errors**: Install dependencies with `pip install -r requirements-clean.txt`

### Logs
Check the console output for detailed error messages and performance information.

## 📈 Performance Features

- ✅ SQLite connection pooling
- ✅ Database indexes for faster queries
- ✅ In-memory caching for frequently accessed data
- ✅ Optimized pagination
- ✅ Gzip compression for responses

---

**🎯 This simplified structure makes the project much easier to understand, maintain, and extend while preserving all functionality.**
