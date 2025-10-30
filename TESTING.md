# 🧪 Testing Guide

Comprehensive testing guide for AI Spot Admin Dashboard.

## 📋 Pre-Testing Checklist

Before running tests:
- [ ] Python 3.11+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with valid credentials
- [ ] Supabase connection available
- [ ] Templates folder has `tablestandee.html`

## 🔧 Component Testing

### 1. Database Connection Test

**Test Supabase connectivity:**

```bash
python3 << EOF
from utils.database import get_supabase_client, load_aispot_data

print("Testing Supabase connection...")
client = get_supabase_client()
if client:
    print("✅ Supabase client created successfully")
else:
    print("❌ Failed to create Supabase client")
    exit(1)

print("\nTesting data retrieval...")
df = load_aispot_data()
if df is not None and not df.empty:
    print(f"✅ Retrieved {len(df)} records from database")
else:
    print("❌ Failed to retrieve data or table is empty")
    exit(1)

print("\n✅ Database connection test PASSED")
EOF
```

**Expected Output:**
```
Testing Supabase connection...
✅ Supabase client created successfully

Testing data retrieval...
✅ Retrieved X records from database

✅ Database connection test PASSED
```

### 2. PDF Generation Test

**Test PDF creation:**

```bash
python3 << EOF
from utils.pdf_generator import generate_standee_pdf

print("Testing PDF generation...")

test_data = {
    'name': 'Test AI Spot Cafe',
    'type_of_place': 'Cafe & Co-working Space',
    'owner_manager_name': 'Test Manager',
    'aispot_id': 'test1234-5678-90ab-cdef-1234567890ab',
    'qr_code_link': 'https://aiwithArijit.com/test'
}

pdf_bytes = generate_standee_pdf(test_data)

if pdf_bytes:
    print(f"✅ PDF generated successfully ({len(pdf_bytes)} bytes)")
    
    # Save test PDF
    with open('test_output.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print("✅ Test PDF saved as 'test_output.pdf'")
    print("👁️  Please open and verify the 2x2 layout")
else:
    print("❌ PDF generation failed")
    exit(1)

print("\n✅ PDF generation test PASSED")
EOF
```

**Manual Verification:**
1. Open `test_output.pdf`
2. Verify A4 page size
3. Check 2×2 grid layout (4 standees)
4. Verify all placeholders replaced correctly
5. Check cutting guides visible
6. Confirm print-ready quality

### 3. Email Configuration Test

**Test email settings (without sending):**

```bash
python3 << EOF
from utils.email_sender import test_email_configuration
import os

print("Testing email configuration...")
print("\nCurrent Settings:")
print(f"  SMTP_HOST: {os.getenv('SMTP_HOST', 'NOT SET')}")
print(f"  SMTP_PORT: {os.getenv('SMTP_PORT', 'NOT SET')}")
print(f"  SMTP_EMAIL: {os.getenv('SMTP_EMAIL', 'NOT SET')}")
print(f"  SMTP_PASSWORD: {'***' if os.getenv('SMTP_PASSWORD') else 'NOT SET'}")
print(f"  SMTP_BCC: {os.getenv('SMTP_BCC', 'NOT SET')}")
print()

result = test_email_configuration()

if result:
    print("\n✅ Email configuration test PASSED")
else:
    print("\n❌ Email configuration test FAILED")
    exit(1)
EOF
```

**⚠️ Test Email Sending (Optional):**

Only run if you want to send a real test email:

```bash
python3 << EOF
from utils.email_sender import send_test_email

# Replace with your test email
TEST_EMAIL = "your-test-email@example.com"

print(f"Sending test email to: {TEST_EMAIL}")
print("This will actually send an email with PDF attachment!")
print()

response = input("Continue? (yes/no): ")
if response.lower() == 'yes':
    result = send_test_email(TEST_EMAIL)
    if result:
        print("\n✅ Test email sent successfully")
        print("Check your inbox for the email with PDF attachment")
    else:
        print("\n❌ Failed to send test email")
else:
    print("Test cancelled")
EOF
```

### 4. Authentication Test

**Test password hashing:**

