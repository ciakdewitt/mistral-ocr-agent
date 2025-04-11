#!/usr/bin/env python
"""
Script to run the Streamlit application with the correct Python path.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the Streamlit application."""
    # Get the project root directory
    root_dir = Path(__file__).parent.absolute()
    
    # Get the Streamlit app path
    streamlit_app = root_dir / "ui" / "app.py"
    
    if not streamlit_app.exists():
        print(f"Error: Streamlit app not found at {streamlit_app}")
        sys.exit(1)
    
    # Set PYTHONPATH environment variable to include the project root
    env = os.environ.copy()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{root_dir}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = str(root_dir)
    
    print(f"Running Streamlit app: {streamlit_app}")
    print(f"Python path: {env['PYTHONPATH']}")
    
    # Run Streamlit
    try:
        subprocess.run(
            ["streamlit", "run", str(streamlit_app)], 
            env=env, 
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Streamlit command not found. Is streamlit installed?")
        print("Try running: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()