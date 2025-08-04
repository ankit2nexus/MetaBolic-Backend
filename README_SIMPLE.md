# METABOLIC_BACKEND - Simplified Structure

A clean, health news API backend with automated scraping and URL validation.

## 📁 Simple File Structure

```
METABOLIC_BACKEND/
├── app/                           # Main application
│   ├── main.py                   # FastAPI application
│   ├── utils.py                  # Database & utility functions
│   ├── url_validator.py          # URL validation
│   ├── health_categories.yml     # Content categories
│   ├── scraper_config.py         # Scraper configuration
│   └── scrapers/                 # News scrapers
│       ├── master_health_scraper.py
│       ├── smart_news_aggregator.py
│       └── social_media_scraper.py
├── data/                         # Database storage
│   └── articles.db              # SQLite database
├── scripts/                     # Utility scripts
│   ├── cleanup_urls.py         # Clean problematic URLs
│   ├── check_urls.py           # Check URL status
│   ├── check_specific_urls.py  # Detailed URL checker
│   └── test_url_validation.py  # Test URL validation
├── deploy/                      # Deployment files
│   ├── docker-compose.yml      # Docker setup
│   ├── Dockerfile              # Container config
│   ├── nginx.conf              # Web server config
│   ├── render.yaml             # Render deployment
│   └── env.production          # Production environment
├── run.py                       # Simple command runner
├── requirements.txt             # Python dependencies
└── README_SIMPLE.md            # This file
```

## 🚀 Quick Start

### Run the API Server
```bash
python run.py api
```

### Run News Scraper
```bash
python run.py scraper
```

### Clean Database
```bash
python run.py clean
```

### Check URLs
```bash
python run.py check
```

## 📊 API Endpoints

- **Search**: `/api/v1/search?q=diabetes`
- **Categories**: `/api/v1/category/diseases`
- **Tags**: `/api/v1/tag/nutrition`
- **Health Check**: `/api/v1/health`
- **Stats**: `/api/v1/stats`

## 🔧 Configuration

All configuration is now centralized in the `app/` directory:
- `health_categories.yml` - Content categories
- `scraper_config.py` - Scraper settings
- `main.py` - API configuration

## 🛠️ Development

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Run API**: `python run.py api`
3. **Access docs**: http://localhost:8000/docs

## 🚢 Deployment

All deployment files are in the `deploy/` directory:
- Docker: `docker-compose -f deploy/docker-compose.yml up`
- Render: Uses `deploy/render.yaml`

## 🧹 Maintenance

- **Clean URLs**: `python run.py clean`
- **Check Status**: `python run.py check` 
- **Test Validation**: `python scripts/test_url_validation.py`

## ✨ Features

- ✅ Clean, validated URLs (no more example.com!)
- ✅ Real-time health news scraping
- ✅ Comprehensive search & filtering
- ✅ Automated content categorization
- ✅ Production-ready deployment

---

**Simple. Clean. Reliable.** 🏥
