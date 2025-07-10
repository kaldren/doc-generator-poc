"""
ERP Data Conversion Assistant - Streamlit App Runner

This script helps you run the Streamlit app for ERP data conversion.

Before running, make sure you have:
1. Set up your .env file with required Azure credentials
2. Installed all dependencies: pip install -r requirements.txt

Then run: streamlit run streamlit_app.py
"""

import subprocess
import sys
import os

def check_env_vars():
    """Check if required environment variables are set"""
    required_vars = [
        "AZURE_OPENAI_CHAT_MODEL_ID",
        "AZURE_OPENAI_API_KEY", 
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_SEARCH_SERVICE_ENDPOINT",
        "AZURE_SEARCH_INDEX_NAME",
        "AZURE_SEARCH_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment.")
        return False
    
    print("✅ All required environment variables are set!")
    return True

def run_streamlit():
    """Run the Streamlit app"""
    if not check_env_vars():
        return
    
    print("🚀 Starting ERP Data Conversion Assistant...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")

if __name__ == "__main__":
    run_streamlit() 