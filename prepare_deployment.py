#!/usr/bin/env python3
"""
Deployment Preparation Script for nutri.ai
This script checks if your project is ready for deployment
"""

import os
import sys

def check_required_files():
    """Check if all required files exist"""
    print("🔍 Checking required files...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'nutrition_analyzer.py',
        'ai_health_assistant.py',
        'medicine_dashboard.py',
        'hospital_finder.py',
        'diet_planner.py',
        'ai_meal_planner.py',
        'water_tracker.py',
        'exercise_tip.py',
        'auth.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    return missing_files

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n🔍 Checking environment configuration...")
    
    if os.path.exists('.env'):
        print("✅ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'GROQ_API_KEY' in content:
                print("✅ GROQ_API_KEY found")
            else:
                print("⚠️  GROQ_API_KEY not found in .env")
            
            if 'MONGO_URI' in content:
                print("✅ MONGO_URI found")
            else:
                print("⚠️  MONGO_URI not found in .env")
    else:
        print("❌ .env file missing")
        print("   Create .env file with:")
        print("   GROQ_API_KEY=your_api_key_here")
        print("   MONGO_URI=your_mongodb_uri")
        print("   PROJECT_NAME=nutri.ai")

def check_requirements():
    """Check if requirements.txt has all necessary packages"""
    print("\n🔍 Checking requirements.txt...")
    
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt exists")
        with open('requirements.txt', 'r') as f:
            content = f.read()
            required_packages = [
                'streamlit',
                'pymongo',
                'transformers',
                'torch',
                'numpy',
                'scipy',
                'plotly',
                'requests',
                'pillow'
            ]
            
            for package in required_packages:
                if package in content:
                    print(f"✅ {package}")
                else:
                    print(f"❌ {package} - MISSING")
    else:
        print("❌ requirements.txt missing")

def create_gitignore():
    """Create .gitignore file if it doesn't exist"""
    print("\n🔍 Checking .gitignore...")
    
    if not os.path.exists('.gitignore'):
        print("📝 Creating .gitignore file...")
        gitignore_content = """# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/

# Logs
*.log
"""
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ .gitignore created")
    else:
        print("✅ .gitignore exists")

def create_readme():
    """Create README.md if it doesn't exist"""
    print("\n🔍 Checking README.md...")
    
    if not os.path.exists('README.md'):
        print("📝 Creating README.md...")
        readme_content = """# nutri.ai - AI-Powered Health & Nutrition Assistant

A comprehensive Streamlit application that provides AI-powered health and nutrition insights.

## Features

- 🍽️ **Nutrition Analyzer**: Analyze food images and get nutritional information
- 🏥 **Hospital Finder**: Find nearby hospitals with AI-generated descriptions
- 💊 **Medicine Dashboard**: Get insights about medicines and drug interactions
- 🥗 **AI Diet Planner**: Plan your meals with AI-powered suggestions
- 🍳 **AI Meal Planner**: Generate personalized meal plans
- 💧 **Water Tracker**: Track your daily water intake
- 🏃 **Exercise Tips**: Get personalized exercise recommendations
- 🤖 **AI Health Assistant**: Ask health-related questions

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env` file
4. Run the app: `streamlit run app.py`

## Environment Variables

- `GROQ_API_KEY`: Your GROQ API key for AI features
- `MONGO_URI`: MongoDB connection string
- `PROJECT_NAME`: Project name (default: nutri.ai)

## Deployment

See `deploy_instructions.md` for detailed deployment instructions.

## License

MIT License
"""
        with open('README.md', 'w') as f:
            f.write(readme_content)
        print("✅ README.md created")
    else:
        print("✅ README.md exists")

def main():
    """Main deployment preparation function"""
    print("🚀 nutri.ai Deployment Preparation")
    print("=" * 50)
    
    # Check all requirements
    missing_files = check_required_files()
    check_env_file()
    check_requirements()
    create_gitignore()
    create_readme()
    
    print("\n" + "=" * 50)
    print("📋 Deployment Summary")
    
    if missing_files:
        print(f"❌ {len(missing_files)} files missing:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n⚠️  Please add missing files before deploying")
    else:
        print("✅ All required files present")
    
    print("\n🎯 Next Steps:")
    print("1. Get a GROQ API key from https://console.groq.com/")
    print("2. Set up MongoDB Atlas (optional)")
    print("3. Update .env file with your API keys")
    print("4. Create a GitHub repository")
    print("5. Upload your files to GitHub")
    print("6. Deploy on Streamlit Cloud or Railway")
    print("\n📖 See deploy_instructions.md for detailed steps")

if __name__ == "__main__":
    main() 