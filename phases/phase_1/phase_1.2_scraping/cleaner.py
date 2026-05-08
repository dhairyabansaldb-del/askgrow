"""
Phase 1.2 - Data Cleaner (v2)
Transforms raw scraped JSON into clean, chatbot-friendly data.

Design principle: Keep EVERYTHING a retail investor or support agent
could plausibly ask about. Only strip internal Groww platform noise.

REMOVED (true noise):
- Internal Groww IDs: scheme_code, plan_id, person_id, search_id inside fund managers
- The massive funds_managed[] arrays (30-45 OTHER funds per manager, irrelevant to THIS fund)
- The entirely-null second block in return_stats[]
- All null-valued fields inside return/SIP return objects (declutter)
- VRO internal analytics fields (vro_return_ytd, vro_modified_ts, etc.)
- Scraper metadata (_raw_next_data_keys, extraction_method, configured_category)
- max_sip_investment: 999999999 (meaningless placeholder)
- super_category (just the fund name repeated)

KEPT (all user-facing facts):
- Fund identity, category, plan type, launch date, description
- NAV + date, AUM, expense ratio, exit load, benchmark
- Min SIP, min lumpsum, min withdrawal, lock-in, stamp duty
- Groww rating, CRISIL rating, risk level (nfo_risk)
- Fund manager name + education + experience + managing_since
- Full annualized return_stats (1d through 10y + since inception)
- Risk metrics (sharpe, beta, alpha, std dev, sortino, information ratio)
- Category avg returns + rank (useful for "how does this fund compare?")
- SIP returns (users ask "what's the SIP return for 5 years?")
- Simple/absolute returns
- Holdings count, portfolio turnover
- SID URL, brochure link, scheme info link
- Source URL (citation link), additional_details (lock-in specifics for ELSS)

HUMANIZED (formatting for readability):
- AUM: 85357.92 -> "Rs. 85,357.92 Cr"
- Lock-in: {years:3, months:0, days:0} -> "3 year(s)"
- Expense ratio: "0.8" -> "0.8%"
- Groww rating: 5 -> "5 out of 5"
"""

import json
import os
from datetime import datetime


def format_aum(aum_value):
    """Convert raw AUM number to human-readable string."""
    if not aum_value:
        return "Not available"
    return "Rs. {:,.2f} Cr".format(aum_value)


def format_lock_in(lock_in):
    """Convert lock-in dict to a human-readable string."""
    if not lock_in or all(v is None or v == 0 for v in lock_in.values()):
        return "No lock-in period"
    parts = []
    if lock_in.get("years"):
        parts.append("{} year(s)".format(lock_in["years"]))
    if lock_in.get("months"):
        parts.append("{} month(s)".format(lock_in["months"]))
    if lock_in.get("days"):
        parts.append("{} day(s)".format(lock_in["days"]))
    return ", ".join(parts) if parts else "No lock-in period"


def strip_nulls(d):
    """Recursively remove keys whose value is None from a dict."""
    if isinstance(d, dict):
        return {k: strip_nulls(v) for k, v in d.items() if v is not None}
    if isinstance(d, list):
        return [strip_nulls(i) for i in d if i is not None]
    return d


def clean_return_block(raw_block):
    """
    Clean a single return stats dict:
    - Remove all null fields
    - Remove internal IDs (scheme_code, plan_id)
    - Remove VRO fields
    - Keep everything else (returns, risk metrics, category comparisons, ranks)
    """
    if not raw_block or not isinstance(raw_block, dict):
        return {}

    drop_keys = {"scheme_code", "plan_id",
                 "vro_return_ytd", "vro_return9m", "vro_return2y",
                 "vro_return4y", "vro_return_date", "vro_modified_ts",
                 "vro_row_number"}

    cleaned = {}
    for k, v in raw_block.items():
        if k in drop_keys:
            continue
        if v is None:
            continue
        cleaned[k] = v
    return cleaned


def clean_fund_managers(raw_managers):
    """
    Keep name, education, experience, managing_since.
    Remove the massive funds_managed[] list and internal IDs.
    """
    cleaned = []
    for mgr in raw_managers:
        entry = {
            "name": mgr.get("person_name", ""),
            "managing_since": mgr.get("date_from", ""),
            "education": mgr.get("education", ""),
            "experience": mgr.get("experience", ""),
        }
        # Remove empty strings
        entry = {k: v for k, v in entry.items() if v}
        cleaned.append(entry)
    return cleaned


