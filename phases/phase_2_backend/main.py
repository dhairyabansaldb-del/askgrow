"""
Phase 2 - FastAPI Main Application
Entry point for the GROW Mutual Fund RAG backend.
Exposes the POST /api/chat endpoint.
"""

import sys
import traceback
import logging

# Configure logging FIRST so we can see startup errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("main")

logger.info("Starting GROW Mutual Fund API...")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os

# Import our custom modules with error handling
try:
    logger.info("Loading PII filter...")
    from pii_filter import contains_pii, get_pii_refusal_message
    logger.info("PII filter loaded.")
    
    logger.info("Loading retriever (ChromaDB + embedding model)...")
    from retriever import retrieve_context
    logger.info("Retriever loaded.")
    
    logger.info("Loading LLM service (Groq)...")
    from llm_service import generate_response
    logger.info("LLM service loaded.")
    
    MODULES_LOADED = True
except Exception as e:
    logger.error(f"FATAL: Failed to load modules: {e}")
    logger.error(traceback.format_exc())
    MODULES_LOADED = False

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="GROW Mutual Fund FAQ Assistant API",
    description="A factual, compliance-first RAG backend for mutual fund queries.",
    version="1.0.0"
)

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# API Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's question about mutual funds.")

class ChatResponse(BaseModel):
    response: str
    citations: list[str]
    filter_used: Optional[str] = None
    pii_blocked: bool = False

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    """Root endpoint - simple JSON response."""
    return {"service": "GROW Mutual Fund API", "status": "online", "modules_loaded": MODULES_LOADED}

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "GROW Mutual Fund Chatbot API", "modules_loaded": MODULES_LOADED}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint.
    Flow: PII Filter -> Entity Extraction -> ChromaDB Retrieval -> Groq LLM Generation
    """
    if not MODULES_LOADED:
        raise HTTPException(status_code=503, detail="Backend modules failed to load. Check server logs.")
    
    query = request.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. PII Filter Guardrail
    if contains_pii(query):
        return ChatResponse(
            response=get_pii_refusal_message(),
            citations=[],
            filter_used=None,
            pii_blocked=True
        )

    # 2. Retrieval (Metadata Pre-filtering + Semantic Search)
    try:
        retrieved_context = retrieve_context(query, top_k=3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

    # 3. LLM Generation
    try:
        final_answer = generate_response(query, retrieved_context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation error: {str(e)}")

    return ChatResponse(
        response=final_answer["response"],
        citations=final_answer["citations"],
        filter_used=final_answer["filter_used"],
        pii_blocked=False
    )

logger.info("FastAPI app created successfully. Ready to serve.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
