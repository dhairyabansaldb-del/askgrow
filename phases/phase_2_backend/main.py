"""
Phase 2 - FastAPI Main Application
Entry point for the HDFC Mutual Fund RAG backend.
Exposes the POST /api/chat endpoint.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import os

# Import our custom modules
from pii_filter import contains_pii, get_pii_refusal_message
from retriever import retrieve_context
from llm_service import generate_response

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="HDFC Mutual Fund FAQ Assistant API",
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

# Mount static files for the frontend UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(static_dir, "index.html"))

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

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "Mutual Fund Chatbot API"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint.
    Flow: PII Filter -> Entity Extraction -> ChromaDB Retrieval -> Groq LLM Generation
    """
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

if __name__ == "__main__":
    import uvicorn
    # Run the server locally for testing
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
