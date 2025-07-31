# Performance Improvements for Metabolical Backend

## Problem
The backend was taking too much time to start due to:
1. Heavy ML dependencies (transformers, torch, sentence-transformers)
2. Database optimization running on startup
3. Synchronous operations blocking the startup

## Solutions Implemented

### 1. Fast Startup Mode
- **File**: `start_fast.py` / `start_fast.ps1`
- **Description**: Quick startup scripts that bypass heavy operations
- **Usage**: 
  ```bash
  python start_fast.py
  # or
  powershell .\start_fast.ps1
  ```

### 2. Minimal Dependencies
- **File**: `requirements-minimal.txt`
- **Description**: Lightweight requirements without ML libraries
- **Install**: `pip install -r requirements-minimal.txt`

### 3. Deferred Optimizations
- **Change**: Startup optimizations are now skipped
- **Alternative**: Use `/admin/optimize` endpoint to run optimizations manually
- **Benefit**: ~10-30 seconds faster startup

### 4. Lightweight Database Operations
- **Change**: Replaced heavy `ANALYZE` and `VACUUM` with `PRAGMA optimize`
- **Benefit**: Faster database initialization

## Quick Start (Fastest)

```bash
# Install minimal dependencies
pip install -r requirements-minimal.txt

# Start server (fast mode)
python start_fast.py
```

## Manual Optimization

After the server is running, trigger optimizations:
```bash
curl -X POST http://localhost:8000/admin/optimize
```

## Performance Comparison

| Mode | Startup Time | Features |
|------|-------------|----------|
| **Original** | 30-60s | Full ML features, auto-optimization |
| **Fast Mode** | 3-5s | Core API, manual optimization |
| **Minimal** | 1-3s | Basic functionality only |

## Recommended Workflow

1. **Development**: Use fast mode for quick iterations
2. **Production**: Install full requirements, run optimization manually
3. **Testing**: Use minimal mode for unit tests

## Available Endpoints

- `GET /health` - Quick health check
- `POST /admin/optimize` - Manual database optimization
- `GET /docs` - API documentation

## API Response Format

All paginated endpoints now return a flattened structure:

```json
{
  "articles": [...],
  "current_page": 1,
  "total_pages": 5,
  "total_items": 100,
  "items_per_page": 20,
  "has_next": true,
  "has_previous": false,
  "message": "Optional informative message when no data found"
}
```

**Previously** (nested structure):
```json
{
  "articles": [...],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 100,
    "items_per_page": 20,
    "has_next": true,
    "has_previous": false
  }
}
```

## Enhanced Error Handling

### Category/Subcategory Validation

**✅ Valid subcategory with no data** (HTTP 200):
```json
{
  "articles": [],
  "current_page": 1,
  "total_pages": 0,
  "total_items": 0,
  "items_per_page": 20,
  "has_next": false,
  "has_previous": false,
  "message": "No articles found for subcategory 'organic_food' in category 'food'. This subcategory exists but currently has no articles."
}
```

**❌ Invalid subcategory** (HTTP 404):
```json
{
  "detail": "Subcategory 'invalid_sub' not found in category 'food'. Available subcategories: ['nutrition_basics', 'organic_food', 'superfoods', ...]"
}
```

**❌ Invalid category** (HTTP 404):
```json
{
  "detail": "Category 'invalid_cat' not found. Available categories: ['diseases', 'solutions', 'food', 'blogs_and_opinions', ...]"
}
```

## Notes

- ML features will be loaded on-demand when needed
- Database indexes are still created automatically
- Connection pooling remains optimized
- All core API functionality is preserved