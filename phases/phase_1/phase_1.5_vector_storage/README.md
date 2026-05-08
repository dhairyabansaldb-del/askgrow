# Phase 1.5: Vector Storage & Indexing - Documentation

## Summary
Phase 1.5 takes the 40 embedded records from Phase 1.4 and upserts them into a persistent local ChromaDB collection, making them available for semantic similarity search.

## Files
- `db_manager.py` - Main script that loads embeddings, initializes ChromaDB, upserts, and verifies.
- `chroma_db/` - Persistent ChromaDB database directory (auto-created).

## ChromaDB Configuration
| Setting | Value |
|---|---|
| Client Type | PersistentClient (survives restarts) |
| Collection Name | `hdfc_mutual_funds` |
| Total Records | 40 (5 funds x 8 sections) |
| Embedding Dimension | 384 (from bge-small-en-v1.5) |

## Metadata per Record
Each record stored in ChromaDB carries:
- `fund_name` - e.g., "HDFC Mid Cap Fund Direct Growth"
- `sub_category` - e.g., "Mid Cap"
- `section` - e.g., "costs_and_benchmarks"
- `source_url` - Citation link
- `last_updated` - Scrape timestamp

This enables **filtered queries** in Phase 2 (e.g., only search within "Mid Cap" fund, or only "investment_rules" sections).

## Upsert Behavior
- Uses **upsert** (not insert): If a record ID already exists, it is overwritten.
- Record IDs are deterministic (MD5 of fund_name + section).
- This ensures the scheduler (Phase 1.6) can refresh data cleanly without creating duplicates.

## Verification
The script includes a built-in similarity search test confirming:
- Self-match returns distance `0.0` (exact match)
- Cross-fund matches return semantically similar sections

## Running
```bash
cd phases/phase_1/phase_1.5_vector_storage
..\venv\Scripts\python.exe db_manager.py
```
