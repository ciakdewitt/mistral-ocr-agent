"""
Main Streamlit application for the OCR Agent.
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dotenv import load_dotenv

# After adding the parent directory to sys.path, we can import our modules
from app.agent.state import AgentState, DocumentInfo
from app.ocr.processor import OCRProcessor
from app.utils.document import save_uploaded_file, determine_document_type, ensure_directory, extract_file_metadata

# Mock the agent_graph for now to avoid import errors
# We'll implement the real functionality later
class MockAgentGraph:
    def invoke(self, state):
        return state

agent_graph = MockAgentGraph()