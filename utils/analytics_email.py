"""
Analytics Email Module
Sends quiz response data and analytics to AI Spot owners
"""

import os
import io
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st
from supabase import create_client, Client

def get_email_config():
    """Get email configuration from Streamlit secrets or environment variables"""
    try:
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
    
    return {
        'host': os.getenv("SMTP_HOST", "smtpout.secureserver.net"),
        'port': int(os.getenv("SMTP_PORT", "465")),
        'use_ssl': os.getenv("SMTP_USE_SSL", "True").lower() == "true",
        'email': os.getenv("SMTP_EMAIL", "ai@withArijit.com"),
        'password': os.getenv("SMTP_PASSWORD", ""),
        'bcc': os.getenv("SMTP_BCC", "star.analytix.ai@gmail.com")
    }

def get_supabase_client() -> Client:
    """Get Supabase client"""
    try:
        if hasattr(st, 'secrets'):
            url = st.secrets.get("SUPABASE_URL")
            key = st.secrets.get("SUPABASE_KEY")
        else:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
        
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to create Supabase client: {str(e)}")
        return None

def fetch_quiz_responses(aispot_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
    """
    Fetch quiz responses for an AI Spot within date range
    
    Args:
        aispot_id: AI Spot ID
        start_date: Start date (None for last 24 hours)
        end_date: End date (None for now)
    
    Returns:
        List of quiz response records
    """
    try:
        supabase = get_supabase_client()
        if not supabase:
            return []
        
        # Default to last 24 hours if no dates provided
        if start_date is None:
            start_date = datetime.now() - timedelta(days=1)
        if end_date is None:
            end_date = datetime.now()
        
        # Query quiz responses
        response = supabase.table('quiz_responses')\
            .select('*')\
            .eq('aispot_id', aispot_id)\
            .gte('created_at', start_date.isoformat())\
            .lte('created_at', end_date.isoformat())\
            .order('created_at', desc=True)\
            .execute()
        
        return response.data if response.data else []
    
    except Exception as e:
        st.error(f"Error fetching quiz responses: {str(e)}")
        return []

def create_csv_from_responses(responses: List[Dict], aispot_name: str) -> bytes:
    """
    Create CSV file from quiz responses
    
    Args:
        responses: List of quiz response records
        aispot_name: AI Spot name
    
    Returns:
        CSV file as bytes
    """
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Responder Name',
            'Email',
            'Mobile',
            'Age',
            'Occupation',
            'Score',
            'Readiness Level',
            'Created At',
            'AI Spot Name'
        ])
        
        # Data rows
        for resp in responses:
            writer.writerow([
                resp.get('name', ''),
                resp.get('email', ''),
                resp.get('mobile', ''),
                resp.get('age', ''),
                resp.get('occupation', ''),
                resp.get('score', ''),
                resp.get('readiness_level', ''),
                resp.get('created_at', ''),
                aispot_name
            ])
        
        return output.getvalue().encode('utf-8')
    
    except Exception as e:
        st.error(f"Error creating CSV: {str(e)}")
        return None

