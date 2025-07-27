#!/usr/bin/env python3
"""
Setup script for nutri.ai application
This script helps you configure your environment variables
"""

import os
import getpass

def create_env_file():
    """Create .env file with user input"""
    
    print("=== nutri.ai Environment Setup ===")
    print()
    
    # MongoDB URI
    print("MongoDB Configuration:")
    print("1. If you have MongoDB installed locally, use: mongodb://localhost:27017/")
    print("2. If you're using MongoDB Atlas, use your connection string")
    print("3. For testing without MongoDB, you can use: mongodb://localhost:27017/")
    mongo_uri = input("Enter MongoDB URI (or press Enter for default): ").strip()
    if not mongo_uri:
        mongo_uri = "mongodb://localhost:27017/"
    
    print()
    
    # GROQ API Key
    print("GROQ API Key Configuration:")
    print("1. Go to https://console.groq.com/")
    print("2. Sign up for a free account")
    print("3. Create an API key")
    print("4. Copy the API key")
    groq_key = getpass.getpass("Enter your GROQ API key (or press Enter to skip): ").strip()
    if not groq_key:
        groq_key = "your_groq_api_key_here"
    
    print()
    
    # Project Name
    project_name = input("Enter project name (or press Enter for default 'nutri.ai'): ").strip()
    if not project_name:
        project_name = "nutri.ai"
    
    # Create .env file
    env_content = f"""# MongoDB Connection
MONGO_URI={mongo_uri}

# GROQ API Key for AI features
# Get your free API key from https://console.groq.com/
GROQ_API_KEY={groq_key}

# Project Name
PROJECT_NAME={project_name}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print()
        print("Next steps:")
        print("1. If you haven't set a GROQ API key, get one from https://console.groq.com/")
        print("2. Edit the .env file and replace 'your_groq_api_key_here' with your actual API key")
        print("3. Run: streamlit run app.py")
        print()
        print("Note: AI features will show 'API key not configured' until you set a valid GROQ API key.")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        print("Please create a .env file manually with the following content:")
        print()
        print(env_content)

if __name__ == "__main__":
    create_env_file() 