"""
Phase 2 - Retriever
Handles connecting to the persistent ChromaDB, performing Metadata Pre-Filtering
based on heuristic entity extraction, and running semantic search using bge-small-en-v1.5.
"""

import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COLLECTION_NAME = "hdfc_mutual_funds"
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
# Check for production path first, then fallback to dev path
PROD_DB_DIR = os.path.join(script_dir, "chroma_db")
DEV_DB_DIR = os.path.join(os.path.dirname(script_dir), "phase_1", "phase_1.5_vector_storage", "chroma_db")
DB_DIR = PROD_DB_DIR if os.path.exists(PROD_DB_DIR) else DEV_DB_DIR

# Initialize clients globally so they are kept in memory for fast API responses
client = chromadb.PersistentClient(
    path=DB_DIR, 
    settings=Settings(anonymized_telemetry=False)
)
collection = client.get_collection(name=COLLECTION_NAME)

# Load the embedding model (only loads once at startup)
# This requires ~130MB of RAM
print("Loading embedding model (bge-small-en-v1.5)...")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
print("Embedding model loaded.")

# ---------------------------------------------------------------------------
# Entity Extraction Heuristics
# ---------------------------------------------------------------------------

FUND_MAPPING = {
    "mid cap": "Mid Cap",
    "mid-cap": "Mid Cap",
    "midcap": "Mid Cap",
    "flexi cap": "Flexi Cap",
    "flexi-cap": "Flexi Cap",
    "flexicap": "Flexi Cap",
    "focused": "Focused Fund",
    "focussed": "Focused Fund",
    "focus 30": "Focused Fund",
    "elss": "ELSS",
    "tax saver": "ELSS",
    "tax saving": "ELSS",
    "large cap": "Large Cap",
    "large-cap": "Large Cap",
    "largecap": "Large Cap"
}

def extract_fund_categories(query: str) -> list:
    """
    Scans the query for known fund keywords and maps them to the exact
    sub_category used in the database metadata.
    Returns a list of unique sub_categories found.
    """
    query_lower = query.lower()
    found_categories = set()
    for keyword, category in FUND_MAPPING.items():
        if keyword in query_lower:
            found_categories.add(category)
    return list(found_categories)

def detect_comparison_intent(query: str) -> bool:
    """
    Detects if the user is trying to compare multiple funds.
    """
    comparison_keywords = ["compare", "difference", "versus", "vs", "better", "higher", "lower", "cheaper"]
    query_lower = query.lower()
    return any(kw in query_lower for kw in comparison_keywords)

# ---------------------------------------------------------------------------
# Retrieval Logic
# ---------------------------------------------------------------------------

def retrieve_context(query: str, top_k: int = 5) -> dict:
    """
    Retrieves the most relevant factual chunks from ChromaDB for a given query.
    Implements Metadata Pre-Filtering for multiple entities and handles comparison intent.
    
    Returns a dictionary containing:
    - text: The combined text context to feed to the LLM.
    - citations: A list of unique source URLs.
    - filter_used: The sub_category filter applied (if any).
    """
    # 1. Entity Extraction & Intent Detection
    target_categories = extract_fund_categories(query)
    is_comparison = detect_comparison_intent(query)
    
    where_filter = None
    if target_categories:
        if len(target_categories) == 1:
            where_filter = {"sub_category": target_categories[0]}
        else:
            where_filter = {"sub_category": {"$in": target_categories}}
        print(f"Applying pre-filter: {where_filter}")
    else:
        print("No specific fund detected in query. Searching globally.")

    # 2. Vector Generation
    full_query = QUERY_INSTRUCTION + query
    query_embedding = model.encode(full_query).tolist()

    # 3. Dynamic top_k scaling
    # - If comparison or global search, use larger top_k (10-12)
    # - If single fund search, use top_k=5 (increased from 3)
    if is_comparison or not target_categories:
        actual_top_k = 12
    else:
        actual_top_k = top_k

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=actual_top_k,
        where=where_filter
    )

    # 4. Format Results
    context_chunks = []
    citations = set()
    
    if results and results["documents"] and len(results["documents"][0]) > 0:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        
        for idx in range(len(docs)):
            doc = docs[idx]
            meta = metas[idx]
            
            # Combine the metadata fund name and section with the chunk text
            formatted_chunk = f"[{meta['fund_name']} - {meta['section'].replace('_', ' ').title()}]\n{doc}"
            context_chunks.append(formatted_chunk)
            citations.add(meta['source_url'])

    combined_context = "\n\n---\n\n".join(context_chunks)
    
    return {
        "text": combined_context,
        "citations": list(citations),
        "filter_used": ", ".join(target_categories) if target_categories else None
    }
