"""
Minimal OCR processor that uses only the Mistral OCR API.
"""
import os
import base64
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union

from mistralai import Mistral

logger = logging.getLogger(__name__)

class MinimalOCRProcessor:
    """
    A minimal OCR processor using Mistral OCR API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with an API key."""
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key not provided and not found in environment")
        
        self.client = Mistral(api_key=self.api_key)
        if not hasattr(self.client, 'ocr'):
            raise AttributeError("OCR functionality not available in Mistral client")
    
    def process_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process a file with OCR.
        
        Args:
            file_path: Path to the file
            
        Returns:
            OCR processing result
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Processing file with OCR: {file_path}")
        
        # Read file and encode as base64
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        base64_content = base64.b64encode(file_content).decode('utf-8')
        
        # Determine content type based on file extension
        suffix = file_path.suffix.lower()
        
        # Based on the error message, we need to use either 'document_url' or 'image_url'
        if suffix in ['.pdf', '.txt', '.doc', '.docx']:
            # For documents, use document_url
            try:
                response = self.client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{base64_content}"
                    }
                )
                return response
            except Exception as e:
                logger.error(f"Document OCR processing failed: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "text": f"Failed to process document {file_path.name} with OCR"
                }
        else:
            # For images, use image_url
            image_mime = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.tiff': 'image/tiff',
                '.tif': 'image/tiff'
            }.get(suffix, 'image/jpeg')
            
            try:
                response = self.client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "image_url",
                        "image_url": f"data:{image_mime};base64,{base64_content}"
                    }
                )
                return response
            except Exception as e:
                logger.error(f"Image OCR processing failed: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "text": f"Failed to process image {file_path.name} with OCR"
                }