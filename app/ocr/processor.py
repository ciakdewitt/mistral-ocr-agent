"""
OCR Processor module for handling document processing using Mistral OCR.
"""
import os
import base64
import logging
from typing import Dict, Optional, Union, List, Any
from pathlib import Path

# Import the correct Mistral API modules
from mistralai import Mistral

logger = logging.getLogger(__name__)

class OCRProcessor:
    """
    Handles OCR processing using Mistral OCR API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the OCR processor.
        
        Args:
            api_key: Mistral API key. If None, will attempt to read from environment.
            model: Mistral OCR model to use. If None, will use default from environment.
        """
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key not provided and not found in environment")
            
        self.model = model or os.environ.get("MISTRAL_OCR_MODEL", "mistral-ocr-latest")
        self.client = Mistral(api_key=self.api_key)
        
    def process_file(self, file_path: Union[str, Path], include_images: bool = False):
        """
        Process a local file using OCR.
        
        Args:
            file_path: Path to the file to process
            include_images: Whether to include base64-encoded images in the result
            
        Returns:
            OCR processing result
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Check file size (Mistral has a 50MB limit)
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 50:
            raise ValueError(f"File size ({file_size_mb:.2f}MB) exceeds Mistral's 50MB limit")
        
        # Read the file and encode it
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        base64_content = base64.b64encode(file_content).decode('utf-8')
        
        # Determine document type and MIME type based on file extension
        suffix = file_path.suffix.lower()
        
        if suffix in ['.pdf']:
            # Process as PDF document
            mime_type = 'application/pdf'
            doc_type = "document_url"
        elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']:
            # Process as image
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.tiff': 'image/tiff',
                '.tif': 'image/tiff'
            }.get(suffix, 'image/jpeg')
            doc_type = "image_url"
        else:
            # Default for text and other files
            mime_type = 'application/octet-stream'
            doc_type = "document_url"
            
        # Create data URI
        data_uri = f"data:{mime_type};base64,{base64_content}"
        
        # Process with OCR
        try:
            logger.info(f"Processing {file_path} as {doc_type} with MIME type {mime_type}")
            
            # Create the document parameter based on document type
            document_param = {
                "type": doc_type
            }
            
            # Add the appropriate URL field based on document type
            if doc_type == "document_url":
                document_param["document_url"] = data_uri
            else:  # image_url
                document_param["image_url"] = data_uri
            
            # Process the document
            response = self.client.ocr.process(
                model=self.model,
                document=document_param,
                include_image_base64=include_images
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing {file_path} with OCR: {str(e)}")
            raise
    
    def process_url(self, url: str, include_images: bool = False):
        """
        Process a document or image from a URL.
        
        Args:
            url: URL of the document or image
            include_images: Whether to include base64-encoded images in the result
            
        Returns:
            OCR processing result
        """
        logger.info(f"Processing URL with OCR: {url}")
        
        # Determine if URL is for an image or document based on extension
        lower_url = url.lower()
        
        if any(lower_url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']):
            doc_type = "image_url"
        else:
            doc_type = "document_url"
        
        # Process with OCR
        try:
            response = self.client.ocr.process(
                model=self.model,
                document={
                    "type": doc_type,
                    doc_type: url
                },
                include_image_base64=include_images
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing URL {url} with OCR: {str(e)}")
            raise
            
    def document_understanding(self, document_source: Union[str, Path], query: str) -> str:
        """
        Use document understanding capabilities to answer questions about a document.
        
        This implementation uses Mistral chat API as a fallback. In the final implementation,
        this should be replaced with Anthropic's Claude API.
        
        Args:
            document_source: URL or path to the document
            query: Natural language question about the document
            
        Returns:
            Answer to the question based on document content
        """
        logger.info(f"Performing document understanding with query: {query}")
        
        # First, process the document with OCR
        try:
            if isinstance(document_source, str) and (document_source.startswith('http://') or document_source.startswith('https://')):
                # Process URL
                ocr_result = self.process_url(document_source)
            else:
                # Process file
                ocr_result = self.process_file(Path(document_source))
                
            # Extract text from OCR result
            if hasattr(ocr_result, 'text'):
                document_text = ocr_result.text
            elif isinstance(ocr_result, dict) and 'text' in ocr_result:
                document_text = ocr_result['text']
            else:
                document_text = str(ocr_result)
                
            # Use Mistral chat API to answer the question about the document
            # Note: In the final implementation, this should use Anthropic's Claude API
            response = self.client.chat.complete(
                model="mistral-small",
                messages=[
                    {"role": "system", "content": "You are an assistant that answers questions about documents."},
                    {"role": "user", "content": f"Based on the following document, please answer this question: {query}\n\nDocument content:\n{document_text}"}
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in document understanding: {str(e)}")
            return f"Error processing document: {str(e)}"
    
    def batch_process(self, file_paths: List[Union[str, Path]], include_images: bool = False) -> List[Dict[str, Any]]:
        """
        Process multiple files in batch.
        
        Args:
            file_paths: List of paths to files to process
            include_images: Whether to include base64-encoded images in the results
            
        Returns:
            List of results with file paths and OCR results
        """
        results = []
        
        for file_path in file_paths:
            try:
                ocr_result = self.process_file(file_path, include_images)
                results.append({
                    "file_path": str(file_path),
                    "success": True,
                    "result": ocr_result
                })
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                results.append({
                    "file_path": str(file_path),
                    "success": False,
                    "error": str(e)
                })
        
        return results