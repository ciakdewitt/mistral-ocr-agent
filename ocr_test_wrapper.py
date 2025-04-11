"""
Test wrapper for OCR processor functionality.
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from app.ocr.processor import OCRProcessor

def process_file(file_path, include_images=False):
    """Process a file with OCR and print the results."""
    print(f"Processing file: {file_path}")
    
    processor = OCRProcessor()
    
    try:
        result = processor.process_file(file_path, include_images=include_images)
        
        print("\nOCR Processing Successful!")
        
        # Display result information
        print("\n--- OCR Result Summary ---")
        
        # Handle different result formats
        if hasattr(result, 'text'):
            print(f"Text length: {len(result.text)} characters")
            print("\nFirst 500 characters:")
            print(result.text[:500] + "..." if len(result.text) > 500 else result.text)
        elif isinstance(result, dict) and 'text' in result:
            print(f"Text length: {len(result['text'])} characters")
            print("\nFirst 500 characters:")
            print(result['text'][:500] + "..." if len(result['text']) > 500 else result['text'])
        else:
            print("Result format:")
            print(type(result))
            print("\nRaw result:")
            print(result)
        
        return True
    except Exception as e:
        print(f"\nError processing file: {str(e)}")
        return False

def process_url(url, include_images=False):
    """Process a URL with OCR and print the results."""
    print(f"Processing URL: {url}")
    
    processor = OCRProcessor()
    
    try:
        result = processor.process_url(url, include_images=include_images)
        
        print("\nOCR Processing Successful!")
        
        # Display result information
        print("\n--- OCR Result Summary ---")
        
        # Handle different result formats
        if hasattr(result, 'text'):
            print(f"Text length: {len(result.text)} characters")
            print("\nFirst 500 characters:")
            print(result.text[:500] + "..." if len(result.text) > 500 else result.text)
        elif isinstance(result, dict) and 'text' in result:
            print(f"Text length: {len(result['text'])} characters")
            print("\nFirst 500 characters:")
            print(result['text'][:500] + "..." if len(result['text']) > 500 else result['text'])
        else:
            print("Result format:")
            print(type(result))
            print("\nRaw result:")
            print(result)
        
        return True
    except Exception as e:
        print(f"\nError processing URL: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Mistral OCR functionality")
    parser.add_argument("--file", type=str, help="Path to file to process")
    parser.add_argument("--url", type=str, help="URL to process")
    parser.add_argument("--include-images", action="store_true", help="Include images in the result")
    
    args = parser.parse_args()
    
    if not args.file and not args.url:
        parser.print_help()
        return
    
    if args.file:
        process_file(args.file, args.include_images)
    
    if args.url:
        process_url(args.url, args.include_images)

if __name__ == "__main__":
    main()