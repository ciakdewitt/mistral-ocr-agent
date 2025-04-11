"""
Simple Streamlit application to test the OCR setup.
"""
import os
import sys
import streamlit as st
from pathlib import Path

# Add the current directory to the Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Try to import from the app module
try:
    from app.ocr.processor import OCRProcessor
    ocr_import_success = True
except ImportError as e:
    ocr_import_success = False
    ocr_import_error = str(e)

st.title("OCR Agent - Simple Test")

st.write("This is a simple test app to verify the Python imports are working properly.")

if ocr_import_success:
    st.success("✅ Successfully imported OCRProcessor from app.ocr.processor")
    
    # Check for API keys
    mistral_key = os.environ.get("MISTRAL_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if mistral_key:
        st.success("✅ MISTRAL_API_KEY is set")
    else:
        st.error("❌ MISTRAL_API_KEY is not set")
    
    if anthropic_key:
        st.success("✅ ANTHROPIC_API_KEY is set")
    else:
        st.error("❌ ANTHROPIC_API_KEY is not set")
    
    # Simple file uploader
    st.subheader("Test Document Upload")
    uploaded_file = st.file_uploader("Upload a PDF or image", type=["pdf", "jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.write("File uploaded:", uploaded_file.name)
        # Save file to a temporary location
        with open(f"temp_{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ File saved to temp_{uploaded_file.name}")
else:
    st.error(f"❌ Failed to import OCRProcessor: {ocr_import_error}")
    
    # Show Python path
    st.subheader("Current Python Path")
    for p in sys.path:
        st.write(p)
    
    # Show directory structure
    st.subheader("Directory Structure")
    app_dir = Path(current_dir) / "app"
    if app_dir.exists():
        st.write(f"app directory exists at: {app_dir}")
        
        # List subdirectories and files
        for item in app_dir.glob("**/*"):
            if item.is_file() and item.name == "__init__.py":
                st.write(f"  {item.relative_to(current_dir)}")
    else:
        st.error(f"app directory does not exist at: {app_dir}")