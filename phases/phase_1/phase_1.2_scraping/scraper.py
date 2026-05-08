"""
Phase 1.2 - Scraper Module
Extracts factual mutual fund data from Groww scheme pages.

Since Groww pages are heavily JavaScript-rendered (Next.js), static HTTP scraping
captures mostly boilerplate. This scraper targets the __NEXT_DATA__ JSON payload
embedded in the page source, which contains all the structured fund data.

If __NEXT_DATA__ is not available, it falls back to BeautifulSoup HTML parsing.
"""

import json
import os
import re
import time
from typing import Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import SCHEME_URLS, REQUEST_TIMEOUT, REQUEST_DELAY, USER_AGENT, RAW_DATA_DIR


def get_page_html(url: str) -> str:
    """Fetch the raw HTML of a Groww mutual fund page."""
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.text


def extract_next_data(html: str) -> Optional[dict]:
    """
    Groww is a Next.js app. It embeds structured data in a
    <script id="__NEXT_DATA__"> tag as JSON. This is the richest
    data source and avoids DOM parsing entirely.
    """
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
    if script_tag and script_tag.string:
        try:
            return json.loads(script_tag.string)
        except json.JSONDecodeError:
            return None
    return None


def extract_fund_facts_from_next_data(next_data: dict, url: str) -> dict:
    """
    Parse the __NEXT_DATA__ JSON to extract structured mutual fund facts.
    Groww stores all fund data under props.pageProps.mfServerSideData.
    """
    facts = {
        "source_url": url,
        "scraped_at": datetime.now().isoformat(),
        "extraction_method": "__NEXT_DATA__",
    }

    try:
        page_props = next_data.get("props", {}).get("pageProps", {})
        fd = page_props.get("mfServerSideData", {})

        if not fd:
            facts["extraction_error"] = "mfServerSideData key not found"
            return facts

        # Core identity
        facts["fund_name"] = fd.get("scheme_name", "")
        facts["fund_house"] = fd.get("fund_house", "")
        facts["amc"] = fd.get("amc", "")
        facts["category"] = fd.get("category", "")
        facts["sub_category"] = fd.get("sub_category", "")
        facts["super_category"] = fd.get("super_category", "")
        facts["plan_type"] = fd.get("plan_type", "")
        facts["scheme_type"] = fd.get("scheme_type", "")
        facts["isin"] = fd.get("isin", "")
        facts["scheme_code"] = fd.get("scheme_code", "")
        facts["launch_date"] = fd.get("launch_date", "")

        # NAV
        facts["nav"] = fd.get("nav", "")
        facts["nav_date"] = fd.get("nav_date", "")

        # Key financial metrics
        facts["expense_ratio"] = fd.get("expense_ratio", "")
        facts["exit_load"] = fd.get("exit_load", "")
        facts["aum"] = fd.get("aum", "")
        facts["benchmark"] = fd.get("benchmark", "")
        facts["benchmark_name"] = fd.get("benchmark_name", "")

        # Investment limits
        facts["min_investment_amount"] = fd.get("min_investment_amount", "")
        facts["min_sip_investment"] = fd.get("min_sip_investment", "")
        facts["max_sip_investment"] = fd.get("max_sip_investment", "")
        facts["sip_multiplier"] = fd.get("sip_multiplier", "")
        facts["purchase_multiplier"] = fd.get("purchase_multiplier", "")
        facts["min_withdrawal"] = fd.get("min_withdrawal", "")

        # Lock-in & stamp duty
        facts["lock_in"] = fd.get("lock_in", "")
        facts["stamp_duty"] = fd.get("stamp_duty", "")

        # Ratings
        facts["groww_rating"] = fd.get("groww_rating", "")
        facts["crisil_rating"] = fd.get("crisil_rating", "")
        facts["nfo_risk"] = fd.get("nfo_risk", "")

        # Fund managers
        facts["fund_manager"] = fd.get("fund_manager", "")
        facts["fund_manager_details"] = fd.get("fund_manager_details", [])

        # Returns data
        facts["return_stats"] = fd.get("return_stats", {})
        facts["sip_return"] = fd.get("sip_return", {})
        facts["simple_return"] = fd.get("simple_return", {})

        # Description & objective
        facts["description"] = fd.get("description", "")

        # Portfolio
        facts["portfolio_turnover"] = fd.get("portfolio_turnover", "")
        facts["holdings_count"] = len(fd.get("holdings", []))

        # Document links
        facts["sid_url"] = fd.get("sid_url", "")
        facts["brochure_link"] = fd.get("brochure_link", "")
        facts["scheme_info_link"] = fd.get("scheme_info_link", "")

        # Additional details (often contains tax info)
        facts["additional_details"] = fd.get("additional_details", {})

        # Flags
        facts["sip_allowed"] = fd.get("sip_allowed", "")
        facts["lumpsum_allowed"] = fd.get("lumpsum_allowed", "")

    except Exception as e:
        facts["extraction_error"] = str(e)

    return facts


