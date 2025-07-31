# Get all articles (paginated)
GET /api/v1/articles/
GET /api/v1/articles/?page=1&limit=20&sort_by=desc

# Get latest articles
GET /api/v1/articles/latest
GET /api/v1/articles/latest?limit=10

# Search articles
GET /api/v1/articles/search?q={query}
GET /api/v1/articles/search?q=diabetes&page=1&limit=20

# Get articles by category
GET /api/v1/articles/{category}
GET /api/v1/articles/news
GET /api/v1/articles/diseases?page=1&limit=10

# Get articles by category and subcategory
GET /api/v1/articles/{category}/{subcategory}
GET /api/v1/articles/diseases/diabetes