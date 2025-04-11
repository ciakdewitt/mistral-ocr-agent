#!/usr/bin/env python
"""
Script to set up the project directory structure.
"""
import os
import sys
from pathlib import Path

def create_directories():
    """Create all required directories for the project."""
    # Define the directories to create
    directories = [
        "app",
        "app/agent",
        "app/agent/tools",
        "app/ocr",
        "app/rag",
        "app/utils",
        "ui",
        "ui/components",
        "ui/pages",
        "ui/utils",
        "data",
        "data/uploads",
        "data/processed",
        "data/vector_store",
        "tests",
        "tests/fixtures",
        "tests/fixtures/sample_docs"
    ]
    
    # Get the project root directory
    root_dir = Path(__file__).parent
    
    # Create each directory
    for directory in directories:
        dir_path = root_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

    # Create __init__.py files in Python directories
    for directory in directories:
        if not any(non_py_dir in directory for non_py_dir in ["data", "tests/fixtures/sample_docs"]):
            init_file = root_dir / directory / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                print(f"Created __init__.py file: {init_file}")

def main():
    """Main entry point."""
    print("Setting up project directory structure...")
    create_directories()
    print("Project directory structure setup complete.")

if __name__ == "__main__":
    main()