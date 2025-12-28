import re
import html
import unicodedata
from typing import Optional
from app.core.logging import logger

def sanitize_input(raw_input: str, max_length: int = 500) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        raw_input (str): Raw user input
        max_length (int): Maximum allowed input length
        
    Returns:
        str: Sanitized and normalized input
    """
    try:
        if not raw_input:
            return ""
            
        text = str(raw_input)
        
        text = unicodedata.normalize("NFKC", text)
        text = text.replace("\0", "")
        text = re.sub(r"<[^>]*>", "", text)
        text = html.escape(text)
        
        text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", text)
        text = re.sub(r"[\\\"';]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
        
    except Exception as e:
        logger.error(f"Input sanitization error: {str(e)}", exc_info=True)
        return ""