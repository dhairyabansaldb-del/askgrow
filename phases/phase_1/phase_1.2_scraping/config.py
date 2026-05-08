"""
Phase 1.2 - Configuration
Source URLs and scheme metadata for the HDFC Mutual Fund FAQ Assistant.
"""

# Target AMC
AMC_NAME = "HDFC Mutual Fund"
AMC_WEBSITE = "https://www.hdfcfund.com"

# Target Schemes with their Groww URLs
SCHEME_URLS = [
    {
        "name": "HDFC Mid-Cap Opportunities Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "slug": "hdfc-mid-cap-fund-direct-growth",
        "category": "Equity - Mid Cap",
    },
    {
        "name": "HDFC Flexi Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
        "slug": "hdfc-equity-fund-direct-growth",
        "category": "Equity - Flexi Cap",
    },
    {
        "name": "HDFC Focused 30 Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
        "slug": "hdfc-focused-fund-direct-growth",
        "category": "Equity - Focused",
    },
    {
        "name": "HDFC ELSS Tax Saver Fund Direct Plan Growth",
        "url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
        "slug": "hdfc-elss-tax-saver-fund-direct-plan-growth",
        "category": "Equity - ELSS",
    },
    {
        "name": "HDFC Large Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
        "slug": "hdfc-large-cap-fund-direct-growth",
        "category": "Equity - Large Cap",
    },
]

# Scraper Settings
REQUEST_TIMEOUT = 30  # seconds
REQUEST_DELAY = 2  # seconds between requests to avoid rate-limiting
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Output paths (relative to phase_1 root)
RAW_DATA_DIR = "phase_1.2_scraping/raw_data"
