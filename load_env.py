"""
Script to load environment variables from .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment_variables():
    """
    Load environment variables from .env file and print them for debugging.
    Returns True if successful, False otherwise.
    """
    # Find .env file
    env_paths = [
        Path('.env'),                      # Current directory
        Path(__file__).parent / '.env',    # Same directory as this script
        Path.home() / '.env',              # Home directory
    ]
    
    env_file = None
    for path in env_paths:
        if path.exists():
            env_file = path
            break
    
    if not env_file:
        print("ERROR: .env file not found in any of the expected locations")
        return False
    
    # Load environment variables
    print(f"Loading environment variables from: {env_file.absolute()}")
    load_dotenv(env_file)
    
    # Check required variables
    required_vars = ['MISTRAL_API_KEY', 'ANTHROPIC_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"ERROR: The following required environment variables are missing: {', '.join(missing_vars)}")
        return False
    
    # Print loaded variables (redacted for security)
    print("Environment variables loaded:")
    for var in os.environ:
        if var in required_vars:
            value = os.environ[var]
            redacted = value[:5] + '...' if value else 'Not set'
            print(f"  {var}: {redacted}")
    
    return True

if __name__ == "__main__":
    success = load_environment_variables()
    if success:
        print("All environment variables loaded successfully!")
    else:
        print("Failed to load all required environment variables.")