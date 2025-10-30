"""
Email Sender utility module
Sends standee HTML embedded in email body with 2x2 grid layout
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional
import streamlit as st
from utils.pdf_generator import generate_preview_html, create_2x2_grid_html

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

def create_email_body_with_standee(row_data: Dict) -> str:
    """
    Create HTML email body with embedded AI Spot standee (2x2 grid)
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        str: Complete HTML email with embedded standee
    """
    
    name = row_data.get('name', '')
    type_of_place = row_data.get('type_of_place', '')
    manager_name = row_data.get('owner_manager_name', '')
    aispot_id = row_data.get('aispot_id', '')[:8]
    
    # Generate the single standee HTML
    standee_html = generate_preview_html(row_data)
    
    # Remove download section
    standee_html = standee_html.replace('<div class="download-section">', '<div class="download-section" style="display: none;">')
    
    # Create 2x2 grid layout
    grid_html = create_2x2_grid_html(standee_html)
    
    # Create email with greeting message + embedded standee
    email_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your AI Spot Table Standee</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background: #f5f5f5;">
  
  <!-- Greeting Section -->
  <div style="max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    <h2 style="color: #0055aa; margin-top: 0;">Dear {manager_name},</h2>
    
    <p style="font-size: 16px;">Congratulations! 🎉 Your AI Spot <strong>"{name}"</strong> has been approved.</p>
    
    <div style="background: #e6f7ff; padding: 20px; border-left: 4px solid #0055aa; margin: 25px 0; border-radius: 5px;">
      <h3 style="margin-top: 0; color: #003366;">Your AI Spot Details:</h3>
      <ul style="margin: 10px 0; padding-left: 20px;">
        <li><strong>AI Spot Name:</strong> {name}</li>
        <li><strong>Type:</strong> {type_of_place}</li>
        <li><strong>Manager:</strong> {manager_name}</li>
        <li><strong>AI Spot ID:</strong> {aispot_id}</li>
      </ul>
    </div>
    
    <h3 style="color: #0055aa;">📋 How to Use Your Standee:</h3>
    <ol style="font-size: 15px; line-height: 1.8;">
      <li><strong>Print:</strong> Open this email on a computer and print (Ctrl+P or Cmd+P)</li>
      <li><strong>Paper:</strong> Use standard A4 size paper for best results</li>
      <li><strong>Cut:</strong> Follow the dotted lines to get 4 identical standees</li>
      <li><strong>Display:</strong> Place on your table, counter, or reception area</li>
    </ol>
    
    <div style="background: #fff4e6; padding: 15px; border-left: 4px solid #ff9800; margin: 25px 0; border-radius: 5px;">
      <p style="margin: 0; font-size: 14px;"><strong>💡 Tip:</strong> Scroll down to see your standee design below. You can print this entire email to get your 2×2 standee grid!</p>
    </div>
    
    <p style="margin-top: 30px; font-size: 15px;">Questions? Contact us at: <a href="mailto:star.analytix.ai@gmail.com" style="color: #0055aa;">star.analytix.ai@gmail.com</a></p>
    
    <hr style="border: none; border-top: 2px solid #e0e0e0; margin: 40px 0;">
    
    <p style="color: #666; font-size: 14px; margin-bottom: 0;">
      <strong>Best regards,</strong><br>
      AI with Arijit Team<br>
      <a href="https://www.AIwithArijit.com" style="color: #0055aa; text-decoration: none;">www.AIwithArijit.com</a>
    </p>
  </div>
  
  <!-- Standee Section (2x2 Grid) -->
  <div style="margin-top: 50px; page-break-before: always;">
    <h2 style="text-align: center; color: #0055aa; font-size: 24px; margin-bottom: 30px;">
      🖨️ Your AI Spot Table Standee (2×2 Grid)
    </h2>
    <div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 20px;">
      Print this page on A4 paper and cut along the dotted lines
    </div>
    
    {grid_html}
  </div>
  
</body>
</html>
"""
    
    return email_html

def send_standee_email(row_data: Dict) -> bool:
    """
    Send standee HTML embedded in email to manager with BCC to admin
    
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
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = config['email']
        msg['To'] = recipient_email
        msg['Bcc'] = config['bcc']  # MANDATORY BCC
        msg['Subject'] = f"🎉 Your AI Spot Table Standee - {row_data.get('name', '')}"
        
        # Create HTML body with embedded standee
        html_body = create_email_body_with_standee(row_data)
        
        # Add plain text alternative
        text_body = f"""
Dear {row_data.get('owner_manager_name', '')},

Congratulations! Your AI Spot "{row_data.get('name', '')}" has been approved.

Your AI Spot Details:
- Name: {row_data.get('name', '')}
- Type: {row_data.get('type_of_place', '')}
- Manager: {row_data.get('owner_manager_name', '')}
- AI Spot ID: {row_data.get('aispot_id', '')[:8]}

Please open this email in an email client that supports HTML to view your standee design.

Instructions:
1. Open this email on a computer
2. Print the email (Ctrl+P or Cmd+P)
3. Use A4 paper
4. Cut along dotted lines to get 4 standees
5. Display at your location

Questions? Contact: star.analytix.ai@gmail.com

Best regards,
AI with Arijit Team
www.AIwithArijit.com
"""
        
        # Attach both versions
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
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
        st.error("Please verify your email credentials in secrets.")
        return False
    
    except smtplib.SMTPException as e:
        st.error(f"❌ SMTP Error: {str(e)}")
        return False
    
    except Exception as e:
        st.error(f"❌ Error sending email: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_email_configuration() -> bool:
    """
    Test email configuration without sending actual email
    
    Returns:
        bool: Configuration valid status
    """
    config = get_email_config()
    issues = []
    
    if not config['host']:
        issues.append("SMTP_HOST not set")
    
    if not config['port']:
        issues.append("SMTP_PORT not set")
    
    if not config['email']:
        issues.append("SMTP_EMAIL not set")
    
    if not config['password']:
        issues.append("SMTP_PASSWORD not set")
    
    if not config['bcc']:
        issues.append("SMTP_BCC not set")
    
    if issues:
        print("❌ Email configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("✅ Email configuration looks good!")
    print(f"  SMTP Host: {config['host']}")
    print(f"  SMTP Port: {config['port']}")
    print(f"  SMTP SSL: {config['use_ssl']}")
    print(f"  From Email: {config['email']}")
    print(f"  BCC Email: {config['bcc']}")
    
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
        'name': 'Test AI Spot Cafe',
        'type_of_place': 'Testing Facility',
        'owner_manager_name': 'Test Manager',
        'aispot_id': 'test1234-5678-90ab-cdef-1234567890ab',
        'email': test_recipient,
        'qr_code_link': 'https://aiwithArijit.com/ai-spot/test'
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
