# Phase 1.3: Sectional Factual Chunking - Documentation

## Summary
Phase 1.3 transforms the cleaned JSON fund data into structured, self-contained text blocks ("chunks") optimized for vector embedding and semantic retrieval. Each fund produces exactly 8 chunks.

## Files
- `chunker.py` - Main chunker script that reads cleaned JSON and produces text chunks.
- `chunks/` - Output directory containing one `*_chunks.json` file per fund.

## Chunking Strategy

### Why not RecursiveCharacterTextSplitter?
Our data is **structured JSON**, not unstructured prose. A generic character-based splitter would:
- Fragment keys from their values (e.g., `expense_ratio` separated from `0.8%`)
- Mix unrelated facts into a single chunk (manager bio + return stats)
- Lose fund identity context after the first chunk

### Sectional Factual Chunking
Instead, we split by **logical topic groups**:

| # | Section | User Question Example |
|---|---|---|
| 1 | Basics & Objective | "What does this fund invest in?" |
| 2 | Costs & Benchmarks | "What is the expense ratio?" |
| 3 | Investment Rules | "Is there a lock-in for ELSS?" |
| 4 | Fund Management | "Who manages the Mid Cap fund?" |
| 5 | Annualized Returns & Rankings | "5-year return? Category rank?" |
| 6 | SIP Returns | "What's the SIP return for 3 years?" |
| 7 | Absolute Returns | "How much did Rs.1L grow in 5 years?" |
| 8 | Risk Metrics | "What is the Sharpe ratio?" |

### Context Injection
Every chunk starts with:
```
Fund: HDFC Mid Cap Fund Direct Growth | Category: Equity | Sub-Category: Mid Cap
```
And ends with:
```
Source: https://groww.in/... | Last Updated: 2026-05-06T22:45:45
```

This ensures the LLM always knows which fund the data belongs to and can cite the source.

## Output
- 5 funds x 8 sections = **40 total chunks**
- Each chunk is a dict with `section`, `text`, and `metadata` fields.

## Running
```bash
cd phases/phase_1/phase_1.3_chunking
..\venv\Scripts\python.exe chunker.py
```
