"""
Utility functions for document handling.
"""
import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import logging

logger = logging.getLogger(__name__)

def determine_document_type(path_or_url: str) -> str:
    """
    Determine the document type from a file path or URL.
    
    Args:
        path_or_url: File path or URL
        
    Returns:
        Document type string: "pdf", "image", "text", or "unknown"
    """
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
        "last_modified": file_path.stat().st_mtime,
        "content_type": mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    }
    
    # Add additional metadata for specific file types
    if metadata["extension"] in ['.pdf']:
        try:
            import pypdf
            with open(file_path, 'rb') as f:
                pdf = pypdf.PdfReader(f)
                metadata["num_pages"] = len(pdf.pages)
                metadata["title"] = pdf.metadata.title if pdf.metadata and hasattr(pdf.metadata, 'title') else None
                metadata["author"] = pdf.metadata.author if pdf.metadata and hasattr(pdf.metadata, 'author') else None
                metadata["creator"] = pdf.metadata.creator if pdf.metadata and hasattr(pdf.metadata, 'creator') else None
        except Exception as e:
            logger.warning(f"Error extracting PDF metadata: {str(e)}")
    
    return metadata

def save_uploaded_file(uploaded_file, upload_dir: Union[str, Path]) -> Path:
    """
    Save an uploaded file to disk.
    
    Args:
        uploaded_file: File object from Streamlit uploader
        upload_dir: Directory to save the file in
        
    Returns:
        Path to the saved file
    """
    upload_dir = Path(upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / uploaded_file.name
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    logger.info(f"Saved uploaded file: {file_path}")
    return file_path

def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object for the directory
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def clean_temp_files(directory: Union[str, Path], max_age_hours: int = 24) -> None:
    """
    Clean temporary files older than a certain age.
    
    Args:
        directory: Directory containing temporary files
        max_age_hours: Maximum age of files in hours before they're deleted
    """
    directory = Path(directory)
    if not directory.exists():
        return
    
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 60 * 60
    
    for file_path in directory.glob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    logger.info(f"Deleted temporary file: {file_path}")
                except Exception as e:
                    logger.warning(f"Error deleting temporary file {file_path}: {str(e)}")