```bash
python3 << EOF
import streamlit_authenticator as stauth

print("Testing authentication...")

# Test password hashing
password = 'arijitwith'
hashed = stauth.Hasher([password]).generate()

print(f"✅ Password hashed successfully")
print(f"  Original: {password}")
print(f"  Hashed: {hashed[0][:50]}...")

# Verify hashing is consistent
import bcrypt
test_hash = hashed[0]
is_valid = bcrypt.checkpw(password.encode(), test_hash.encode())

if is_valid:
    print("✅ Password verification works")
else:
    print("❌ Password verification failed")
    exit(1)

print("\n✅ Authentication test PASSED")
EOF
```

## 🌐 Application Testing

### 1. Local Application Test

**Start the application:**

```bash
streamlit run app.py
```

**Manual Test Checklist:**

#### Login Page
- [ ] Page loads without errors
- [ ] Username field present
- [ ] Password field present
- [ ] Login button works
- [ ] Wrong credentials show error
- [ ] Correct credentials (`admin`/`arijitwith`) login successfully

#### Dashboard
- [ ] Welcome message displays username
- [ ] Statistics cards show correct counts
- [ ] Logout button present in sidebar
- [ ] Data table loads with records
- [ ] All columns display correctly

#### Filtering & Search
- [ ] Search box filters by name
- [ ] Search box filters by city
- [ ] Search box filters by state
- [ ] Type dropdown filters correctly
- [ ] Approval status filter works
- [ ] State dropdown filters correctly
- [ ] Sort options work (date/name)
- [ ] Active filters display correctly
- [ ] Refresh button reloads data

#### Action Buttons - Per Row
1. **✅ Approve Button**
   - [ ] Button visible for pending records
   - [ ] Clicking updates status to approved
   - [ ] Success message displays
   - [ ] Table refreshes automatically
   - [ ] Database updated correctly

2. **❌ Disapprove Button**
   - [ ] Button visible for approved records
   - [ ] Clicking updates status to pending
   - [ ] Warning message displays
   - [ ] Table refreshes automatically
   - [ ] Database updated correctly

3. **✏️ Edit Button**
   - [ ] Opens edit form
   - [ ] All fields populate correctly
   - [ ] Read-only fields display
   - [ ] Can modify editable fields
   - [ ] Save updates database
   - [ ] Cancel closes form
   - [ ] Form validates email

4. **👁️ View HTML Button**
   - [ ] Opens HTML preview
   - [ ] Standee displays correctly
   - [ ] All placeholders replaced
   - [ ] QR code visible
   - [ ] Close button returns to table

5. **📄 Download PDF Button**
   - [ ] Generates PDF successfully
   - [ ] Download button appears
   - [ ] PDF downloads correctly
   - [ ] Filename format correct
   - [ ] PDF opens in viewer
   - [ ] 2×2 layout correct
   - [ ] All 4 standees identical

6. **📧 Send Email Button**
   - [ ] Clicking triggers email
   - [ ] Loading spinner shows
   - [ ] Success message on completion
   - [ ] Email received at manager address
   - [ ] BCC received at admin address
   - [ ] PDF attached correctly
   - [ ] Email content correct

#### Error Handling
- [ ] Database errors show friendly message
- [ ] Network errors handled gracefully
- [ ] Invalid data shows validation errors
- [ ] Loading states during operations
- [ ] Errors don't crash application

#### Performance
- [ ] Page loads in < 3 seconds
- [ ] Table filtering is responsive
- [ ] PDF generation < 5 seconds
- [ ] Email sending < 10 seconds
- [ ] No memory leaks over time

### 2. Cross-Browser Testing

Test in multiple browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### 3. Responsive Design Testing

Test on different screen sizes:
- [ ] Desktop (1920×1080)
- [ ] Laptop (1366×768)
- [ ] Tablet (768×1024)
- [ ] Mobile (375×667) - view only

## 🔄 Integration Testing

### End-to-End Workflow Test

**Scenario: New AI Spot Approval**

1. **Initial State**
   - [ ] Log into dashboard
   - [ ] Find pending AI Spot

2. **Approval Process**
   - [ ] Click ✅ Approve button
   - [ ] Verify status changes
   - [ ] Check database updated

