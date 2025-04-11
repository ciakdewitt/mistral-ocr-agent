"""
General helper functions for the OCR agent.
"""
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)

def determine_document_type(path_or_url: str) -> str:
    """
    Determine the document type from a file path or URL.
    
    Args:
        path_or_url: File path or URL
        
    Returns:
        Document type string: "pdf", "image", "text", or "unknown"
    """
    if not path_or_url:
        return "unknown"
        
    lower_path = path_or_url.lower()
    
    if lower_path.endswith(('.pdf')):
        return "pdf"
    elif lower_path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif')):
        return "image"
    elif lower_path.endswith(('.txt', '.md', '.rtf', '.csv', '.html', '.xml', '.json')):
        return "text"
    else:
        return "unknown"

def extract_file_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract metadata from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary of metadata
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    metadata = {
        "filename": file_path.name,
        "extension": file_path.suffix.lower(),
        "size_bytes": file_path.stat().st_size,
        "last_modified": file_path.stat().st_mtime
    }
    
    # Try to determine content type
    import mimetypes
    metadata["content_type"] = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    
    # Add additional metadata for specific file types
    if metadata["extension"] == '.pdf':
        try:
            import pypdf
            with open(file_path, 'rb') as f:
                pdf = pypdf.PdfReader(f)
                metadata["num_pages"] = len(pdf.pages)
                
                # Try to extract document info
                if pdf.metadata:
                    for key in ['title', 'author', 'creator', 'producer', 'subject']:
                        if hasattr(pdf.metadata, key) and getattr(pdf.metadata, key):
                            metadata[key] = getattr(pdf.metadata, key)
        except Exception as e:
            logger.warning(f"Error extracting PDF metadata: {str(e)}")
    
    return metadata

def format_time_delta(seconds: float) -> str:
    """
    Format a time delta in seconds to a human-readable string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    elif seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load JSON string, returning default if it fails.
    
    Args:
        json_str: JSON string to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON object or default value
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.warning(f"Error parsing JSON: {str(e)}")
        return default

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding a suffix if truncated.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length] + suffix

def get_error_message(exception: Exception) -> str:
    """
    Get a user-friendly error message from an exception.
    
    Args:
        exception: Exception object
        
    Returns:
        User-friendly error message
    """
    if hasattr(exception, 'message'):
        return str(exception.message)
    
    message = str(exception)
    
    # Handle common error types with better messages
    if "ConnectionError" in message or "Connection refused" in message:
        return "Connection error. Please check your internet connection and try again."
    elif "Timeout" in message:
        return "Request timed out. The server took too long to respond."
    elif "401" in message or "Unauthorized" in message:
        return "Authentication error. Please check your API key."
    elif "403" in message or "Forbidden" in message:
        return "Access denied. You don't have permission to perform this action."
    elif "404" in message or "Not Found" in message:
        return "Resource not found. The requested item does not exist."
    elif "429" in message or "Too Many Requests" in message:
        return "Rate limit exceeded. Please try again later."
    elif "500" in message or "503" in message or "Server Error" in message:
        return "Server error. The service is currently unavailable. Please try again later."
    
    return message