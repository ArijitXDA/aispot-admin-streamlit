# 🤖 AI Spot Admin Dashboard

A professional Streamlit-based admin dashboard for managing AI Spot locations with PDF generation and email functionality.

## ✨ Features

### 📊 Dashboard
- **Real-time data** from Supabase database
- **Statistics cards** showing total, approved, and pending AI Spots
- **Color-coded rows** (green for approved, yellow for pending)
- **Advanced filtering** by search, type, approval status, and state
- **Sorting options** by date and name

### 🔧 Action Buttons (6 per row)
1. **✅ Approve** - Approve pending AI Spots
2. **❌ Disapprove** - Revoke approval
3. **✏️ Edit** - Edit all spot details inline
4. **👁️ View HTML** - Preview standee design
5. **📄 Download PDF** - Generate 2×2 standee layout on A4
6. **📧 Send Email** - Email standee PDF to manager with BCC to admin

### 📄 PDF Generation
- **2×2 Grid Layout** - 4 identical standees per A4 page
- **Professional design** with cutting guides
- **Optimized for printing** - Ready to cut and display
- **Generated on-the-fly** using WeasyPrint

### 📧 Email Functionality
- **GoDaddy SMTP** integration
- **Professional HTML email** template
- **Automatic PDF attachment**
- **Mandatory BCC** to admin email
- **Success/error notifications**

### 🔐 Authentication
- **Secure login** with password hashing
- **Session management** with cookies
- **Auto-logout** after 1 day

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Local Installation

1. **Clone or download the project**
```bash
cd aispot-admin-streamlit
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your SMTP_PASSWORD
```

5. **Run the application**
```bash
streamlit run app.py
```

6. **Access the dashboard**
   - Open browser to: `http://localhost:8501`
   - Login with:
     - **Username:** `admin`
     - **Password:** `arijitwith`

## 📁 Project Structure

```
aispot-admin-streamlit/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── Procfile                    # Railway deployment config
├── runtime.txt                 # Python version
├── .env.example                # Environment variables template
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── templates/
│   └── tablestandee.html      # Standee HTML template
├── utils/
│   ├── __init__.py
│   ├── database.py            # Supabase database operations
│   ├── pdf_generator.py       # PDF generation with WeasyPrint
│   └── email_sender.py        # Email sending with SMTP
├── README.md                   # This file
└── DEPLOYMENT.md              # Railway deployment guide
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Supabase
SUPABASE_URL=https://enszifyeqnwcnxaqrmrq.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Email (GoDaddy SMTP)
SMTP_HOST=smtpout.secureserver.net
SMTP_PORT=465
SMTP_USE_SSL=True
SMTP_EMAIL=ai@withArijit.com
SMTP_PASSWORD=your_smtp_password_here
SMTP_BCC=star.analytix.ai@gmail.com
```

### Supabase Database

The app expects a table named `aispot_master` with these columns:

```sql
- aispot_id (uuid, PK)
- name (text)
- type_of_place (text)
- address, country, state, city, pin_zip (text)
- telephone, mobile (text)
- aispot_email (text)
- owner_manager_name (text)
- email (text)
- price (text)
- ratings (numeric)
- image_url, map_link, qr_code_link (text)
- consent, is_approved (boolean)
- created_at, updated_at (timestamp)
```

## 🎯 Usage Guide

### Login
1. Navigate to dashboard URL
2. Enter username: `admin`
3. Enter password: `arijitwith`
4. Click Login

### Managing AI Spots

#### Approve/Disapprove
- Click **✅ Approve** to approve pending spots
- Click **❌ Disapprove** to revoke approval
- Status updates immediately with visual feedback

#### Edit Record
1. Click **✏️ Edit** button
2. Update fields in the form
3. Click **💾 Save Changes** to update
4. Or click **❌ Cancel** to discard

#### View HTML Preview
1. Click **👁️ View HTML** button
2. Preview the standee design
3. Click **Close Preview** to return

#### Download PDF
1. Click **📄 Download PDF** button
2. PDF generates with 2×2 layout
3. Click **⬇️ Download PDF** to save
4. Print on A4 paper and cut along guides

#### Send Email
1. Click **📧 Send Email** button
2. PDF generates automatically
3. Email sent to manager with BCC to admin
4. Success/error message displayed

### Filtering & Searching

#### Search
- Type in search box to filter by:
  - AI Spot name
  - Type of place
  - City
  - State

#### Filters
- **Type of Place:** Filter by spot type
- **Approval Status:** Show approved/pending only
- **State:** Filter by geographic state

#### Sorting
- Date (Newest/Oldest)
- Name (A-Z/Z-A)

### Tips
- Use **Refresh Data** button to reload from database
- Active filters shown at top of table
- Color coding: Green = Approved, Yellow = Pending
- Session expires after 1 day

## 🧪 Testing

### Test Database Connection
```python
python -c "from utils.database import load_aispot_data; print('✅ Success' if load_aispot_data() is not None else '❌ Failed')"
```

### Test PDF Generation
```python
python utils/pdf_generator.py
# Generates test_standee.pdf
```

### Test Email Configuration
```python
python utils/email_sender.py
# Shows email configuration status
```

## 🔧 Troubleshooting

### WeasyPrint Installation Issues

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y python3-dev libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
pip install WeasyPrint
```

**macOS:**
```bash
brew install pango gdk-pixbuf libffi
pip install WeasyPrint
```

**Windows:**
- Download GTK3 Runtime: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
- Install GTK3
- Add GTK bin to PATH
- `pip install WeasyPrint`

### Database Connection Errors
- Verify SUPABASE_URL and SUPABASE_KEY in .env
- Check Supabase project is active
- Verify table name is `aispot_master`

### Email Sending Errors
- Verify SMTP_PASSWORD is correct
- Check SMTP_EMAIL credentials with GoDaddy
- Ensure port 465 is not blocked by firewall
- Test SMTP settings independently

### PDF Generation Errors
- Ensure WeasyPrint is properly installed
- Check templates/tablestandee.html exists
- Verify QR code links are valid URLs

## 📱 Mobile Responsive

The dashboard is optimized for:
- ✅ Desktop (primary use case)
- ✅ Tablet (limited functionality)
- ⚠️ Mobile (view only, editing not recommended)

## 🔒 Security Notes

- **Password hashing** with bcrypt
- **Session cookies** expire after 1 day
- **HTTPS required** for production
- **Environment variables** for sensitive data
- **No credentials** in code repository

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Railway deployment instructions.

## 📋 Requirements

- Python 3.11+
- Streamlit 1.31.0
- Supabase 2.3.0
- WeasyPrint 60.2
- See requirements.txt for complete list

## 🤝 Support

For issues or questions:
- Email: star.analytix.ai@gmail.com
- Check Supabase console for database issues
- Review Railway logs for deployment issues

## 📄 License

© 2025 AI with Arijit. All rights reserved.

## 🎉 Features Checklist

- [x] Secure authentication
- [x] Real-time Supabase integration
- [x] Approval workflow
- [x] Inline editing
- [x] HTML preview
- [x] 2×2 PDF generation
- [x] Email with attachments
- [x] Advanced filtering
- [x] Responsive design
- [x] Error handling
- [x] Loading states
- [x] Success notifications
- [x] Railway deployment ready

---

**Built with ❤️ using Streamlit**
