"""
Simple test script to verify basic Mistral API functionality.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('.env')
load_dotenv(env_path)

# Get API key
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    print("ERROR: MISTRAL_API_KEY not found in environment variables")
    exit(1)

print(f"Using API key starting with: {api_key[:5]}...")

try:
    # Try to import and initialize Mistral client
    from mistralai import Mistral
    print("Successfully imported Mistral")
    
    client = Mistral(api_key=api_key)
    print("Successfully created Mistral client")
    
    # Check for OCR support
    if hasattr(client, 'ocr'):
        print("OCR module available in Mistral client")
        
        # Print available methods and attributes
        print("OCR module attributes:")
        for attr in dir(client.ocr):
            if not attr.startswith('_'):
                print(f"  - {attr}")
    else:
        print("WARNING: No OCR module found in Mistral client")
        
    # Try a simple chat completion to test the API
    print("\nTesting chat completion...")
    response = client.chat.completions.create(
        model="mistral-tiny",
        messages=[{"role": "user", "content": "Hello, world!"}],
        max_tokens=10
    )
    print(f"Chat response: {response.choices[0].message.content}")
    print("API connection test successful!")
    
except ImportError as e:
    print(f"ERROR importing Mistral: {e}")
except Exception as e:
    print(f"ERROR: {e}")