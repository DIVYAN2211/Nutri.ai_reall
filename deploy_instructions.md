# 🚀 nutri.ai Deployment Guide

## Option 1: Streamlit Cloud (Recommended)

### Step 1: Prepare Your Repository
1. **Create a GitHub repository** for your project
2. **Upload your files** to GitHub:
   ```
   nutri/
   ├── app.py
   ├── requirements.txt
   ├── .env (or create it on Streamlit Cloud)
   ├── nutrition_analyzer.py
   ├── ai_health_assistant.py
   ├── medicine_dashboard.py
   ├── hospital_finder.py
   ├── diet_planner.py
   ├── ai_meal_planner.py
   ├── water_tracker.py
   ├── exercise_tip.py
   └── auth.py
   ```

### Step 2: Deploy on Streamlit Cloud
1. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and set:
   - **Repository**: `your-username/nutri-ai`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click "Deploy"

### Step 3: Configure Environment Variables
1. In your deployed app, go to **Settings** → **Secrets**
2. Add your environment variables:
   ```toml
   GROQ_API_KEY = "your_actual_groq_api_key"
   MONGO_URI = "your_mongodb_connection_string"
   PROJECT_NAME = "nutri.ai"
   ```

## Option 2: Railway (Alternative)

### Step 1: Create Railway Account
1. Go to [https://railway.app/](https://railway.app/)
2. Sign up with GitHub

### Step 2: Deploy
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway will auto-detect it's a Python app

### Step 3: Add Environment Variables
1. Go to **Variables** tab
2. Add your environment variables

## Option 3: Heroku (Legacy)

### Step 1: Create Heroku Account
1. Go to [https://heroku.com/](https://heroku.com/)
2. Sign up (note: Heroku removed free tier)

### Step 2: Install Heroku CLI
```bash
# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli

# Or use winget
winget install --id=Heroku.HerokuCLI
```

### Step 3: Deploy
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-nutri-app

# Add environment variables
heroku config:set GROQ_API_KEY=your_api_key
heroku config:set MONGO_URI=your_mongodb_uri
heroku config:set PROJECT_NAME=nutri.ai

# Deploy
git add .
git commit -m "Deploy nutri.ai app"
git push heroku main
```

## Option 4: Local Network Deployment

### For Local Network Access:
```bash
# Run with host parameter
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 📋 Pre-Deployment Checklist

### ✅ Required Files
- [ ] `app.py` (main app file)
- [ ] `requirements.txt` (dependencies)
- [ ] All Python modules (`.py` files)
- [ ] `.env` file (or configure on platform)

### ✅ Environment Variables
- [ ] `GROQ_API_KEY` (for AI features)
- [ ] `MONGO_URI` (for database)
- [ ] `PROJECT_NAME` (optional)

### ✅ Dependencies
- [ ] All packages in `requirements.txt`
- [ ] Compatible Python version (3.8+)

## 🔧 Platform-Specific Requirements

### Streamlit Cloud
- **Python version**: 3.8-3.11
- **Memory limit**: 1GB
- **File size limit**: 200MB
- **Deployment time**: ~2-5 minutes

### Railway
- **Python version**: 3.8+
- **Memory**: Configurable
- **Custom domains**: Available
- **Deployment time**: ~1-3 minutes

### Heroku
- **Python version**: 3.8+
- **Memory**: Configurable (paid)
- **Custom domains**: Available
- **Deployment time**: ~2-5 minutes

## 🌐 Custom Domain Setup

### Streamlit Cloud
1. Go to app settings
2. Click "Custom domain"
3. Add your domain
4. Update DNS records

### Railway
1. Go to project settings
2. Add custom domain
3. Update DNS records

## 📊 Monitoring & Analytics

### Streamlit Cloud
- Built-in analytics
- Usage statistics
- Error logs

### Railway
- Real-time logs
- Performance metrics
- Error tracking

## 🔒 Security Considerations

### Environment Variables
- Never commit API keys to Git
- Use platform secrets management
- Rotate keys regularly

### Database Security
- Use MongoDB Atlas (cloud) for production
- Enable authentication
- Use connection strings with credentials

## 🚨 Troubleshooting

### Common Issues:
1. **Import errors**: Check `requirements.txt`
2. **API key errors**: Verify environment variables
3. **Database connection**: Check MongoDB URI
4. **Memory issues**: Optimize app performance

### Debug Commands:
```bash
# Test locally first
streamlit run app.py

# Check requirements
pip install -r requirements.txt

# Test imports
python test_imports.py
```

## 📞 Support

- **Streamlit Cloud**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **Railway**: [https://docs.railway.app/](https://docs.railway.app/)
- **Heroku**: [https://devcenter.heroku.com/](https://devcenter.heroku.com/) 