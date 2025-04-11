#!/usr/bin/env python
"""
Quick launch script for the OCR Agent application.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def check_environment():
    """Check if the environment is properly set up."""
    # Check for required API keys
    if not os.environ.get("MISTRAL_API_KEY"):
        logger.error("MISTRAL_API_KEY environment variable not set.")
        logger.info("Please set this in your .env file or environment.")
        return False
    
    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.error("ANTHROPIC_API_KEY environment variable not set.")
        logger.info("Please set this in your .env file or environment.")
        return False
    
    return True

def main():
    """Main entry point."""
    if not check_environment():
        sys.exit(1)
    
    # Import and run the main application
    try:
        # Add the current directory to the Python path to ensure imports work correctly
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from app.main import main as app_main
        app_main()
    except ImportError as e:
        logger.error(f"Error importing application code: {str(e)}")
        logger.info("Make sure you have installed all dependencies with 'pip install -r requirements.txt'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running application: {str(e)}")
        logger.exception("Detailed error:")
        sys.exit(1)

if __name__ == "__main__":
    main()