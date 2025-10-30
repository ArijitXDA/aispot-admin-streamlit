# 🚀 Railway Deployment Guide

Complete step-by-step guide to deploy AI Spot Admin Dashboard on Railway.app with custom domain.

## 📋 Prerequisites

Before starting deployment:
- ✅ Railway.app account (free tier available)
- ✅ GitHub account
- ✅ Domain registrar access (for admin.aiwithArijit.com)
- ✅ GoDaddy SMTP password for ai@withArijit.com
- ✅ Project code pushed to GitHub repository

## 🎯 Deployment Steps

### Step 1: Prepare Your Repository

1. **Create GitHub Repository**
   ```bash
   # Initialize git (if not already done)
   git init
   
   # Add all files
   git add .
   
   # Commit
   git commit -m "Initial commit: AI Spot Admin Dashboard"
   
   # Create repository on GitHub and push
   git remote add origin https://github.com/yourusername/aispot-admin.git
   git branch -M main
   git push -u origin main
   ```

2. **Verify Required Files**
   - ✅ `app.py` - Main application
   - ✅ `requirements.txt` - Dependencies
   - ✅ `Procfile` - Railway start command
   - ✅ `runtime.txt` - Python version
   - ✅ `.streamlit/config.toml` - Streamlit config
   - ✅ `templates/tablestandee.html` - Standee template
   - ✅ `utils/` directory with all modules

3. **Create `.gitignore`**
   ```
   # Create .gitignore to exclude sensitive files
   .env
   .venv
   venv/
   __pycache__/
   *.pyc
   *.pyo
   .DS_Store
   *.pdf
   test_*.py
   ```

### Step 2: Create Railway Project

1. **Go to Railway.app**
   - Visit: https://railway.app
   - Click **"Start a New Project"**

2. **Deploy from GitHub**
   - Click **"Deploy from GitHub repo"**
   - Authorize Railway to access your GitHub
   - Select your repository: `aispot-admin`

3. **Railway Auto-Detection**
   - Railway will detect Python project
   - Will read `Procfile` for start command
   - Will install from `requirements.txt`

### Step 3: Configure Environment Variables

1. **In Railway Dashboard**
   - Click on your project
   - Go to **"Variables"** tab
   - Click **"New Variable"**

2. **Add These Variables** (one by one):

   ```bash
   # Supabase Configuration
   SUPABASE_URL=https://enszifyeqnwcnxaqrmrq.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVuc3ppZnllcW53Y254YXFybXJxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQxMTIyNTcsImV4cCI6MjA2OTY4ODI1N30.eCMgm8ayfG2RNkOSk8iOBEfZMl64gY7a8dLs1W3m79o
   
   # Email Configuration (GoDaddy SMTP)
   SMTP_HOST=smtpout.secureserver.net
   SMTP_PORT=465
   SMTP_USE_SSL=True
   SMTP_EMAIL=ai@withArijit.com
   SMTP_PASSWORD=your_actual_smtp_password_here
   SMTP_BCC=star.analytix.ai@gmail.com
   
   # Authentication (optional, using defaults)
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=arijitwith
   AUTH_COOKIE_KEY=aispot_admin_cookie_key_12345
   ```

   **⚠️ CRITICAL:** Replace `your_actual_smtp_password_here` with real password!

3. **Save Variables**
   - Click **"Add"** for each variable
   - Railway will redeploy automatically

### Step 4: Deploy Application

1. **Initial Deployment**
   - Railway starts deployment automatically
   - Monitor logs in **"Deployments"** tab
   - Watch for successful build messages

2. **Check Build Logs**
   Look for:
   ```
   ✓ Installing dependencies from requirements.txt
   ✓ Building application
   ✓ Starting web process: streamlit run app.py
   ✓ Deployment successful
   ```

3. **Get Deployment URL**
   - Railway provides temporary URL
   - Format: `https://your-app-name.up.railway.app`
   - Click to test your dashboard

### Step 5: Verify Deployment

