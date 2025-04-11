"""
Minimal Streamlit app to test OCR functionality with updated configurations.
"""
import os
import sys
import streamlit as st
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import the environment loader and load variables
from load_env import load_environment_variables
env_loaded = load_environment_variables()

# Import our OCR processor
from app.ocr.processor import OCRProcessor

st.title("OCR Document Processor")
st.write("Upload a document to process with OCR")

# Check environment variables
if not env_loaded:
    st.error("⚠️ Failed to load environment variables")
    st.info("Check the output in the terminal for more details")
else:
    st.success("✅ Environment variables loaded successfully")
    
    # Check specific variables
    mistral_key = os.environ.get("MISTRAL_API_KEY")
    if mistral_key:
        st.success(f"✅ MISTRAL_API_KEY is set (starts with: {mistral_key[:5]}...)")
    else:
        st.error("⚠️ MISTRAL_API_KEY is not set")
    
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        st.success(f"✅ ANTHROPIC_API_KEY is set (starts with: {anthropic_key[:5]}...)")
    else:
        st.error("⚠️ ANTHROPIC_API_KEY is not set")

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
                    if isinstance(result, dict) and "text" in result:
                        st.text_area("Extracted Text", result["text"], height=300)
                    else:
                        st.text_area("Extracted Text", str(result), height=300)
                
                with tab2:
                    if isinstance(result, dict) and "markdown" in result:
                        st.markdown(result["markdown"])
                    else:
                        st.markdown(f"```\n{str(result)}\n```")
                
                # Display additional info
                if isinstance(result, dict):
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