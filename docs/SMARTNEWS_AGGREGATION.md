# SmartNews-Style Health News Aggregation

This project now includes comprehensive news aggregation similar to SmartNews, while maintaining all existing API endpoints.

## New Features Added

### 1. Comprehensive News Scraper (`comprehensive_news_scraper.py`)
- **Major News Outlets**: BBC Health, Reuters Health, CNN Health, Associated Press, NPR, ABC News
- **Health-Specific Sources**: WebMD, Healthline, Medical News Today, Health.com, Everyday Health
- **Government Sources**: CDC, NIH, WHO, FDA
- **Google News Integration**: Health-specific topic searches
- **NewsAPI Integration**: Multiple health-related queries (requires API key)

### 2. Social Media Scraper (`social_media_scraper.py`)
- **Reddit Health Communities**: r/Health, r/HealthyFood, r/nutrition, r/MentalHealth, r/medicine, r/science
- **YouTube Health Channels**: TED-Ed Health, Mayo Clinic, Cleveland Clinic
- **Health Blogs**: Medium Health Stories, Healthline Blog, Psychology Today

### 3. Master Aggregator (`smart_news_aggregator.py`)
- Runs all scrapers in sequence
- Provides comprehensive reporting
- Handles errors gracefully
- Supports quick updates (high-priority sources only)

## Usage

### Quick Start (Recommended)
```bash
# Run the master aggregator for comprehensive coverage
python scrapers/smart_news_aggregator.py

# For quick updates (high-priority sources only)
python scrapers/smart_news_aggregator.py --quick

# List available scrapers
python scrapers/smart_news_aggregator.py --list-scrapers
```

### Individual Scrapers
```bash
# Run comprehensive news scraper
python scrapers/comprehensive_news_scraper.py

# Run social media scraper
python scrapers/social_media_scraper.py

# Run existing enhanced health scraper
python scrapers/enhanced_health_scraper.py
```

## API Endpoints (Unchanged)

All existing endpoints continue to work with aggregated content:

- `GET /articles/latest` - Latest articles from all sources
- `GET /articles/search?q=health` - Search across all aggregated content
- `GET /articles/tag/latest` - Trending content from all sources
- `GET /articles/category/news` - Categorized content
- `GET /articles/stats` - Statistics including new sources

## Configuration

### NewsAPI (Optional but Recommended)
1. Get a free API key from [newsapi.org](https://newsapi.org/)
2. Update the `newsapi_key` in `comprehensive_news_scraper.py`:
   ```python
   self.newsapi_key = "your_actual_api_key_here"
   ```

### Features Enabled
- ✅ **Multi-source aggregation** from 20+ reliable health news sources
- ✅ **Smart categorization** using AI-like keyword analysis
- ✅ **Social media integration** for community discussions and viral content
- ✅ **International coverage** including Indian health news
- ✅ **Content scoring** for news relevance and trending potential
- ✅ **URL validation** to ensure all links are accessible
- ✅ **Duplicate detection** to avoid repeated content

## Database Schema Updates

The new scrapers add these optional fields to existing articles:
- `news_score` - Relevance score for news content (0.0 to 1.0)
- `trending_score` - Viral/trending potential (0.0 to 1.0)
- `social_score` - Social media engagement potential
- Enhanced `tags` including: `smartnews_aggregated`, `trending`, `community_discussion`, `educational_content`

## Content Sources

### Major News Networks
- BBC Health, Reuters Health, CNN Health, Associated Press Health, NPR Health, ABC News Health

### Health-Specific Media
- WebMD, Healthline, Medical News Today, Health.com, Everyday Health

### Government & Institutional
- CDC, NIH, WHO, FDA, Indian Ministry of Health

### Social & Community
- Reddit health communities, YouTube health education, Medium health stories

### News Aggregators
- Google News health topics, NewsAPI health queries

## Scheduling (Recommended)

Set up automated runs for continuous updates:

```bash
# Add to crontab for automatic updates
# Run comprehensive update twice daily
0 6,18 * * * /usr/bin/python3 /path/to/scrapers/smart_news_aggregator.py

# Run quick updates every 4 hours
0 */4 * * * /usr/bin/python3 /path/to/scrapers/smart_news_aggregator.py --quick
```

## Performance

- **Comprehensive run**: ~5-10 minutes, 100-300 articles
- **Quick run**: ~2-3 minutes, 50-150 articles
- **Memory usage**: <100MB during execution
- **Database growth**: ~50-100MB per month with daily runs

## Troubleshooting

### Common Issues
1. **No articles saved**: Check internet connection and RSS feed availability
2. **NewsAPI not working**: Verify API key and rate limits
3. **Reddit content blocked**: Some regions may block Reddit access
4. **Slow performance**: Use `--quick` flag for faster updates

### Logs
Check the console output for detailed information about:
- Articles found and saved per source
- Failed sources and error messages
- Performance metrics and timing

## Integration Notes

- **Zero API changes**: All existing endpoints work exactly the same
- **Backward compatible**: Existing database schema is preserved
- **Additive only**: New features are added without breaking existing functionality
- **Source attribution**: All articles include proper source information