def extract_fund_facts_from_html(html: str, url: str) -> dict:
    """
    Fallback: Parse visible text from the HTML when __NEXT_DATA__ is unavailable.
    Extracts all text content, stripping navigation and footer boilerplate.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove nav, footer, script, style tags
    for tag in soup.find_all(["nav", "footer", "script", "style", "noscript"]):
        tag.decompose()

    # Extract the main content text
    body = soup.find("body")
    text = body.get_text(separator="\n", strip=True) if body else ""

    # Clean up excessive whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = "\n".join(lines)

    return {
        "source_url": url,
        "scraped_at": datetime.now().isoformat(),
        "extraction_method": "html_fallback",
        "raw_text": cleaned_text,
    }


def scrape_scheme(scheme: dict) -> dict:
    """Scrape a single mutual fund scheme page."""
    url = scheme["url"]
    print(f"  Scraping: {scheme['name']}")
    print(f"  URL: {url}")

    html = get_page_html(url)

    # Try __NEXT_DATA__ first (preferred)
    next_data = extract_next_data(html)
    if next_data:
        print("  [OK] Found __NEXT_DATA__ JSON payload")
        facts = extract_fund_facts_from_next_data(next_data, url)
        # Also save the raw next_data for debugging
        facts["_raw_next_data_keys"] = list(next_data.get("props", {}).get("pageProps", {}).keys())
    else:
        print("  [WARN] __NEXT_DATA__ not found, falling back to HTML parsing")
        facts = extract_fund_facts_from_html(html, url)

    facts["scheme_slug"] = scheme["slug"]
    facts["configured_category"] = scheme["category"]
    return facts


def save_raw_data(facts: dict, output_dir: str):
    """Save extracted data as JSON to the raw_data directory."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{facts.get('scheme_slug', 'unknown')}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2, ensure_ascii=False, default=str)

    print(f"  [OK] Saved to {filepath}")
    return filepath


def run_scraper():
    """Main scraper entry point. Scrapes all configured schemes."""
    print("=" * 60)
    print("Phase 1.2: Mutual Fund Data Scraper")
    print(f"Target: {len(SCHEME_URLS)} HDFC schemes from Groww")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    # Resolve output directory relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "raw_data")

    results = []
    for i, scheme in enumerate(SCHEME_URLS):
        print(f"\n[{i + 1}/{len(SCHEME_URLS)}]")
        try:
            facts = scrape_scheme(scheme)
            filepath = save_raw_data(facts, output_dir)
            results.append({"scheme": scheme["name"], "status": "success", "file": filepath})
        except requests.exceptions.RequestException as e:
            print(f"  [FAIL] Network error: {e}")
            results.append({"scheme": scheme["name"], "status": "failed", "error": str(e)})
        except Exception as e:
            print(f"  [FAIL] Unexpected error: {e}")
            results.append({"scheme": scheme["name"], "status": "failed", "error": str(e)})

        # Respect rate limits
        if i < len(SCHEME_URLS) - 1:
            print(f"  Waiting {REQUEST_DELAY}s before next request...")
            time.sleep(REQUEST_DELAY)

    # Summary
    print("\n" + "=" * 60)
    print("Scraping Summary")
    print("=" * 60)
    success = sum(1 for r in results if r["status"] == "success")
    print(f"  Successful: {success}/{len(results)}")
    for r in results:
        status = "[OK]" if r["status"] == "success" else "[FAIL]"
        print(f"  {status} {r['scheme']}")

    # Save summary
    summary_path = os.path.join(output_dir, "_scrape_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(
            {"timestamp": datetime.now().isoformat(), "results": results},
            f, indent=2, ensure_ascii=False, default=str,
        )
    print(f"\nSummary saved to: {summary_path}")

    return results


if __name__ == "__main__":
    run_scraper()
