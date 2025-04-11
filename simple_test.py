"""
Simple test script to verify Mistral API functionality.
"""
import os
import sys
from pathlib import Path

# Try to import mistralai and check what's available
print("Checking Mistral API package:")
try:
    import mistralai
    print("✅ Successfully imported mistralai package")
    print("Available modules in mistralai:")
    for item in dir(mistralai):
        if not item.startswith("__"):
            print(f"  - {item}")
    
    # Check for specific client classes
    if hasattr(mistralai, "client"):
        print("✅ Found mistralai.client module")
        from mistralai.client import MistralClient
        print("✅ Successfully imported MistralClient")
    else:
        print("❌ No client module found in mistralai")
        
except ImportError as e:
    print(f"❌ Failed to import mistralai: {str(e)}")
    print("Please install the mistralai package with: pip install mistralai")

print("\nTrying to import our OCRProcessor:")
try:
    # Add the project root to Python path
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    
    # Try to import OCRProcessor
    from app.ocr.processor import OCRProcessor
    print("✅ Successfully imported OCRProcessor")
    
    # Check if we can instantiate it
    try:
        processor = OCRProcessor()
        print("✅ Successfully instantiated OCRProcessor")
    except Exception as e:
        print(f"❌ Failed to instantiate OCRProcessor: {str(e)}")
        
except ImportError as e:
    print(f"❌ Failed to import OCRProcessor: {str(e)}")
    
print("\nChecking API keys:")
mistral_key = os.environ.get("MISTRAL_API_KEY")
if mistral_key:
    print(f"✅ MISTRAL_API_KEY is set (first 5 chars: {mistral_key[:5]}...)")
else:
    print("❌ MISTRAL_API_KEY is not set")

anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
if anthropic_key:
    print(f"✅ ANTHROPIC_API_KEY is set (first 5 chars: {anthropic_key[:5]}...)")
else:
    print("❌ ANTHROPIC_API_KEY is not set")