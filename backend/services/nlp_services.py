# app/services/nlp_service.py
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def clean_text(raw_text: str) -> str:
    """
    Removes extra whitespace, special characters, and normalizes text.
    """
    if not raw_text:
        return ""
    
    # Remove multiple newlines/spaces into single space
    text = re.sub(r'\s+', ' ', raw_text).strip()
    
    # Remove common OCR artifacts (keep alphanumeric and basic punctuation)
    # Adjust regex if you need to keep specific symbols
    text = re.sub(r'[^\w\s.,@#$%&\-()/]', '', text)
    
    return text

def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extracts named entities using Pure Python Regex.
    No external NLP libraries (like spaCy) required.
    """
    entities = {
        "PERSON": [],
        "DATE": [],
        "ORG": [],      # Hard to detect with regex, leaving empty or heuristic
        "GPE": [],      # Hard to detect with regex
        "CARDINAL": [], # Numbers
        "MONEY": [],
        "EMAIL": [],
        "PHONE": [],
        "ID_NUMBER": []
    }
    
    # 1. Email Extraction
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    if emails:
        entities["EMAIL"] = list(set(emails))
    
    # 2. Phone Number Extraction (International & Local formats)
    phone_pattern = r'\+?\d[\d\s\-\(\)]{7,}\d'
    phones = re.findall(phone_pattern, text)
    if phones:
        entities["PHONE"] = list(set(phones))
        
    # 3. Date Extraction (DD/MM/YYYY, MM-DD-YYYY, YYYY-MM-DD)
    date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b'
    dates = re.findall(date_pattern, text)
    if dates:
        entities["DATE"] = list(set(dates))
        
    # 4. ID Number Extraction (Alphanumeric strings 6-15 chars, often uppercase)
    # Adjust based on expected ID format (e.g., Aadhaar, Passport, SSN)
    id_pattern = r'\b[A-Z0-9]{6,15}\b'
    ids = re.findall(id_pattern, text)
    # Filter out common words that might match (optional heuristic)
    filtered_ids = [i for i in ids if not i.isdigit() and len(i) > 4] 
    if filtered_ids:
        entities["ID_NUMBER"] = list(set(filtered_ids))

    # 5. Person Name Heuristic
    # Without NLP, we assume the first non-empty line that isn't a number/date is a name.
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        potential_name = lines[0]
        # Check if it looks like a name (has space, no digits, reasonable length)
        if ' ' in potential_name and not any(c.isdigit() for c in potential_name) and 5 < len(potential_name) < 50:
            entities["PERSON"].append(potential_name)
            
    # 6. Money Extraction (Simple $ or ₹ or Rs pattern)
    money_pattern = r'[$₹Rs]\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
    money = re.findall(money_pattern, text, re.IGNORECASE)
    if money:
        entities["MONEY"] = list(set(money))

    logger.info(f"Extracted entities: {entities}")
    return entities

def detect_language(text: str) -> str:
    """
    Returns 'en' by default. 
    For multi-language support without heavy libs, you'd need 'langdetect'.
    """
    return "en" 

def process_document_text(raw_text: str) -> Dict[str, Any]:
    """
    Main pipeline: Clean -> Extract -> Structure
    """
    if not raw_text:
        return {"error": "No text provided", "entities": {}, "cleaned_text": ""}
        
    cleaned = clean_text(raw_text)
    entities = extract_entities(cleaned)
    lang = detect_language(cleaned)
    
    return {
        "cleaned_text": cleaned,
        "language": lang,
        "entities": entities,
        "word_count": len(cleaned.split())
    }