3. **PDF Generation**
   - [ ] Click 📄 Download PDF
   - [ ] Verify PDF generates
   - [ ] Download and open PDF
   - [ ] Verify 2×2 layout correct

4. **Email Notification**
   - [ ] Click 📧 Send Email
   - [ ] Verify success message
   - [ ] Check manager email inbox
   - [ ] Check admin BCC inbox
   - [ ] Verify PDF attached
   - [ ] Verify email content

5. **Record Edit**
   - [ ] Click ✏️ Edit
   - [ ] Modify field
   - [ ] Save changes
   - [ ] Verify update in table

**Scenario: Data Filtering**

1. **Search Functionality**
   - [ ] Enter search term
   - [ ] Verify filtered results
   - [ ] Clear search
   - [ ] Verify all records return

2. **Combined Filters**
   - [ ] Set type filter
   - [ ] Set approval filter
   - [ ] Set state filter
   - [ ] Verify results match all filters
   - [ ] Clear all filters

## 🐛 Bug Testing

### Common Issues to Check

1. **Session Handling**
   - [ ] Session persists on refresh
   - [ ] Logout clears session
   - [ ] Session expires correctly

2. **Data Integrity**
   - [ ] No data corruption on edit
   - [ ] Concurrent updates handled
   - [ ] Rollback on error

3. **Edge Cases**
   - [ ] Empty database handled
   - [ ] Special characters in names
   - [ ] Very long text fields
   - [ ] Missing QR code links
   - [ ] Invalid email addresses

4. **Security**
   - [ ] Can't access without login
   - [ ] SQL injection prevented
   - [ ] XSS attacks prevented
   - [ ] CSRF protection enabled

## 📊 Performance Testing

### Load Testing (Optional)

Test with multiple concurrent users:

```python
# test_performance.py
import concurrent.futures
import requests
import time

def test_concurrent_access(n_users=5):
    url = "http://localhost:8501"
    
    def access_dashboard(user_id):
        start = time.time()
        response = requests.get(url)
        duration = time.time() - start
        return user_id, response.status_code, duration
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_users) as executor:
        futures = [executor.submit(access_dashboard, i) for i in range(n_users)]
        results = [f.result() for f in futures]
    
    for user_id, status, duration in results:
        print(f"User {user_id}: Status {status}, Time {duration:.2f}s")

if __name__ == "__main__":
    test_concurrent_access()
```

## ✅ Testing Completion Checklist

Before deploying to production:

### Core Functionality
- [ ] Authentication works
- [ ] Database connection stable
- [ ] All CRUD operations work
- [ ] PDF generation successful
- [ ] Email sending operational

### UI/UX
- [ ] Responsive design works
- [ ] All buttons functional
- [ ] Error messages clear
- [ ] Loading states visible
- [ ] Navigation intuitive

### Data Integrity
- [ ] No data loss on updates
- [ ] Transactions atomic
- [ ] Error recovery works
- [ ] Validation effective

### Performance
- [ ] Page load < 3 seconds
- [ ] Operations complete timely
- [ ] No memory leaks
- [ ] Handles expected load

### Security
- [ ] Authentication required
- [ ] Passwords hashed
- [ ] Sessions secure
- [ ] Input validated
- [ ] HTTPS ready

## 📝 Test Report Template

```markdown
# Test Report - AI Spot Admin Dashboard

**Date:** YYYY-MM-DD
**Tester:** Your Name
**Environment:** Local / Railway

## Test Summary
- Total Tests: X
- Passed: X
- Failed: X
- Skipped: X

## Failed Tests
1. Test Name
   - Expected: ...
   - Actual: ...
   - Error: ...

## Performance Metrics
- Page Load: X seconds
- PDF Generation: X seconds
- Email Sending: X seconds

## Recommendations
- [ ] Issue 1: Description and fix
- [ ] Issue 2: Description and fix

## Sign-off
All critical tests passed: YES / NO
Ready for deployment: YES / NO
```

## 🚨 Critical Issues

If any of these fail, **DO NOT DEPLOY**:
- [ ] Authentication broken
- [ ] Database connection fails
- [ ] Email password invalid
- [ ] PDF generation errors
- [ ] Data corruption possible

---

**Testing completed? Ready to deploy!** 🚀

See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment instructions.
