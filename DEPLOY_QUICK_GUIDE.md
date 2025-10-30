# Streamlit Cloud Deployment - Quick Start

## 5 Simple Steps

### 1. Create GitHub Repo
- Go to github.com
- New repository: `aispot-admin-streamlit`
- Make it Private

### 2. Upload Files
Upload ALL project files to GitHub

### 3. Streamlit Cloud
- Go to streamlit.io/cloud
- Sign in with GitHub

### 4. Deploy
- Click "New app"
- Select your repository
- Main file: app.py
- Add secrets (see below)

### 5. Secrets Configuration
```toml
SUPABASE_URL = "https://enszifyeqnwcnxaqrmrq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVuc3ppZnllcW53Y254YXFybXJxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQxMTIyNTcsImV4cCI6MjA2OTY4ODI1N30.eCMgm8ayfG2RNkOSk8iOBEfZMl64gY7a8dLs1W3m79o"
SMTP_HOST = "smtpout.secureserver.net"
SMTP_PORT = 465
SMTP_USE_SSL = true
SMTP_EMAIL = "ai@withArijit.com"
SMTP_PASSWORD = "YOUR_PASSWORD_HERE"
SMTP_BCC = "star.analytix.ai@gmail.com"
```

Replace YOUR_PASSWORD_HERE with actual password.

## Done!
Your app will be at: your-app-name.streamlit.app
