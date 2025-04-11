"""
Tiny Streamlit app to test minimal OCR processor.
"""
import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import the minimal OCR processor
from app.ocr.minimal_processor import MinimalOCRProcessor

st.title("Minimal OCR Tester")

# Check API key
mistral_key = os.environ.get("MISTRAL_API_KEY")
if not mistral_key:
    st.error("⚠️ MISTRAL_API_KEY not found in environment variables")
    st.stop()
else:
    st.success(f"✅ Using Mistral API key: {mistral_key[:5]}...")

# File upload
uploaded_file = st.file_uploader(
    "Upload a file to process with OCR", 
    type=["pdf", "png", "jpg", "jpeg", "txt"]
)

if uploaded_file:
    # Display file details
    st.write(f"File name: {uploaded_file.name}")
    st.write(f"File size: {uploaded_file.size / 1024:.1f} KB")
    
    # Save to temporary file
    temp_path = Path(f"temp_{uploaded_file.name}")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write(f"Saved to temporary file: {temp_path}")
    
    # Process with OCR
    if st.button("Process with OCR"):
        with st.spinner("Processing with OCR..."):
            try:
                processor = MinimalOCRProcessor()
                result = processor.process_file(temp_path)
                
                # Show results
                st.success("Processing completed")
                st.subheader("OCR Result")
                
                # Handle different result formats
                if isinstance(result, dict):
                    if "text" in result:
                        st.text_area("Extracted Text:", result["text"], height=300)
                    elif "success" in result and not result["success"]:
                        st.error(f"OCR processing failed: {result.get('error', 'Unknown error')}")
                    else:
                        st.json(result)
                else:
                    st.write("Result type:", type(result))
                    st.json(result)
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                st.exception(e)
            
            # Clean up
            try:
                temp_path.unlink()
                st.write("Temporary file removed")
            except Exception as e:
                st.warning(f"Could not remove temporary file: {str(e)}")