1. **Test Application**
   - Visit the Railway-provided URL
   - Login with: `admin` / `arijitwith`
   - Test all features:
     - ✅ Dashboard loads
     - ✅ Data displays from Supabase
     - ✅ Filters work
     - ✅ Approve/Disapprove buttons
     - ✅ Edit functionality
     - ✅ HTML preview
     - ✅ PDF generation
     - ✅ Email sending

2. **Check Logs for Errors**
   - In Railway dashboard, click **"View Logs"**
   - Look for any Python errors
   - Verify Supabase connections
   - Check email sending attempts

### Step 6: Get Your FREE Railway URL

#### Automatic URL Generation

1. **Railway Provides Free URL**
   - After deployment completes
   - Go to **"Settings"** tab
   - Look for **"Domains"** section
   - You'll see: `your-app-name.up.railway.app`

2. **URL Format**
   ```
   https://aispot-admin-production.up.railway.app
   https://aispot-admin.up.railway.app
   ```
   (Railway auto-generates based on your repo/project name)

3. **Access Your Dashboard**
   - Click the URL
   - Opens your live dashboard
   - Login with: admin / arijitwith

#### SSL Certificate (Automatic)

Railway automatically provisions SSL certificates:
- Uses Let's Encrypt
- Provisions within 2-5 minutes
- Renews automatically
- Forces HTTPS

**Verify SSL:**
- Visit your Railway URL
- Check for padlock icon in browser
- Click padlock to view certificate details

### Step 7: Post-Deployment Configuration

#### Update Streamlit Settings (if needed)

If you need to adjust settings, update `.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = true
enableCORS = true  # Enable if needed for external resources
enableXsrfProtection = true
baseUrlPath = ""

[browser]
serverAddress = "0.0.0.0"
serverPort = 8501
```

Push changes to GitHub, Railway auto-deploys.

#### Configure Railway Settings

1. **Build Settings**
   - Build Command: Auto-detected from `Procfile`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

2. **Health Check** (optional)
   - Railway can monitor app health
   - Set endpoint: `/`
   - Timeout: 30 seconds

3. **Auto-Deploy**
   - Enable: Deploy on Git push
   - Branch: `main`

### Step 8: Monitoring & Maintenance

#### Railway Dashboard

1. **Metrics**
   - CPU usage
   - Memory usage
   - Request count
   - Error rate

2. **Logs**
   - Real-time application logs
   - Error tracking
   - Performance monitoring

3. **Deployments History**
   - View past deployments
   - Rollback if needed
   - Compare versions

#### Set Up Alerts (optional)

1. **Railway Notifications**
   - Deployment success/failure
   - Error threshold alerts
   - Resource usage warnings

2. **Email Notifications**
   - Configure in Railway settings
   - Get notified on issues

### Step 9: Scaling (if needed)

#### Railway Pricing Tiers

1. **Hobby Plan** (Free)
   - $5 credit/month
   - Good for testing
   - May sleep after inactivity

2. **Pro Plan** ($20/month)
   - More resources
   - No sleep
   - Better performance

3. **Upgrade if needed**
   - Click "Upgrade" in dashboard
   - Select plan
   - Add payment method

#### Scaling Options

If traffic increases:
- **Horizontal:** Deploy multiple instances
- **Vertical:** Increase resources per instance
- Railway handles load balancing

## 🔧 Troubleshooting

### Deployment Fails

**Build Errors:**
```bash
# Check requirements.txt has all dependencies
# Verify Python version in runtime.txt matches
# Check Railway logs for specific error
```

**WeasyPrint Install Issues:**
Railway might need additional system packages:
```bash
# Add nixpacks.toml to root:
[phases.setup]
nixPkgs = ["python311", "cairo", "pango", "gdk-pixbuf", "libffi"]
```

### Application Won't Start

1. **Check Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Verify Environment Variables**
   - All variables set correctly
   - No typos in variable names
   - SMTP_PASSWORD is correct

3. **Check Logs**
   - Look for Python import errors
   - Verify Supabase connection
   - Check for missing dependencies

