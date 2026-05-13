"""
Phase 2 - LLM Service
Handles the integration with Groq, implements the strict "facts-only" constraint
prompting, and enforces the refusal guardrail for advisory queries.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from datetime import datetime

# Load environment variables (like GROQ_API_KEY) from .env file
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(root_dir, ".env")
load_dotenv(env_path)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Initialize the Groq model
try:
    api_key = os.environ.get("GROQ_API_KEY")
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.0, # Zero temperature for maximum factual consistency
        max_tokens=256,  # We only need short answers
        api_key=api_key
    )
except Exception as e:
    print(f"Warning: Failed to initialize Groq. Check your GROQ_API_KEY in .env. Error: {e}")
    llm = None

# ---------------------------------------------------------------------------
# Dynamic Metadata (Last Ingestion Date)
# ---------------------------------------------------------------------------

def get_last_ingestion_date():
    """Reads the last ingestion date from the metadata file."""
    metadata_path = os.path.join(root_dir, "phases", "phase_1", "phase_1.6_scheduling", "last_ingestion.json")
    default_date = "2026-05-08" # Fallback if file is missing
    
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                data = json.load(f)
                return data.get("last_updated", default_date)
        except:
            return default_date
    return default_date

LAST_UPDATE_DATE = get_last_ingestion_date()

SYSTEM_PROMPT = f"""You are a highly strictly constrained, factual AI assistant for HDFC Mutual Funds.
You have access to information regarding the following 5 funds:
- HDFC Mid-Cap Opportunities Fund Direct Growth
- HDFC Flexi Cap Fund Direct Growth
- HDFC Focused 30 Fund Direct Growth
- HDFC ELSS Tax Saver Fund Direct Plan Growth
- HDFC Large Cap Fund Direct Growth

Your ONLY job is to answer the user's question using ONLY the provided context and the knowledge of the 5 funds listed above.

STRICT CONSTRAINTS:
1. NO FINANCIAL ADVICE: If the user asks for investment advice, predictions, or asks which fund is "best", you MUST refuse using the exact Refusal Template below.
2. FACTS ONLY: Do not hallucinate or use outside knowledge. If the answer is not in the context, say "I do not have the specific information to answer that question."
3. LENGTH LIMIT: Your answer MUST be 3 sentences or fewer (bullet points do not count against the sentence limit).
4. CITATION & FOOTER: You MUST append the exact footer string below at the very end of EVERY SINGLE response you generate. No exceptions.

Refusal Template:
"I am a factual assistant and cannot provide investment advice or recommendations. Please consult a SEBI-registered financial advisor."

Footer String:
"Last updated from sources: {LAST_UPDATE_DATE}"

CONTEXT DATA:
{{context}}

SOURCE CITATIONS AVAILABLE:
{{citations}}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])

output_parser = StrOutputParser()

# Create the LangChain processing chain if LLM is available
chain = None
if llm:
    chain = prompt | llm | output_parser

# ---------------------------------------------------------------------------
# Service Logic
# ---------------------------------------------------------------------------

def check_advisory_intent(query: str) -> bool:
    """
    A fast heuristic to catch obvious advisory queries before hitting the LLM.
    Returns True if advisory intent is detected.
    """
    advisory_keywords = ["should i buy", "which is best", "is it good to invest", 
                         "recommend", "what to buy", "will it go up", "prediction"]
    query_lower = query.lower()
    for kw in advisory_keywords:
        if kw in query_lower:
            return True
    return False

def generate_response(query: str, retrieved_context: dict) -> dict:
    """
    Takes the user query and the context retrieved from ChromaDB,
    checks for advisory intent, and calls the Groq LLM to generate the final response.
    """
    
    # Fast refusal guardrail (saves an API call)
    if check_advisory_intent(query):
        return {
            "response": "I am a factual assistant and cannot provide investment advice or recommendations. Please consult a SEBI-registered financial advisor.",
            "citations": [],
            "filter_used": None
        }

    # Extract context details
    context_text = retrieved_context["text"]
    citations_list = retrieved_context["citations"]
    filter_used = retrieved_context["filter_used"]
    
    # Format citations as a string for the prompt
    citations_str = "\n".join([f"- {url}" for url in citations_list])

    # Ensure we don't try to invoke LLM if not initialized (e.g. missing API key)
    if not llm:
        return {
            "response": "Error: LLM service is not configured. Please check API keys.",
            "citations": [],
            "filter_used": None
        }

    # Generate the response using LangChain
    try:
        response_text = chain.invoke({
            "context": context_text,
            "citations": citations_str,
            "question": query
        })
        
        # Enforce footer compliance programmatically if LLM misses it
        footer_string = f"Last updated from sources: {LAST_UPDATE_DATE}"
        if footer_string not in response_text:
            response_text += f"\n\n{footer_string}"
            
    except Exception as e:
        response_text = f"An error occurred while generating the response: {str(e)}"

    return {
        "response": response_text,
        "citations": citations_list,
        "filter_used": filter_used
    }