def clean_fund_data(raw):
    """Transform raw scraped JSON into clean, chatbot-ready data."""

    # --- Identity ---
    cleaned = {
        "fund_name": raw.get("fund_name", ""),
        "fund_house": raw.get("fund_house", ""),
        "category": raw.get("category", ""),
        "sub_category": raw.get("sub_category", ""),
        "plan_type": raw.get("plan_type", ""),
        "scheme_type": raw.get("scheme_type", ""),
        "launch_date": raw.get("launch_date", ""),
        "description": raw.get("description", ""),
    }

    # --- Core metrics (humanized) ---
    cleaned["nav"] = raw.get("nav", "")
    cleaned["nav_date"] = raw.get("nav_date", "")
    cleaned["expense_ratio"] = "{}%".format(raw["expense_ratio"]) if raw.get("expense_ratio") else ""
    cleaned["exit_load"] = raw.get("exit_load", "Nil").strip() if raw.get("exit_load") else "Nil"
    cleaned["aum"] = format_aum(raw.get("aum"))
    cleaned["benchmark"] = raw.get("benchmark_name", "") or raw.get("benchmark", "")

    # --- Investment details ---
    cleaned["min_sip_investment"] = "Rs. {}".format(raw["min_sip_investment"]) if raw.get("min_sip_investment") else ""
    cleaned["min_lumpsum_investment"] = "Rs. {}".format(raw["min_investment_amount"]) if raw.get("min_investment_amount") else ""
    cleaned["min_withdrawal"] = "Rs. {}".format(raw["min_withdrawal"]) if raw.get("min_withdrawal") else ""
    cleaned["lock_in_period"] = format_lock_in(raw.get("lock_in"))
    cleaned["stamp_duty"] = raw.get("stamp_duty", "0.005%")
    cleaned["sip_allowed"] = raw.get("sip_allowed", "")
    cleaned["lumpsum_allowed"] = raw.get("lumpsum_allowed", "")

    # --- Ratings & Risk ---
    cleaned["groww_rating"] = "{} out of 5".format(raw["groww_rating"]) if raw.get("groww_rating") else "Not rated"
    if raw.get("crisil_rating"):
        cleaned["crisil_rating"] = raw["crisil_rating"]
    cleaned["risk_classification"] = raw.get("nfo_risk", "")

    # --- Fund Managers (trimmed, no funds_managed noise) ---
    cleaned["fund_managers"] = clean_fund_managers(raw.get("fund_manager_details", []))

    # --- Returns: Annualized (keep full detail, strip nulls + VRO) ---
    return_stats = raw.get("return_stats", [])
    if return_stats and isinstance(return_stats, list):
        # First block = actual data, second block = always null (discard)
        cleaned["annualized_returns"] = clean_return_block(return_stats[0])
    else:
        cleaned["annualized_returns"] = {}

    # --- SIP Returns (users ask "SIP return for 5 years?") ---
    sip_return = raw.get("sip_return", {})
    if sip_return:
        cleaned["sip_returns"] = clean_return_block(sip_return)

    # --- Absolute Returns ---
    simple_return = raw.get("simple_return", {})
    if simple_return:
        cleaned["absolute_returns"] = clean_return_block(simple_return)

    # --- Portfolio ---
    cleaned["holdings_count"] = raw.get("holdings_count", "")
    cleaned["portfolio_turnover"] = "{}%".format(raw["portfolio_turnover"]) if raw.get("portfolio_turnover") else ""

    # --- Additional details (ELSS lock-in specifics, etc.) ---
    if raw.get("additional_details"):
        cleaned["additional_details"] = strip_nulls(raw["additional_details"])

    # --- Document links ---
    cleaned["sid_url"] = raw.get("sid_url", "")
    if raw.get("brochure_link"):
        cleaned["brochure_link"] = raw["brochure_link"]
    if raw.get("scheme_info_link"):
        cleaned["scheme_info_link"] = raw["scheme_info_link"]

    # --- Citation & timestamp ---
    cleaned["source_url"] = raw.get("source_url", "")
    cleaned["last_updated"] = raw.get("scraped_at", datetime.now().isoformat())

    return cleaned


def run_cleaner():
    """Clean all raw JSON files and output to cleaned_data directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(script_dir, "raw_data")
    clean_dir = os.path.join(script_dir, "cleaned_data")
    os.makedirs(clean_dir, exist_ok=True)

    print("=" * 60)
    print("Phase 1.2: Data Cleaner v2")
    print("=" * 60)

    json_files = [f for f in os.listdir(raw_dir) if f.endswith(".json") and not f.startswith("_")]

    for filename in sorted(json_files):
        filepath = os.path.join(raw_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)

        cleaned = clean_fund_data(raw)

        out_path = os.path.join(clean_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False, default=str)

        raw_size = os.path.getsize(filepath)
        clean_size = os.path.getsize(out_path)
        reduction = ((raw_size - clean_size) / raw_size) * 100

        print("  [OK] {}".format(filename))
        print("       Raw: {:,} bytes -> Cleaned: {:,} bytes ({:.0f}% reduction)".format(
            raw_size, clean_size, reduction))

    print("\nCleaned files saved to: {}".format(clean_dir))


if __name__ == "__main__":
    run_cleaner()