### Database Connection Issues

1. **Verify Supabase Credentials**
   - SUPABASE_URL is correct
   - SUPABASE_KEY is valid
   - Check Supabase project is active

2. **Test Connection**
   ```python
   # In Railway shell or logs
   from utils.database import get_supabase_client
   client = get_supabase_client()
   ```

### Email Not Sending

1. **Check SMTP Settings**
   - SMTP_HOST: `smtpout.secureserver.net`
   - SMTP_PORT: `465`
   - SMTP_USE_SSL: `True`

2. **Verify Credentials**
   - SMTP_EMAIL: `ai@withArijit.com`
   - SMTP_PASSWORD: Correct password
   - Test with: `python utils/email_sender.py`

3. **Firewall/Port Issues**
   - Railway allows outbound port 465
   - GoDaddy SMTP should work from Railway

### Custom Domain Not Working (Optional Feature)

**Note:** Custom domains are optional. Your app works perfectly with the free Railway URL!

If you decide to add a custom domain later:

1. **DNS Propagation**
   - Wait 24 hours for full propagation
   - Use incognito/private browsing
   - Clear DNS cache: `ipconfig /flushdns` (Windows)

2. **CNAME Record Correct**
   ```
   your-domain.com -> your-app.up.railway.app
   ```

3. **SSL Certificate**
   - Wait 10-15 minutes after DNS propagates
   - Railway auto-provisions
   - Check Railway domain settings

### Performance Issues

1. **Check Resource Usage**
   - Railway dashboard shows metrics
   - Upgrade plan if maxing out
   - Optimize database queries

2. **Cache Management**
   - Streamlit caching helps
   - Adjust TTL in `@st.cache_data(ttl=300)`

3. **Database Optimization**
   - Add indexes in Supabase
   - Limit query results
   - Use pagination

## 📊 Monitoring Best Practices

### Regular Checks

- **Daily:** Check logs for errors
- **Weekly:** Review usage metrics
- **Monthly:** Verify email delivery
- **Quarterly:** Update dependencies

### Backup Strategy

1. **Database:** Supabase handles backups
2. **Code:** GitHub repository
3. **Environment Variables:** Document separately

### Update Process

1. **Test Locally**
   ```bash
   # Make changes
   # Test thoroughly
   git add .
   git commit -m "Description of changes"
   ```

2. **Deploy to Railway**
   ```bash
   git push origin main
   # Railway auto-deploys
   # Monitor deployment logs
   ```

3. **Verify Production**
   - Test critical features
   - Check logs for errors
   - Rollback if issues

## 🎯 Success Checklist

Before considering deployment complete:

- [ ] Application deployed successfully on Railway
- [ ] Environment variables configured
- [ ] Database connection working
- [ ] Login authentication functional
- [ ] All 6 action buttons work
- [ ] PDF generation successful
- [ ] Email sending operational
- [ ] FREE Railway URL working (https://your-app.up.railway.app)
- [ ] SSL certificate installed
- [ ] No errors in logs
- [ ] Monitoring set up
- [ ] Documentation reviewed

## 📞 Support Resources

### Railway Support
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Streamlit Support
- Documentation: https://docs.streamlit.io
- Community: https://discuss.streamlit.io

### Supabase Support
- Documentation: https://supabase.com/docs
- Community: https://github.com/supabase/supabase/discussions

### Email Support
- GoDaddy SMTP: https://www.godaddy.com/help
- Contact: star.analytix.ai@gmail.com

---

## 🎉 Deployment Complete!

Your AI Spot Admin Dashboard is now live at:
**https://your-app-name.up.railway.app**

(Railway will show you the exact URL in the dashboard)

**Default Credentials:**
- Username: `admin`
- Password: `arijitwith`

**🔒 Security Reminder:** Change default password in production!

**💡 Optional:** You can add a custom domain later if needed (follow Railway docs)

---

**Built with ❤️ and deployed on Railway - 100% FREE!**
