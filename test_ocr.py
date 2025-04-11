"""
Test script for Mistral OCR functionality.
"""
import os
import base64
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    print("ERROR: MISTRAL_API_KEY not found in environment variables")
    exit(1)

print(f"Using API key starting with: {api_key[:5]}...")

try:
    from mistralai import Mistral
    client = Mistral(api_key=api_key)
    print("Successfully created Mistral client")
    
    # Check if OCR module is available
    if not hasattr(client, 'ocr'):
        print("ERROR: OCR module not found in Mistral client")
        exit(1)
    
    print("OCR module available in Mistral client")
    
    # Test the OCR processing capability with a simple example
    # Let's create a very simple text file
    test_file_path = Path("ocr_test_file.txt")
    with open(test_file_path, "w") as f:
        f.write("This is a test file for OCR processing.")
    
    print(f"Created test file at: {test_file_path.absolute()}")
    
    # Read the file and encode it
    with open(test_file_path, "rb") as f:
        file_content = f.read()
    
    base64_content = base64.b64encode(file_content).decode('utf-8')
    
    # Try to process using OCR
    print("Attempting OCR processing...")
    try:
        # Based on the error message, we need to use 'document_url' for documents
        result = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:text/plain;base64,{base64_content}"
            }
        )
        
        print("OCR processing successful!")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error during OCR processing: {str(e)}")
        print("Checking process method signature...")
        
        import inspect
        if hasattr(client.ocr, 'process'):
            sig = inspect.signature(client.ocr.process)
            print(f"OCR process method signature: {sig}")
            
            # Try with different parameters based on error message
            print("Trying alternative parameter format...")
            try:
                # Try with image_url instead
                result = client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "image_url",
                        "image_url": f"data:text/plain;base64,{base64_content}"
                    }
                )
                print("Alternative OCR processing successful!")
                print(f"Result: {result}")
            except Exception as e2:
                print(f"Alternative approach also failed: {str(e2)}")
                
                # One more try with a file that's definitely an image
                print("Creating a test image file...")
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    
                    # Create a simple image with text
                    img = Image.new('RGB', (200, 100), color='white')
                    d = ImageDraw.Draw(img)
                    d.text((20, 40), "OCR Test Image", fill='black')
                    img_path = Path("ocr_test_image.png")
                    img.save(img_path)
                    
                    # Read and encode the image
                    with open(img_path, "rb") as f:
                        img_content = f.read()
                    
                    img_base64 = base64.b64encode(img_content).decode('utf-8')
                    
                    # Try OCR with this image
                    print("Trying OCR with a PNG image...")
                    result = client.ocr.process(
                        model="mistral-ocr-latest",
                        document={
                            "type": "image_url",
                            "image_url": f"data:image/png;base64,{img_base64}"
                        }
                    )
                    print("Image OCR processing successful!")
                    print(f"Result: {result}")
                    
                    # Clean up
                    img_path.unlink()
                except ImportError:
                    print("PIL not available for image creation")
                except Exception as e3:
                    print(f"Image OCR approach also failed: {str(e3)}")