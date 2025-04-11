"""
Minimal Streamlit app to test OCR functionality.
"""
import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import our OCR processor
from app.ocr.processor import OCRProcessor

st.title("OCR Document Processor")
st.write("Upload a document to process with OCR")

# Check for API keys
mistral_key = os.environ.get("MISTRAL_API_KEY")
if not mistral_key:
    st.error("⚠️ MISTRAL_API_KEY environment variable is not set")
    st.info("Please set this in your .env file or environment and restart the app")

# Upload file
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    # Display file details
    st.write(f"File: {uploaded_file.name}")
    st.write(f"File size: {uploaded_file.size / 1024:.1f} KB")
    
    # Save the file temporarily
    temp_file_path = Path(f"temp_{uploaded_file.name}")
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write(f"Saved temporary file to: {temp_file_path}")
    
    # Process with OCR if button is clicked
    if st.button("Process with OCR"):
        with st.spinner("Processing document with OCR..."):
            try:
                # Create OCR processor and process the file
                processor = OCRProcessor()
                result = processor.process_file(temp_file_path)
                
                # Show the results
                st.success("Document processed successfully!")
                
                # Display in tabs
                tab1, tab2 = st.tabs(["Text", "Markdown"])
                
                with tab1:
                    st.text_area("Extracted Text", result.get("text", ""), height=300)
                
                with tab2:
                    st.markdown(result.get("markdown", ""))
                
                # Display additional info
                st.write(f"Document ID: {result.get('id', 'N/A')}")
                st.write(f"Pages processed: {len(result.get('pages', []))}")
                
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
                st.exception(e)
            
            # Clean up the temporary file
            try:
                temp_file_path.unlink()
                st.write("Temporary file removed")
            except:
                st.write("Could not remove temporary file")