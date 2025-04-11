"""
Main entry point for the OCR Agent application.
"""
import os
import logging
import argparse
from pathlib import Path
import subprocess
import sys

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ocr_agent.log")
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import anthropic
        import mistralai
        import langgraph
        import streamlit
        import langchain
        import chromadb
        
        logger.info("All required dependencies are installed.")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        return False

def check_api_keys():
    """Check if all required API keys are set."""
    missing_keys = []
    
    if not os.environ.get("MISTRAL_API_KEY"):
        missing_keys.append("MISTRAL_API_KEY")
    
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if missing_keys:
        logger.error(f"Missing API keys: {', '.join(missing_keys)}")
        return False
    
    logger.info("All required API keys are set.")
    return True

def ensure_directories():
    """Ensure all required directories exist."""
    dirs = [
        os.environ.get("UPLOAD_FOLDER", "./data/uploads"),
        os.environ.get("VECTOR_DB_PATH", "./data/vector_store"),
        "./data/processed"
    ]
    
    for dir_path in dirs:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {path}")
    
    return True

def start_streamlit():
    """Start the Streamlit application."""
    streamlit_path = os.path.join(os.path.dirname(__file__), "..", "ui", "app.py")
    streamlit_path = os.path.abspath(streamlit_path)
    
    if not os.path.exists(streamlit_path):
        logger.error(f"Streamlit app not found at: {streamlit_path}")
        return False
    
    port = os.environ.get("STREAMLIT_SERVER_PORT", "8501")
    
    try:
        logger.info(f"Starting Streamlit app at: {streamlit_path} on port {port}")
        subprocess.run([
            "streamlit", "run", streamlit_path,
            "--server.port", port,
            "--server.headless", os.environ.get("STREAMLIT_SERVER_HEADLESS", "false")
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting Streamlit: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error starting Streamlit: {str(e)}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="OCR Agent Application")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies and exit")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    # Set debug mode if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        os.environ["DEBUG"] = "True"
    
    # Check dependencies and API keys
    deps_ok = check_dependencies()
    keys_ok = check_api_keys()
    dirs_ok = ensure_directories()
    
    if args.check_only:
        if deps_ok and keys_ok and dirs_ok:
            logger.info("All checks passed.")
            sys.exit(0)
        else:
            logger.error("One or more checks failed.")
            sys.exit(1)
    
    # Warn but continue if there are issues
    if not deps_ok:
        logger.warning("Missing dependencies. The application may not function correctly.")
    
    if not keys_ok:
        logger.warning("Missing API keys. The application may not function correctly.")
    
    # Start the Streamlit application
    start_streamlit()

if __name__ == "__main__":
    main()