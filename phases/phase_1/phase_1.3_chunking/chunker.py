"""
Phase 1.3 - Sectional Factual Chunker

Converts each cleaned JSON fund file into ~8 self-contained factual
text chunks, optimized for embedding and retrieval.

Design principles:
1. Every chunk starts with "Fund: <name> | Category: <sub_category>"
   so the LLM always knows which fund the facts belong to.
2. Each chunk maps to one logical topic a user would ask about.
3. All numbers are presented with human-readable labels.
4. The source_url is appended to every chunk as a citation anchor.

Sections produced per fund:
  1. basics_and_objective
  2. costs_and_benchmarks
  3. investment_rules
  4. fund_management
  5. annualized_returns_and_rankings
  6. sip_returns
  7. absolute_returns
  8. risk_metrics
"""

import json
import os
from datetime import datetime
from typing import Dict, List


# ---------------------------------------------------------------------------
# Human-readable label maps
# ---------------------------------------------------------------------------

RETURN_LABELS = {
    "return1d": "1 Day",
    "return1w": "1 Week",
    "return1m": "1 Month",
    "return3m": "3 Months",
    "return6m": "6 Months",
    "return9m": "9 Months",
    "return1y": "1 Year",
    "return2y": "2 Years",
    "return3y": "3 Years",
    "return4y": "4 Years",
    "return5y": "5 Years",
    "return7y": "7 Years",
    "return10y": "10 Years",
    "return_default": "Default Period",
    "return_since_created": "Since Inception",
}

CAT_RETURN_LABELS = {
    "cat_return3m": "Category Avg 3 Months",
    "cat_return6m": "Category Avg 6 Months",
    "cat_return1y": "Category Avg 1 Year",
    "cat_return3y": "Category Avg 3 Years",
    "cat_return5y": "Category Avg 5 Years",
    "cat_return10y": "Category Avg 10 Years",
}

RANK_LABELS = {
    "rank3m": "3 Month Rank",
    "rank6m": "6 Month Rank",
    "rank1yr": "1 Year Rank",
    "rank3yr": "3 Year Rank",
    "rank5yr": "5 Year Rank",
    "rank10yr": "10 Year Rank",
}

INDEX_RETURN_LABELS = {
    "index_return1y": "Benchmark Index 1 Year",
    "index_return3y": "Benchmark Index 3 Years",
    "index_return5y": "Benchmark Index 5 Years",
}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _header(fund):
    """Build the context prefix that starts every chunk."""
    return "Fund: {} | Category: {} | Sub-Category: {}".format(
        fund.get("fund_name", "Unknown"),
        fund.get("category", ""),
        fund.get("sub_category", ""),
    )


def _citation(fund):
    """Build the citation footer appended to every chunk."""
    source = fund.get("source_url", "")
    updated = fund.get("last_updated", "")
    return "Source: {} | Last Updated: {}".format(source, updated)


def _format_return_value(val):
    """Format a return value to 2 decimal places with a % sign."""
    if isinstance(val, (int, float)):
        return "{:.2f}%".format(val)
    return str(val)


# ---------------------------------------------------------------------------
# Section builders — each returns a single text chunk string
# ---------------------------------------------------------------------------

def _chunk_basics(fund):
    """Section 1: Basics & Objective"""
    lines = [
        _header(fund),
        "Section: Basics & Objective",
        "",
        "Fund Name: {}".format(fund.get("fund_name", "")),
        "Fund House: {}".format(fund.get("fund_house", "")),
        "Category: {}".format(fund.get("category", "")),
        "Sub-Category: {}".format(fund.get("sub_category", "")),
        "Plan Type: {}".format(fund.get("plan_type", "")),
        "Scheme Type: {}".format(fund.get("scheme_type", "")),
        "Launch Date: {}".format(fund.get("launch_date", "")),
        "Investment Objective: {}".format(fund.get("description", "")),
        "Holdings Count: {}".format(fund.get("holdings_count", "")),
        "Portfolio Turnover: {}".format(fund.get("portfolio_turnover", "")),
        "",
        _citation(fund),
    ]
    return "\n".join(lines)


def _chunk_costs(fund):
    """Section 2: Costs & Benchmarks"""
    lines = [
        _header(fund),
        "Section: Costs & Benchmarks",
        "",
        "NAV: Rs. {} (as of {})".format(fund.get("nav", ""), fund.get("nav_date", "")),
        "AUM: {}".format(fund.get("aum", "")),
        "Expense Ratio: {}".format(fund.get("expense_ratio", "")),
        "Exit Load: {}".format(fund.get("exit_load", "")),
        "Stamp Duty: {}".format(fund.get("stamp_duty", "")),
        "Benchmark: {}".format(fund.get("benchmark", "")),
        "Groww Rating: {}".format(fund.get("groww_rating", "")),
    ]
    if fund.get("crisil_rating"):
        lines.append("CRISIL Rating: {}".format(fund["crisil_rating"]))
    lines.append("")
    lines.append(_citation(fund))
    return "\n".join(lines)


