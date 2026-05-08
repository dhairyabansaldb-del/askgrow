"""
Phase 1.4 - Embedding Generator

Uses BAAI/bge-small-en-v1.5 to convert sectional factual text chunks
into 384-dimensional vector embeddings.

Key design choices:
1. bge models use a query-instruction prefix for retrieval tasks.
   During embedding of DOCUMENTS (our chunks), we do NOT add the prefix.
   During embedding of QUERIES (user questions at runtime), we ADD the prefix:
   "Represent this sentence for searching relevant passages: "
   This asymmetric approach is how bge models achieve top retrieval scores.

2. Output is saved as JSON with the original text, metadata, and the
   embedding vector alongside it. This makes Phase 1.5 (ChromaDB ingestion)
   straightforward -- it just reads and upserts.

3. Each embedding gets a deterministic ID based on fund_name + section,
   enabling clean upserts during scheduled refreshes.
"""

import json
import os
import hashlib
import time
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME = "BAAI/bge-small-en-v1.5"

# The instruction prefix used ONLY at query time (not during document embedding).
# Stored here so Phase 2 (backend) can import it.
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def generate_chunk_id(fund_name, section):
    """Create a deterministic, unique ID for each chunk."""
    raw = "{}_{}".format(fund_name, section)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def load_chunks(chunks_dir):
    """Load all chunk JSON files from the Phase 1.3 output directory."""
    all_chunks = []
    json_files = sorted([f for f in os.listdir(chunks_dir) if f.endswith("_chunks.json")])

    for filename in json_files:
        filepath = os.path.join(chunks_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            all_chunks.extend(chunks)

    return all_chunks


def embed_chunks(chunks, model):
    """
    Generate embeddings for all chunks.
    For bge document embedding, we pass raw text WITHOUT the query instruction.
    """
    texts = [c["text"] for c in chunks]
    print("  Generating embeddings for {} chunks...".format(len(texts)))

    start = time.time()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    elapsed = time.time() - start

    print("  Embedding complete in {:.2f}s".format(elapsed))
    return embeddings


def build_embedded_records(chunks, embeddings):
    """Combine chunks with their embeddings into final records."""
    records = []
    for chunk, embedding in zip(chunks, embeddings):
        record = {
            "id": generate_chunk_id(
                chunk["metadata"]["fund_name"],
                chunk["section"]
            ),
            "section": chunk["section"],
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "embedding": embedding.tolist(),
        }
        records.append(record)
    return records


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_embedder():
    """Load chunks, generate embeddings, save output."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    chunks_dir = os.path.join(script_dir, "..", "phase_1.3_chunking", "chunks")
    output_dir = os.path.join(script_dir, "embeddings")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Phase 1.4: Embedding Generator")
    print("Model: {}".format(MODEL_NAME))
    print("=" * 60)

    # Step 1: Load model
    print("\n[1/3] Loading model...")
    model = SentenceTransformer(MODEL_NAME)
    print("  Model loaded. Dimension: {}".format(model.get_sentence_embedding_dimension()))

    # Step 2: Load chunks
    print("\n[2/3] Loading chunks...")
    chunks = load_chunks(chunks_dir)
    print("  Loaded {} chunks from {} fund files".format(
        len(chunks), len(chunks) // 8 if chunks else 0))

    # Step 3: Generate embeddings
    print("\n[3/3] Generating embeddings...")
    embeddings = embed_chunks(chunks, model)

    # Build final records
    records = build_embedded_records(chunks, embeddings)

    # Save output
    output_path = os.path.join(output_dir, "all_fund_embeddings.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_path)
    print("\n" + "=" * 60)
    print("Results:")
    print("  Total records: {}".format(len(records)))
    print("  Embedding dimension: {}".format(len(records[0]["embedding"])))
    print("  Output file: {}".format(os.path.abspath(output_path)))
    print("  File size: {:,.0f} KB".format(file_size / 1024))
    print("  Query instruction (for Phase 2):")
    print("    '{}'".format(QUERY_INSTRUCTION))
    print("=" * 60)

    # Print sample IDs for verification
    print("\nSample chunk IDs:")
    for r in records[:5]:
        print("  {} -> {} / {}".format(
            r["id"][:12], r["metadata"]["fund_name"][:30], r["section"]))


if __name__ == "__main__":
    run_embedder()
