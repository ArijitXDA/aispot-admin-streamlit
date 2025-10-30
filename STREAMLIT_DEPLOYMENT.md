# Streamlit Cloud Deployment Guide

## Step-by-Step Deployment

### Step 1: Create GitHub Repository
1. Go to github.com and login
2. Click "+" → "New repository"
3. Name: `aispot-admin-streamlit`
4. Set to Private
5. Create repository

### Step 2: Upload Your Code
Upload all files to GitHub:
- app.py
- requirements.txt
- utils/ folder
- templates/ folder
- .streamlit/ folder
- All other files

### Step 3: Configure Streamlit Cloud
1. Go to streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Main file: app.py

### Step 4: Add Secrets
In Streamlit Cloud, add these secrets:

```toml
SUPABASE_URL = "https://enszifyeqnwcnxaqrmrq.supabase.co"
SUPABASE_KEY = "your_key_here"
SMTP_HOST = "smtpout.secureserver.net"
SMTP_PORT = 465
SMTP_USE_SSL = true
SMTP_EMAIL = "ai@withArijit.com"
SMTP_PASSWORD = "your_password_here"
SMTP_BCC = "star.analytix.ai@gmail.com"
```

### Step 5: Deploy
Click "Deploy" and wait 2-5 minutes.

Your app will be live at: your-app-name.streamlit.app