def _chunk_investment_rules(fund):
    """Section 3: Investment Rules"""
    lines = [
        _header(fund),
        "Section: Investment Rules",
        "",
        "Minimum SIP Investment: {}".format(fund.get("min_sip_investment", "")),
        "Minimum Lumpsum Investment: {}".format(fund.get("min_lumpsum_investment", "")),
        "Minimum Withdrawal: {}".format(fund.get("min_withdrawal", "")),
        "Lock-in Period: {}".format(fund.get("lock_in_period", "")),
        "SIP Allowed: {}".format("Yes" if fund.get("sip_allowed") else "No"),
        "Lumpsum Allowed: {}".format("Yes" if fund.get("lumpsum_allowed") else "No"),
    ]

    # ELSS-specific additional details
    additional = fund.get("additional_details", {})
    if additional:
        if additional.get("lock_in_yrs"):
            lines.append("Tax-Saver Lock-in: {} year(s)".format(additional["lock_in_yrs"]))

    lines.append("")
    lines.append(_citation(fund))
    return "\n".join(lines)


def _chunk_fund_management(fund):
    """Section 4: Fund Management"""
    lines = [
        _header(fund),
        "Section: Fund Management",
        "",
    ]
    managers = fund.get("fund_managers", [])
    if not managers:
        lines.append("Fund Manager information not available.")
    else:
        for i, mgr in enumerate(managers, 1):
            lines.append("Fund Manager {}: {}".format(i, mgr.get("name", "")))
            if mgr.get("managing_since"):
                # Parse ISO date to readable format
                try:
                    dt = datetime.fromisoformat(mgr["managing_since"].replace("Z", "+00:00"))
                    lines.append("  Managing Since: {}".format(dt.strftime("%B %Y")))
                except (ValueError, AttributeError):
                    lines.append("  Managing Since: {}".format(mgr["managing_since"]))
            if mgr.get("education"):
                lines.append("  Education: {}".format(mgr["education"]))
            if mgr.get("experience"):
                lines.append("  Experience: {}".format(mgr["experience"]))
            lines.append("")

    lines.append(_citation(fund))
    return "\n".join(lines)


def _chunk_annualized_returns(fund):
    """Section 5: Annualized Returns & Rankings"""
    data = fund.get("annualized_returns", {})
    lines = [
        _header(fund),
        "Section: Annualized Returns & Rankings",
        "",
    ]

    # Fund returns
    lines.append("-- Fund Annualized Returns (CAGR) --")
    for key, label in RETURN_LABELS.items():
        if key in data:
            lines.append("  {}: {}".format(label, _format_return_value(data[key])))

    # Category average returns
    cat_lines = []
    for key, label in CAT_RETURN_LABELS.items():
        if key in data:
            cat_lines.append("  {}: {}".format(label, _format_return_value(data[key])))
    if cat_lines:
        lines.append("")
        lines.append("-- Category Average Returns --")
        lines.extend(cat_lines)

    # Rankings
    rank_lines = []
    for key, label in RANK_LABELS.items():
        if key in data:
            rank_lines.append("  {}: #{}".format(label, data[key]))
    if rank_lines:
        lines.append("")
        lines.append("-- Category Rankings (lower is better) --")
        lines.extend(rank_lines)

    # Benchmark index returns
    idx_lines = []
    for key, label in INDEX_RETURN_LABELS.items():
        if key in data:
            idx_lines.append("  {}: {}".format(label, _format_return_value(data[key])))
    if idx_lines:
        lines.append("")
        lines.append("-- Benchmark Index Returns --")
        lines.extend(idx_lines)

    lines.append("")
    lines.append(_citation(fund))
    return "\n".join(lines)


def _chunk_sip_returns(fund):
    """Section 6: SIP Returns"""
    data = fund.get("sip_returns", {})
    lines = [
        _header(fund),
        "Section: SIP Returns (Annualized)",
        "",
    ]

    if not data:
        lines.append("SIP return data not available.")
    else:
        for key, label in RETURN_LABELS.items():
            if key in data:
                lines.append("  SIP Return {}: {}".format(label, _format_return_value(data[key])))

    lines.append("")
    lines.append(_citation(fund))
    return "\n".join(lines)


