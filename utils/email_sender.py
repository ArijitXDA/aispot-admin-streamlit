"""
Email Sender utility module
Sends standee HTML directly as email body (single standee with print button)
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional
import streamlit as st
from utils.pdf_generator import generate_preview_html

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

def send_standee_email(row_data: Dict) -> bool:
    """
    Send standee HTML as email body (exactly as shown in "View HTML")
    
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
        
        # Generate the standee HTML (exactly as "View HTML" shows)
        html_body = generate_preview_html(row_data)
        
        if not html_body:
            st.error("❌ Failed to generate HTML for email.")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = config['email']
        msg['To'] = recipient_email
        msg['Bcc'] = config['bcc']  # MANDATORY BCC
        msg['Subject'] = "AI Spot Standee - Print this in color and display on your tables (6inch x 4inch)"
        
        # Plain text alternative
        text_body = f"""
AI Spot Standee

Dear {row_data.get('owner_manager_name', '')},

Please open this email in an email client that supports HTML to view your AI Spot standee.

Instructions:
1. Open this email on a computer
2. Click the "Download the PDF Table-Standee Poster" button
3. Print in color on A4 paper
4. Cut to 6 inch x 4 inch size
5. Display on your tables

Your AI Spot Details:
- Name: {row_data.get('name', '')}
- Type: {row_data.get('type_of_place', '')}
- Manager: {row_data.get('owner_manager_name', '')}
- AI Spot ID: {row_data.get('aispot_id', '')[:8]}

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
