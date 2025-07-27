#!/usr/bin/env python3
"""
Setup script for SQLite version of nutri.ai
"""

import os

def create_env_file():
    """Create .env file for SQLite version"""
    env_content = """# GROQ API Key for AI features
# Get your free API key from https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# Project Name
PROJECT_NAME=nutri.ai
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file for SQLite version")

def main():
    print("🔧 Setting up nutri.ai with SQLite")
    print("=" * 50)
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Setup complete!")
    print("\n📝 Next steps:")
    print("1. Get a free GROQ API key from https://console.groq.com/")
    print("2. Update the GROQ_API_KEY in your .env file")
    print("3. Run: streamlit run app.py")
    print("\n💡 The app now uses SQLite instead of MongoDB - no cloud database needed!")

if __name__ == "__main__":
    main() 