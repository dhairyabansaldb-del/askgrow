"""
Phase 1.5 - Vector Storage & Indexing (ChromaDB)

Reads the embedded records from Phase 1.4 and upserts them into a
local ChromaDB persistent collection.

Design choices:
1. Uses ChromaDB's PersistentClient so the database survives restarts.
   The DB directory lives at phase_1.5_vector_storage/chroma_db/.
2. Collection name: "hdfc_mutual_funds"
3. Upsert mode: If a record with the same ID already exists, it is
   overwritten. This is critical for the scheduler (Phase 1.6) to
   refresh data without creating duplicates.
4. Metadata stored per record: fund_name, sub_category, section,
   source_url, last_updated. This enables filtered queries later
   (e.g., "only search Mid Cap fund chunks").
5. Includes a verification step that runs a sample similarity search
   to confirm the DB is working correctly.
"""

import json
import os
import time
import chromadb


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COLLECTION_NAME = "hdfc_mutual_funds"
DB_DIR_NAME = "chroma_db"


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def load_embedded_records(embeddings_path):
    """Load the embedded records JSON from Phase 1.4."""
    with open(embeddings_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    return records


def init_chroma_client(db_dir):
    """Initialize a persistent ChromaDB client."""
    os.makedirs(db_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=db_dir)
    return client


def upsert_to_collection(client, records):
    """
    Create or get the collection and upsert all records.
    ChromaDB upsert = insert if new, update if ID exists.
    """
    # Get or create the collection (no embedding function — we supply our own)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "HDFC Mutual Fund factual chunks for RAG chatbot"}
    )

    # Prepare batch data
    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for record in records:
        ids.append(record["id"])
        embeddings.append(record["embedding"])
        documents.append(record["text"])
        metadatas.append({
            "fund_name": record["metadata"]["fund_name"],
            "sub_category": record["metadata"]["sub_category"],
            "section": record["section"],
            "source_url": record["metadata"]["source_url"],
            "last_updated": record["metadata"]["last_updated"],
        })

    # Upsert in a single batch (40 records is well within limits)
    print("  Upserting {} records...".format(len(ids)))
    start = time.time()
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    elapsed = time.time() - start
    print("  Upsert complete in {:.2f}s".format(elapsed))

    return collection


def verify_collection(collection):
    """Run basic checks to confirm the collection is healthy."""
    count = collection.count()
    print("\n  Collection '{}' now has {} records.".format(COLLECTION_NAME, count))

    # Peek at a few records
    peek = collection.peek(limit=3)
    print("  Sample records (peek):")
    for i, doc_id in enumerate(peek["ids"]):
        meta = peek["metadatas"][i]
        doc_preview = peek["documents"][i][:80].replace("\n", " | ")
        print("    [{}] {} / {} -> '{}'...".format(
            doc_id[:12], meta["fund_name"][:30], meta["section"], doc_preview))

    return count


def run_sample_query(collection):
    """
    Run a sample similarity search to verify retrieval works.
    We use a pre-computed query embedding here. In production (Phase 2),
    the FastAPI backend will compute this using the bge model with
    the QUERY_INSTRUCTION prefix.
    """
    # For verification, we'll query by text using ChromaDB's built-in
    # We can't use text query without an embedding function, so we'll
    # query by embedding — use the first record's embedding as a test
    peek = collection.peek(limit=1)
    if peek["embeddings"] is not None and len(peek["embeddings"]) > 0:
        test_embedding = list(peek["embeddings"][0])
        results = collection.query(
            query_embeddings=[test_embedding],
            n_results=3,
        )
        print("\n  Sample similarity search (using first record as query):")
        print("  Top 3 results:")
        for i, doc_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i]
            dist = results["distances"][0][i] if results.get("distances") else "N/A"
            print("    {}. {} / {} (distance: {})".format(
                i + 1, meta["fund_name"][:35], meta["section"], dist))


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_db_manager():
    """Load embeddings, initialize ChromaDB, upsert, and verify."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    embeddings_path = os.path.join(
        script_dir, "..", "phase_1.4_embedding", "embeddings", "all_fund_embeddings.json"
    )
    db_dir = os.path.join(script_dir, DB_DIR_NAME)

    print("=" * 60)
    print("Phase 1.5: Vector Storage & Indexing (ChromaDB)")
    print("=" * 60)

    # Step 1: Load embedded records
    print("\n[1/4] Loading embedded records...")
    records = load_embedded_records(embeddings_path)
    print("  Loaded {} records".format(len(records)))

    # Step 2: Initialize ChromaDB
    print("\n[2/4] Initializing ChromaDB...")
    print("  DB directory: {}".format(os.path.abspath(db_dir)))
    client = init_chroma_client(db_dir)
    print("  ChromaDB client ready.")

    # Step 3: Upsert records
    print("\n[3/4] Upserting to collection '{}'...".format(COLLECTION_NAME))
    collection = upsert_to_collection(client, records)

    # Step 4: Verify
    print("\n[4/4] Verifying...")
    count = verify_collection(collection)
    run_sample_query(collection)

    print("\n" + "=" * 60)
    print("Phase 1.5 Complete!")
    print("  Collection: {}".format(COLLECTION_NAME))
    print("  Records: {}".format(count))
    print("  DB path: {}".format(os.path.abspath(db_dir)))
    print("=" * 60)


if __name__ == "__main__":
    run_db_manager()