def create_analytics_email_html(aispot_data: Dict, responses: List[Dict], date_range_text: str) -> str:
    """
    Create HTML email with analytics
    
    Args:
        aispot_data: AI Spot record
        responses: List of quiz responses
        date_range_text: Text describing date range (e.g., "today" or "Dec 1-5, 2024")
    
    Returns:
        HTML email content
    """
    
    name = aispot_data.get('name', '')
    manager_name = aispot_data.get('owner_manager_name', '')
    count = len(responses)
    
    # Determine message based on count
    if count <= 5:
        performance_message = """
        <div style="background: #fff4e6; padding: 20px; border-left: 4px solid #ff9800; margin: 25px 0; border-radius: 5px;">
            <p style="margin: 0; font-size: 15px; color: #e65100;">
                <strong>⚠️ Quick Action Needed:</strong> You have not started to utilize the power of AI Spot yet. 
                Believe me, this is super-powerful to help you make more money in your current business setup. 
                <strong>You must take our support to train your team quickly on your tables.</strong> 
                You'll be surprised to see how this small AI standee can increase your revenue very fast.
            </p>
        </div>
        """
    else:
        performance_message = """
        <div style="background: #e8f5e9; padding: 20px; border-left: 4px solid #4caf50; margin: 25px 0; border-radius: 5px;">
            <p style="margin: 0; font-size: 15px; color: #2e7d32;">
                <strong>✅ Great Progress!</strong> You are doing well, and gradually getting stronger grip on your customer base. 
                You must use our analytics email everyday, run campaigns, make a full-blown reachout. 
                <strong>Do not worry</strong>, we have taken their consent so that you can contact them on their phones/emails provided by them.
            </p>
        </div>
        """
    
    # Create data table HTML
    table_rows = ""
    for resp in responses:
        table_rows += f"""
        <tr style="border-bottom: 1px solid #e0e0e0;">
            <td style="padding: 12px; font-size: 14px;">{resp.get('name', '')}</td>
            <td style="padding: 12px; font-size: 14px;">{resp.get('email', '')}</td>
            <td style="padding: 12px; font-size: 14px;">{resp.get('mobile', '')}</td>
            <td style="padding: 12px; font-size: 14px; text-align: center;"><strong>{resp.get('score', '')}</strong></td>
            <td style="padding: 12px; font-size: 14px; text-align: center;">{resp.get('age', '')}</td>
            <td style="padding: 12px; font-size: 14px;">{resp.get('occupation', '')}</td>
            <td style="padding: 12px; font-size: 13px; color: #666;">{resp.get('created_at', '')[:19] if resp.get('created_at') else ''}</td>
        </tr>
        """
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Spot Analytics - {name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background: #f5f5f5;">
    
    <!-- Main Container -->
    <div style="max-width: 900px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #0055aa 0%, #003366 100%); padding: 40px 30px; text-align: center;">
            <h1 style="color: white; margin: 0 0 10px 0; font-size: 28px;">🎯 AI Spot Analytics</h1>
            <p style="color: #a3d9ff; margin: 0; font-size: 16px;">{name}</p>
        </div>
        
        <!-- Hero Section -->
        <div style="padding: 40px 30px; background: #f8f9fa;">
            <h2 style="color: #0055aa; margin: 0 0 20px 0; font-size: 24px;">Dear {manager_name},</h2>
            
            <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 25px; border-radius: 8px; border-left: 5px solid #0055aa;">
                <p style="margin: 0; font-size: 18px; line-height: 1.6;">
                    <strong style="color: #0055aa; font-size: 20px;">{count}</strong> of your guests submitted the Quiz <strong>{date_range_text}</strong>! 🎉
                </p>
            </div>
            
            <p style="font-size: 16px; margin: 25px 0; line-height: 1.8;">
                This data is a <strong style="color: #0055aa;">gold mine</strong> 💎. We have received their consent so that you can 
                <strong>reach out to each of them to make them visit you again</strong>.
            </p>
            
            <p style="font-size: 16px; margin: 25px 0; line-height: 1.8;">
                Let us know, in case you want to run further analytics on your data, or in case you want our help to run 
                <strong>streamlined marketing campaigns to bring them back</strong>. We'll be glad to help you 
                <strong style="color: #4caf50;">increase your revenue this way, faster</strong>. 💰
            </p>
        </div>
        
        <!-- Performance Message -->
        <div style="padding: 0 30px;">
            {performance_message}
        </div>
        
        <!-- Data Grid -->
        <div style="padding: 30px;">
            <h3 style="color: #0055aa; margin: 0 0 20px 0; font-size: 20px;">📊 Customer Data</h3>
            
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; background: white; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background: #0055aa; color: white;">
                            <th style="padding: 15px 12px; text-align: left; font-size: 14px;">Name</th>
                            <th style="padding: 15px 12px; text-align: left; font-size: 14px;">Email</th>
                            <th style="padding: 15px 12px; text-align: left; font-size: 14px;">Mobile</th>
                            <th style="padding: 15px 12px; text-align: center; font-size: 14px;">Score</th>
                            <th style="padding: 15px 12px; text-align: center; font-size: 14px;">Age</th>
                            <th style="padding: 15px 12px; text-align: left; font-size: 14px;">Occupation</th>
                            <th style="padding: 15px 12px; text-align: left; font-size: 14px;">Created At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Additional Benefits -->
        <div style="padding: 30px; background: #f8f9fa;">
            <div style="background: #e8f5e9; padding: 20px; border-left: 4px solid #4caf50; border-radius: 5px;">
                <h3 style="color: #2e7d32; margin: 0 0 10px 0; font-size: 18px;">💰 Bonus Revenue Opportunity</h3>
                <p style="margin: 0; font-size: 15px; color: #2e7d32;">
                    Additionally, if anyone from your AI Spot data enrols in our paid course, 
                    <strong>we'll pay you 10%</strong> to make it sweeter! 🎁
                </p>
            </div>
        </div>
        
        <!-- Closing -->
        <div style="padding: 30px; text-align: center; background: #ffffff;">
            <p style="font-size: 16px; margin: 0 0 10px 0; color: #0055aa;">
                <strong>📧 Wait for my next email with the data and analytics of your AI Spot, again tomorrow.</strong>
            </p>
            <p style="font-size: 16px; margin: 0; color: #666;">
                Same time. See you!!! 👋
            </p>
        </div>
        
        <!-- Footer -->
        <div style="padding: 30px; background: #003366; text-align: center;">
            <p style="color: #a3d9ff; margin: 0 0 10px 0; font-size: 14px;">
                Questions? Contact us at: <a href="mailto:star.analytix.ai@gmail.com" style="color: #66ccff; text-decoration: none;">star.analytix.ai@gmail.com</a>
            </p>
            <p style="color: #a3d9ff; margin: 0; font-size: 14px;">
                <strong>AI with Arijit Team</strong><br>
                <a href="https://www.AIwithArijit.com" style="color: #66ccff; text-decoration: none;">www.AIwithArijit.com</a>
            </p>
        </div>
        
    </div>
    
</body>
</html>
"""
    
    return html

def send_analytics_email(aispot_data: Dict, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> bool:
    """
    Send analytics email to AI Spot owner
    
    Args:
        aispot_data: AI Spot record
        start_date: Start date (None for last 24 hours)
        end_date: End date (None for now)
    
    Returns:
        bool: Success status
    """
    try:
        # Get email configuration
        config = get_email_config()
        
        if not config['password']:
            st.error("❌ SMTP password not configured.")
            return False
        
        recipient_email = aispot_data.get('email', '')
        manager_email = aispot_data.get('manager_email', '')  # CC
        
        if not recipient_email:
            st.error(f"❌ No email found for {aispot_data.get('name', '')}")
            return False
        
        # Fetch quiz responses
        aispot_id = aispot_data.get('aispot_id', '')
        responses = fetch_quiz_responses(aispot_id, start_date, end_date)
        
        # Determine date range text
        if start_date is None:
            date_range_text = "today (last 24 hours)"
        else:
            date_range_text = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        
        # Create CSV attachment
        csv_data = create_csv_from_responses(responses, aispot_data.get('name', ''))
        if not csv_data:
            st.error("❌ Failed to create CSV")
            return False
        
        # Create email
        msg = MIMEMultipart('mixed')
        msg['From'] = config['email']
        msg['To'] = recipient_email
        
        # Add CC if manager email exists
        if manager_email and manager_email != recipient_email:
            msg['Cc'] = manager_email
        
        msg['Bcc'] = config['bcc']
        msg['Subject'] = f"AI Spot, {aispot_data.get('name', '')}, Your customer data and analytics for {date_range_text}"
        
        # Create HTML body
        html_body = create_analytics_email_html(aispot_data, responses, date_range_text)
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach CSV
        csv_filename = f"aispot_{aispot_data.get('name', '').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_attachment = MIMEApplication(csv_data, _subtype='csv')
        csv_attachment.add_header('Content-Disposition', 'attachment', filename=csv_filename)
        msg.attach(csv_attachment)
        
        # Send email
        if config['use_ssl']:
            with smtplib.SMTP_SSL(config['host'], config['port']) as server:
                server.login(config['email'], config['password'])
                server.send_message(msg)
        else:
            with smtplib.SMTP(config['host'], config['port']) as server:
                server.starttls()
                server.login(config['email'], config['password'])
                server.send_message(msg)
        
        return True
    
    except Exception as e:
        st.error(f"❌ Error sending analytics email: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return False

def send_bulk_analytics_emails(all_aispots: List[Dict], start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
    """
    Send analytics emails to all AI Spots
    
    Args:
        all_aispots: List of all AI Spot records
        start_date: Start date
        end_date: End date
    
    Returns:
        Dict with success and failure counts
    """
    results = {
        'success': 0,
        'failed': 0,
        'failed_spots': []
    }
    
    for aispot in all_aispots:
        try:
            success = send_analytics_email(aispot, start_date, end_date)
            if success:
                results['success'] += 1
                st.success(f"✅ Sent to {aispot.get('name', '')}")
            else:
                results['failed'] += 1
                results['failed_spots'].append(aispot.get('name', ''))
        except Exception as e:
            results['failed'] += 1
            results['failed_spots'].append(aispot.get('name', ''))
            st.error(f"❌ Failed for {aispot.get('name', '')}: {str(e)}")
    
    return results
