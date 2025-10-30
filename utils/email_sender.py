"""
Email Sender utility module
Sends standee PDFs via GoDaddy SMTP with mandatory BCC
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, Optional
import streamlit as st
from utils.pdf_generator import generate_standee_pdf

def get_email_config():
    """Get email configuration from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        if hasattr(st, 'secrets') and 'SMTP_HOST' in st.secrets:
            return {
                'host': st.secrets['SMTP_HOST'],
                'port': int(st.secrets['SMTP_PORT']),
                'use_ssl': st.secrets.get('SMTP_USE_SSL', True),
                'email': st.secrets['SMTP_EMAIL'],
                'password': st.secrets['SMTP_PASSWORD'],
                'bcc': st.secrets['SMTP_BCC']
            }
    except:
        pass
    
    # Fallback to environment variables (for local development)
    return {
        'host': os.getenv("SMTP_HOST", "smtpout.secureserver.net"),
        'port': int(os.getenv("SMTP_PORT", "465")),
        'use_ssl': os.getenv("SMTP_USE_SSL", "True").lower() == "true",
        'email': os.getenv("SMTP_EMAIL", "ai@withArijit.com"),
        'password': os.getenv("SMTP_PASSWORD", ""),
        'bcc': os.getenv("SMTP_BCC", "star.analytix.ai@gmail.com")
    }

def create_email_body(row_data: Dict) -> str:
    """
    Create HTML email body with AI Spot details
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        str: HTML email body
    """
    
    name = row_data.get('name', '')
    type_of_place = row_data.get('type_of_place', '')
    manager_name = row_data.get('owner_manager_name', '')
    aispot_id = row_data.get('aispot_id', '')[:8]
    
    email_html = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
  <h2 style="color: #0055aa;">Dear {manager_name},</h2>
  
  <p>Congratulations! Your AI Spot <strong>"{name}"</strong> has been approved.</p>
  
  <p>Please find attached your official <strong>AI Spot Table Standee PDF</strong>.</p>
  
  <div style="background: #f0f8ff; padding: 15px; border-left: 4px solid #0055aa; margin: 20px 0;">
    <h3 style="margin-top: 0; color: #003366;">Standee Details:</h3>
    <ul style="margin: 10px 0;">
      <li><strong>AI Spot Name:</strong> {name}</li>
      <li><strong>Type:</strong> {type_of_place}</li>
      <li><strong>AI Spot ID:</strong> {aispot_id}</li>
    </ul>
  </div>
  
  <h3 style="color: #0055aa;">Instructions:</h3>
  <ol>
    <li>Download the attached PDF file</li>
    <li>Print on standard A4 size paper</li>
    <li>Cut along the dotted lines to get 4 identical standees</li>
    <li>Display on your table, counter, or reception area</li>
  </ol>
  
  <p style="margin-top: 30px;">For any queries, contact: <a href="mailto:star.analytix.ai@gmail.com">star.analytix.ai@gmail.com</a></p>
  
  <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
  
  <p style="color: #666; font-size: 14px;">
    <strong>Best regards,</strong><br>
    AI with Arijit Team<br>
    <a href="https://www.AIwithArijit.com">www.AIwithArijit.com</a>
  </p>
</body>
</html>
"""
    
    return email_html

def send_standee_email(row_data: Dict) -> bool:
    """
    Send standee PDF via email to manager with BCC to admin
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        bool: Success status
    """
    try:
        # Get email configuration
        config = get_email_config()
        
        # Validate SMTP configuration
        if not config['password']:
            st.error("❌ SMTP password not configured. Please set SMTP_PASSWORD in secrets.")
            return False
        
        recipient_email = row_data.get('email', '')
        if not recipient_email:
            st.error("❌ No recipient email found in record.")
            return False
        
        # Generate PDF
        pdf_bytes = generate_standee_pdf(row_data)
        if not pdf_bytes:
            st.error("❌ Failed to generate PDF for email.")
            return False
        
        # Create message
        msg = MIMEMultipart('mixed')
        msg['From'] = config['email']
        msg['To'] = recipient_email
        msg['Bcc'] = config['bcc']  # MANDATORY BCC
        msg['Subject'] = f"Your AI Spot Table Standee - {row_data.get('name', '')}"
        
        # Add HTML body
        html_body = create_email_body(row_data)
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach PDF
        pdf_attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
        pdf_filename = f"standee_{row_data.get('name', '').replace(' ', '_')}_{row_data.get('aispot_id', '')[:8]}.pdf"
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        msg.attach(pdf_attachment)
        
        # Send email
        if config['use_ssl']:
            # Use SSL (port 465)
            with smtplib.SMTP_SSL(config['host'], config['port']) as server:
                server.login(config['email'], config['password'])
                server.send_message(msg)
        else:
            # Use TLS (port 587)
            with smtplib.SMTP(config['host'], config['port']) as server:
                server.starttls()
                server.login(config['email'], config['password'])
                server.send_message(msg)
        
        return True
    
    except smtplib.SMTPAuthenticationError as e:
        st.error(f"❌ SMTP Authentication failed: {str(e)}")
        st.error("Please verify your email credentials in environment variables.")
        return False
    
    except smtplib.SMTPException as e:
        st.error(f"❌ SMTP Error: {str(e)}")
        return False
    
    except Exception as e:
        st.error(f"❌ Error sending email: {str(e)}")
        return False

def test_email_configuration() -> bool:
    """
    Test email configuration without sending actual email
    
    Returns:
        bool: Configuration valid status
    """
    issues = []
    
    if not SMTP_HOST:
        issues.append("SMTP_HOST not set")
    
    if not SMTP_PORT:
        issues.append("SMTP_PORT not set")
    
    if not SMTP_EMAIL:
        issues.append("SMTP_EMAIL not set")
    
    if not SMTP_PASSWORD:
        issues.append("SMTP_PASSWORD not set")
    
    if not SMTP_BCC:
        issues.append("SMTP_BCC not set")
    
    if issues:
        print("❌ Email configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("✅ Email configuration looks good!")
    print(f"  SMTP Host: {SMTP_HOST}")
    print(f"  SMTP Port: {SMTP_PORT}")
    print(f"  SMTP SSL: {SMTP_USE_SSL}")
    print(f"  From Email: {SMTP_EMAIL}")
    print(f"  BCC Email: {SMTP_BCC}")
    
    return True

def send_test_email(test_recipient: str) -> bool:
    """
    Send a test email to verify configuration
    
    Args:
        test_recipient: Email address to send test to
    
    Returns:
        bool: Success status
    """
    test_data = {
        'name': 'Test AI Spot',
        'type_of_place': 'Testing Facility',
        'owner_manager_name': 'Test Manager',
        'aispot_id': 'test1234-5678-90ab-cdef-1234567890ab',
        'email': test_recipient,
        'qr_code_link': 'https://aiwithArijit.com/test'
    }
    
    print(f"Sending test email to: {test_recipient}")
    result = send_standee_email(test_data)
    
    if result:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Test email failed!")
    
    return result

if __name__ == "__main__":
    # Test email configuration when module is executed directly
    print("Testing email configuration...")
    test_email_configuration()