def _chunk_absolute_returns(fund):
    """Section 7: Absolute Returns"""
    data = fund.get("absolute_returns", {})
    lines = [
        _header(fund),
        "Section: Absolute (Total) Returns",
        "",
    ]

    if not data:
        lines.append("Absolute return data not available.")
    else:
        # Fund absolute returns
        lines.append("-- Fund Absolute Returns --")
        for key, label in RETURN_LABELS.items():
            if key in data:
                lines.append("  {}: {}".format(label, _format_return_value(data[key])))

        # Category absolute returns (if present)
        cat_lines = []
        for key, label in CAT_RETURN_LABELS.items():
            if key in data:
                cat_lines.append("  {}: {}".format(label, _format_return_value(data[key])))
        if cat_lines:
            lines.append("")
            lines.append("-- Category Average Absolute Returns --")
            lines.extend(cat_lines)

    lines.append("")
    lines.append(_citation(fund))
    return "\n".join(lines)


def _chunk_risk_metrics(fund):
    """Section 8: Risk Metrics & Riskometer"""
    data = fund.get("annualized_returns", {})
    lines = [
        _header(fund),
        "Section: Risk Metrics & Riskometer",
        "",
        "Risk Classification (Riskometer): {}".format(fund.get("risk_classification", "Not available")),
        "Risk Level: {}".format(data.get("risk", "Not available")),
    ]

    risk_fields = {
        "sharpe_ratio": "Sharpe Ratio",
        "beta": "Beta",
        "standard_deviation": "Standard Deviation",
        "alpha": "Alpha",
        "sortino_ratio": "Sortino Ratio",
        "information_ratio": "Information Ratio",
        "mean_return": "Mean Return",
        "risk_rating": "Risk Rating (numeric)",
    }

    for key, label in risk_fields.items():
        if key in data:
            val = data[key]
            if isinstance(val, float):
                lines.append("{}: {:.4f}".format(label, val))
            else:
                lines.append("{}: {}".format(label, val))

    lines.append("")
    lines.append(_citation(fund))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main chunking pipeline
# ---------------------------------------------------------------------------

def chunk_fund(fund_data):
    # type: (Dict) -> List[Dict]
    """
    Given a cleaned fund JSON dict, produce a list of chunk dicts.
    Each chunk dict has:
      - section: str (section identifier)
      - text: str (the factual text block)
      - metadata: dict (fund_name, sub_category, source_url, last_updated)
    """
    section_builders = [
        ("basics_and_objective", _chunk_basics),
        ("costs_and_benchmarks", _chunk_costs),
        ("investment_rules", _chunk_investment_rules),
        ("fund_management", _chunk_fund_management),
        ("annualized_returns_and_rankings", _chunk_annualized_returns),
        ("sip_returns", _chunk_sip_returns),
        ("absolute_returns", _chunk_absolute_returns),
        ("risk_metrics", _chunk_risk_metrics),
    ]

    metadata = {
        "fund_name": fund_data.get("fund_name", ""),
        "sub_category": fund_data.get("sub_category", ""),
        "source_url": fund_data.get("source_url", ""),
        "last_updated": fund_data.get("last_updated", ""),
    }

    chunks = []
    for section_id, builder_fn in section_builders:
        text = builder_fn(fund_data)
        chunks.append({
            "section": section_id,
            "text": text,
            "metadata": metadata,
        })

    return chunks


def run_chunker():
    """Read all cleaned JSON files, chunk them, and save output."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Cleaned data is in the phase_1.2 sibling directory
    clean_dir = os.path.join(script_dir, "..", "phase_1.2_scraping", "cleaned_data")
    output_dir = os.path.join(script_dir, "chunks")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Phase 1.3: Sectional Factual Chunker")
    print("=" * 60)

    json_files = sorted([f for f in os.listdir(clean_dir) if f.endswith(".json")])

    total_chunks = 0
    for filename in json_files:
        filepath = os.path.join(clean_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            fund_data = json.load(f)

        chunks = chunk_fund(fund_data)
        total_chunks += len(chunks)

        # Save chunks as JSON array
        out_name = filename.replace(".json", "_chunks.json")
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False, default=str)

        print("  [OK] {} -> {} chunks".format(filename, len(chunks)))

        # Print a sample chunk for verification
        print("       Sample (Section 1, first 120 chars):")
        preview = chunks[0]["text"][:120].replace("\n", " | ")
        print("       '{}'...".format(preview))

    print("\nTotal: {} files -> {} chunks".format(len(json_files), total_chunks))
    print("Chunks saved to: {}".format(os.path.abspath(output_dir)))


if __name__ == "__main__":
    run_chunker()
