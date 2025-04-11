"""
OCR tool for the LangGraph agent.
"""
import os
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from app.ocr.processor import OCRProcessor
from app.utils.helpers import determine_document_type, extract_file_metadata, get_error_message

logger = logging.getLogger(__name__)

class OCRTool:
    """
    Tool for processing documents with OCR.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the OCR tool.
        
        Args:
            api_key: Mistral API key. If None, will use environment variable.
            model: Mistral OCR model to use. If None, will use default.
        """
        self.processor = OCRProcessor(api_key=api_key, model=model)
    
    def process_document(self, file_path: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a document with OCR.
        
        Args:
            file_path: Path to the file to process
            url: URL of the document to process
            
        Returns:
            Dictionary with OCR results and metadata
        """
        if not file_path and not url:
            return {
                "success": False,
                "error": "No file path or URL provided"
            }
        
        try:
            if file_path:
                logger.info(f"Processing file with OCR: {file_path}")
                ocr_result = self.processor.process_file(file_path)
            else:
                logger.info(f"Processing URL with OCR: {url}")
                ocr_result = self.processor.process_url(url)
            
            # Extract basic metadata
            metadata = {}
            if file_path:
                try:
                    metadata = extract_file_metadata(file_path)
                except Exception as e:
                    logger.warning(f"Error extracting file metadata: {str(e)}")
            
            # Create result dictionary
            result = {
                "success": True,
                "text": ocr_result.text,
                "markdown": ocr_result.markdown,
                "document_id": ocr_result.id,
                "pages_processed": len(ocr_result.pages) if hasattr(ocr_result, 'pages') else 1,
                "metadata": metadata
            }
            
            # Add images if available
            if hasattr(ocr_result, 'images') and ocr_result.images:
                result["has_images"] = True
                result["image_count"] = len(ocr_result.images)
            else:
                result["has_images"] = False
                result["image_count"] = 0
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing document with OCR: {str(e)}")
            return {
                "success": False,
                "error": get_error_message(e)
            }
    
    def extract_tables(self, file_path: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract tables from a document.
        
        Args:
            file_path: Path to the file to process
            url: URL of the document to process
            
        Returns:
            Dictionary with extracted tables
        """
        # This is a placeholder for table extraction functionality
        # In a real implementation, you would use specialized table extraction techniques
        
        # First, process the document with OCR
        ocr_result = self.process_document(file_path=file_path, url=url)
        
        if not ocr_result["success"]:
            return ocr_result
        
        # In a real implementation, you would analyze the OCR results to extract tables
        # For now, just return a placeholder response
        return {
            "success": True,
            "message": "Table extraction is not yet implemented. This is a placeholder response.",
            "tables": [],
            "ocr_result": ocr_result
        }
    
    def document_understanding(self, document_source: Union[str, Path], query: str) -> Dict[str, Any]:
        """
        Use document understanding capabilities to answer questions about a document.
        
        Args:
            document_source: URL or path to the document
            query: Natural language question about the document
            
        Returns:
            Dictionary with the answer and metadata
        """
        try:
            logger.info(f"Performing document understanding with query: {query}")
            
            answer = self.processor.document_understanding(
                document_source=document_source,
                query=query
            )
            
            return {
                "success": True,
                "query": query,
                "answer": answer,
                "document_source": str(document_source)
            }
            
        except Exception as e:
            logger.error(f"Error in document understanding: {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": get_error_message(e),
                "document_source": str(document_source)
            }