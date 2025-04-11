"""
Basic Streamlit app using simplified OCR processor.
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

# Import the simplified processor
from app.ocr.simple_processor import SimpleOCRProcessor

st.title("Basic OCR Text Processor")

# Check for API key
mistral_key = os.environ.get("MISTRAL_API_KEY")
if not mistral_key:
    st.error("⚠️ MISTRAL_API_KEY not found in environment variables")
    st.stop()
else:
    st.success(f"✅ Using Mistral API key: {mistral_key[:5]}...")

# Two options: text input or file upload
option = st.radio("Choose input method:", ["Text Input", "File Upload"])

if option == "Text Input":
    text_input = st.text_area("Enter text to process:", height=200)
    
    if st.button("Process Text") and text_input:
        with st.spinner("Processing..."):
            try:
                processor = SimpleOCRProcessor()
                result = processor.process_text(text_input)
                
                st.success("Text processed successfully!")
                st.subheader("Analysis:")
                st.write(result["analysis"])
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)
else:
    uploaded_file = st.file_uploader("Upload a text file:", type=["txt", "md", "py", "csv"])
    
    if uploaded_file is not None:
        # Save the file temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("Process File"):
            with st.spinner("Processing file..."):
                try:
                    processor = SimpleOCRProcessor()
                    result = processor.process_file(temp_path)
                    
                    if result["success"]:
                        st.success("File processed successfully!")
                    else:
                        st.warning("File processed with warnings")
                    
                    # Display results
                    st.subheader("File Content:")
                    st.text_area("", result["text"], height=200)
                    
                    st.subheader("Analysis:")
                    st.write(result["analysis"])
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.exception(e)
                
                # Clean up
                try:
                    Path(temp_path).unlink()
                except:
                    pass