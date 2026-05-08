# Phase 1.2: Scraping & Content Extraction - Documentation

## Summary
Phase 1.2 implements the data extraction pipeline that scrapes mutual fund scheme data from Groww.in. The scraper targets the `__NEXT_DATA__` JSON payload embedded in Groww's Next.js rendered pages, which contains all structured fund information without requiring browser-based scraping.

## Files
- `config.py` - Configuration file with target URLs, scraper settings, and scheme metadata.
- `scraper.py` - Main scraper module with extraction logic and HTML fallback.
- `raw_data/` - Output directory containing extracted JSON data for each scheme.

## How It Works
1. The scraper fetches the raw HTML from each Groww URL using `requests`.
2. It locates the `<script id="__NEXT_DATA__">` tag in the HTML, which is a Next.js standard containing all page props as JSON.
3. The structured fund data lives under `props.pageProps.mfServerSideData`.
4. Key facts are extracted and saved as individual JSON files per scheme.

## Extracted Data Fields
| Field | Example (HDFC Mid Cap) |
|---|---|
| Fund Name | HDFC Mid Cap Fund Direct Growth |
| NAV | 218.745 (as of 05-May-2026) |
| Expense Ratio | 0.8% |
| Exit Load | 1% if redeemed within 1 year |
| AUM | 85,357.92 Cr |
| Benchmark | NIFTY Midcap 150 Total Return Index |
| Min SIP | Rs. 100 |
| Min Lumpsum | Rs. 100 |
| Category | Equity - Mid Cap |
| Fund Manager | Chirag Setalvad |
| Groww Rating | 5/5 |

## Running the Scraper
```bash
cd phases/phase_1/phase_1.2_scraping
..\venv\Scripts\python.exe scraper.py
```

## Known Limitations
- Data is sourced from Groww (aggregator), not directly from HDFC AMC official website.
- If Groww changes their `__NEXT_DATA__` structure, the extraction logic will need updating.
- The HTML fallback parser is basic and may miss structured data fields.
