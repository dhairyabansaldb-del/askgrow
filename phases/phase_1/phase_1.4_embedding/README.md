# Phase 1.4: Embedding Generation - Documentation

## Summary
Phase 1.4 converts the 40 sectional text chunks (from Phase 1.3) into 384-dimensional vector embeddings using the `BAAI/bge-small-en-v1.5` model.

## Files
- `embedder.py` - Main script that loads chunks, generates embeddings, and saves output.
- `embeddings/all_fund_embeddings.json` - Output file containing all 40 records with text + vectors.

## Model Choice: `BAAI/bge-small-en-v1.5`
- **Size:** ~133 MB (lightweight, easy to deploy)
- **Dimensions:** 384
- **Retrieval Quality:** MTEB score ~63.0 (state-of-the-art for its size class)
- **Why not `all-MiniLM-L6-v2`?** bge-small has better semantic understanding of domain-specific terms (NAV, CAGR, AUM) and supports query-instruction prefixes.

## Asymmetric Query Design (Important for Phase 2)
The `bge` model family uses an **asymmetric** approach:

| Stage | Prefix | When Used |
|---|---|---|
| **Document Embedding** (this phase) | None — raw text is embedded as-is | During ingestion |
| **Query Embedding** (Phase 2 runtime) | `"Represent this sentence for searching relevant passages: "` | When user asks a question |

This constant is exported from `embedder.py` as `QUERY_INSTRUCTION` for Phase 2 to import.

## Output Format
Each record in `all_fund_embeddings.json`:
```json
{
  "id": "beb169653d92...",
  "section": "costs_and_benchmarks",
  "text": "Fund: HDFC Mid Cap... NAV: Rs. 218.745...",
  "metadata": {
    "fund_name": "HDFC Mid Cap Fund Direct Growth",
    "sub_category": "Mid Cap",
    "source_url": "https://groww.in/...",
    "last_updated": "2026-05-06T22:45:45"
  },
  "embedding": [0.0234, -0.0891, ...]
}
```

## Results
- 40 records, 384 dimensions each
- Total file size: ~476 KB
- Embedding time: ~3 seconds on CPU

## Running
```bash
cd phases/phase_1/phase_1.4_embedding
..\venv\Scripts\python.exe embedder.py
```
