#!/usr/bin/env python3
"""
Test SQLite version of nutri.ai
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ streamlit")
    except ImportError as e:
        print(f"❌ streamlit: {e}")
        return False
    
    try:
        import bcrypt
        print("✅ bcrypt")
    except ImportError as e:
        print(f"❌ bcrypt: {e}")
        return False
    
    try:
        import sqlite3
        print("✅ sqlite3 (built-in)")
    except ImportError as e:
        print(f"❌ sqlite3: {e}")
        return False
    
    try:
        from auth_sqlite import register_user, login_user, get_user_info
        print("✅ auth_sqlite")
    except ImportError as e:
        print(f"❌ auth_sqlite: {e}")
        return False
    
    try:
        from water_tracker_sqlite import water_tracker_page
        print("✅ water_tracker_sqlite")
    except ImportError as e:
        print(f"❌ water_tracker_sqlite: {e}")
        return False
    
    try:
        from nutrition_analyzer import nutrition_analyzer_page
        print("✅ nutrition_analyzer")
    except ImportError as e:
        print(f"❌ nutrition_analyzer: {e}")
        return False
    
    return True

def test_database():
    """Test SQLite database operations"""
    print("\n🗄️ Testing database operations...")
    
    try:
        from auth_sqlite import register_user, login_user, get_user_info
        
        # Test registration
        success = register_user("testuser", "test@example.com", "testpass123")
        if success:
            print("✅ User registration")
        else:
            print("❌ User registration failed")
            return False
        
        # Test login
        login_success = login_user("testuser", "testpass123")
        if login_success:
            print("✅ User login")
        else:
            print("❌ User login failed")
            return False
        
        # Test get user info
        user_info = get_user_info("testuser")
        if user_info and user_info['username'] == "testuser":
            print("✅ Get user info")
        else:
            print("❌ Get user info failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_env_file():
    """Test environment file"""
    print("\n📄 Testing environment file...")
    
    if os.path.exists('.env'):
        print("✅ .env file exists")
        load_dotenv()
        
        project_name = os.getenv('PROJECT_NAME')
        if project_name:
            print(f"✅ PROJECT_NAME: {project_name}")
        else:
            print("⚠️ PROJECT_NAME not set")
        
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key and groq_key != "your_groq_api_key_here":
            print("✅ GROQ_API_KEY is set")
        else:
            print("⚠️ GROQ_API_KEY not set (app will work with fallback features)")
        
        return True
    else:
        print("❌ .env file not found")
        return False

def main():
    print("🧪 Testing SQLite version of nutri.ai")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
    
    # Test environment
    test_env_file()
    
    # Test database
    if not test_database():
        print("\n❌ Database tests failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed!")
    print("\n🚀 Your app is ready to run:")
    print("   streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 