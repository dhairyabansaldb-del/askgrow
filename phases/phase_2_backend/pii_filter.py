"""
Phase 2 - PII Filter
Detects Personal Identifiable Information (PII) such as PAN cards and Aadhaar numbers
in user queries. Acts as an early-rejection middleware to prevent sensitive data
from being sent to the LLM.
"""

import re

# Regex for Indian PAN Card (5 letters, 4 digits, 1 letter)
PAN_REGEX = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', re.IGNORECASE)

# Regex for Aadhaar Card (12 digits, optional spaces or hyphens)
AADHAAR_REGEX = re.compile(r'\b\d{4}[ -]?\d{4}[ -]?\d{4}\b')

def contains_pii(text: str) -> bool:
    """
    Checks if the input text contains recognizable PII patterns.
    Returns True if PII is found, False otherwise.
    """
    if not text:
        return False
        
    if PAN_REGEX.search(text):
        return True
        
    if AADHAAR_REGEX.search(text):
        return True
        
    return False

def get_pii_refusal_message() -> str:
    """Standard message returned when PII is detected."""
    return (
        "For your security, I cannot process queries containing Personal Identifiable "
        "Information (PII) such as PAN or Aadhaar numbers. Please ask your question "
        "without including sensitive personal details."
    )
