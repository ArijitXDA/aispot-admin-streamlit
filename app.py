"""
AI Spot Admin Dashboard - Streamlit Application
Main application file with authentication and dashboard functionality
"""

import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from datetime import datetime
import time
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import utility modules
from utils.database import (
    get_supabase_client,
    load_aispot_data,
    update_approval_status,
    update_aispot_record,
    get_aispot_by_id
)
from utils.pdf_generator import generate_standee_pdf
from utils.email_sender import send_standee_email

# Page configuration
st.set_page_config(
    page_title="AI Spot Admin Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .approved-row {
        background-color: #d4edda !important;
    }
    .pending-row {
        background-color: #fff3cd !important;
    }
    .stButton button {
        width: 100%;
        padding: 0.3rem 0.5rem;
        font-size: 0.85rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    h1 {
        color: #0055aa;
    }
    .success-msg {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-msg {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Authentication setup
def setup_authentication():
    """Setup authentication with streamlit-authenticator"""
    # Hash password for 'arijitwith'
    hashed_passwords = stauth.Hasher(['arijitwith']).generate()
    
    credentials = {
        'usernames': {
            'admin': {
                'name': 'Admin User',
                'password': hashed_passwords[0]
            }
        }
    }
    
    authenticator = stauth.Authenticate(
        credentials,
        'aispot_admin',
        'aispot_admin_cookie_key_12345',
        cookie_expiry_days=1
    )
    
    return authenticator

def display_stats(df):
    """Display statistics cards at the top"""
    total_spots = len(df)
    approved_spots = len(df[df['is_approved'] == True])
    pending_spots = total_spots - approved_spots
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <p class="stat-number">{total_spots}</p>
            <p class="stat-label">Total AI Spots</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);">
            <p class="stat-number">{approved_spots}</p>
            <p class="stat-label">✅ Approved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);">
            <p class="stat-number">{pending_spots}</p>
            <p class="stat-label">⏳ Pending</p>
        </div>
        """, unsafe_allow_html=True)

def apply_filters(df, search_query, type_filter, approval_filter, state_filter):
    """Apply filters to dataframe"""
    filtered_df = df.copy()
    
    # Search filter
    if search_query:
        mask = (
            filtered_df['name'].str.contains(search_query, case=False, na=False) |
            filtered_df['type_of_place'].str.contains(search_query, case=False, na=False) |
            filtered_df['city'].str.contains(search_query, case=False, na=False) |
            filtered_df['state'].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Type filter
    if type_filter != "All":
        filtered_df = filtered_df[filtered_df['type_of_place'] == type_filter]
    
    # Approval filter
    if approval_filter == "Approved":
        filtered_df = filtered_df[filtered_df['is_approved'] == True]
    elif approval_filter == "Pending":
        filtered_df = filtered_df[filtered_df['is_approved'] == False]
    
    # State filter
    if state_filter != "All":
        filtered_df = filtered_df[filtered_df['state'] == state_filter]
    
    return filtered_df

def display_edit_form(row):
    """Display edit form for a row"""
    st.subheader(f"Edit: {row['name']}")
    
    with st.form(key=f"edit_form_{row['aispot_id']}"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", value=row['name'])
            type_of_place = st.text_input("Type of Place", value=row['type_of_place'])
            owner_manager_name = st.text_input("Manager Name", value=row['owner_manager_name'])
            email = st.text_input("Email", value=row['email'])
            mobile = st.text_input("Mobile", value=row['mobile'] or "")
            telephone = st.text_input("Telephone", value=row['telephone'] or "")
        
        with col2:
            address = st.text_area("Address", value=row['address'] or "")
            city = st.text_input("City", value=row['city'] or "")
            state = st.text_input("State", value=row['state'] or "")
            country = st.text_input("Country", value=row['country'] or "")
            pin_zip = st.text_input("PIN/ZIP", value=row['pin_zip'] or "")
            price = st.text_input("Price", value=row['price'] or "")
        
        st.markdown("---")
        st.markdown("**Read-only Information:**")
        st.text(f"AI Spot ID: {row['aispot_id'][:8]}")
        st.text(f"Created At: {row['created_at']}")
        st.text(f"QR Code Link: {row['qr_code_link']}")
        
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            submit = st.form_submit_button("💾 Save Changes", use_container_width=True)
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submit:
            updated_data = {
                'name': name,
                'type_of_place': type_of_place,
                'owner_manager_name': owner_manager_name,
                'email': email,
                'mobile': mobile,
                'telephone': telephone,
                'address': address,
                'city': city,
                'state': state,
                'country': country,
                'pin_zip': pin_zip,
                'price': price
            }
            
            success = update_aispot_record(row['aispot_id'], updated_data)
            
            if success:
                st.success("✅ Record updated successfully!")
                time.sleep(1)
                st.session_state.editing_row = None
                st.rerun()
            else:
                st.error("❌ Failed to update record. Please try again.")
        
        if cancel:
            st.session_state.editing_row = None
            st.rerun()

def display_html_preview(row):
    """Display HTML preview of standee"""
    st.subheader(f"HTML Preview: {row['name']}")
    
    # Load template
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'tablestandee.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    # Replace placeholders
    html_content = html_template.replace('{{name}}', row['name'])
    html_content = html_content.replace('{{type_of_place}}', row['type_of_place'])
    html_content = html_content.replace('{{manager_name}}', row['owner_manager_name'])
    html_content = html_content.replace('{{aispot_id}}', row['aispot_id'][:8])
    html_content = html_content.replace('{{qr_code_link}}', row['qr_code_link'])
    
    # Display HTML in iframe
    st.components.v1.html(html_content, height=800, scrolling=True)
    
    if st.button("Close Preview", key=f"close_preview_{row['aispot_id']}"):
        st.session_state.viewing_html = None
        st.rerun()

def main():
    """Main application logic"""
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'editing_row' not in st.session_state:
        st.session_state.editing_row = None
    if 'viewing_html' not in st.session_state:
        st.session_state.viewing_html = None
    
    # Setup authentication
    authenticator = setup_authentication()
    
    # Login
    name, authentication_status, username = authenticator.login('Login to AI Spot Admin', 'main')
    
    if authentication_status == False:
        st.error('❌ Username/Password is incorrect')
        return
    
    if authentication_status == None:
        st.warning('⚠️ Please enter your username and password')
        st.info("**Demo Credentials:**\n\nUsername: `admin`\n\nPassword: `arijitwith`")
        return
    
    # Authenticated - Show dashboard
    if authentication_status:
        # Sidebar
        st.sidebar.title("🤖 AI Spot Admin")
        st.sidebar.write(f"Welcome, **{name}**!")
        
        authenticator.logout('Logout', 'sidebar')
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Filters")
        
        # Load data
        with st.spinner("Loading AI Spots..."):
            df = load_aispot_data()
        
        if df is None or df.empty:
            st.error("❌ Failed to load data from Supabase. Please check your connection.")
            return
        
        # Prepare data for display
        df['aispot_id_short'] = df['aispot_id'].str[:8]
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Sidebar filters
        search_query = st.sidebar.text_input("🔎 Search", placeholder="Name, city, state...")
        
        type_options = ["All"] + sorted(df['type_of_place'].dropna().unique().tolist())
        type_filter = st.sidebar.selectbox("📍 Type of Place", type_options)
        
        approval_options = ["All", "Approved", "Pending"]
        approval_filter = st.sidebar.selectbox("✅ Approval Status", approval_options)
        
        state_options = ["All"] + sorted(df['state'].dropna().unique().tolist())
        state_filter = st.sidebar.selectbox("🗺️ State", state_options)
        
        sort_option = st.sidebar.selectbox("🔃 Sort By", ["Date (Newest)", "Date (Oldest)", "Name (A-Z)", "Name (Z-A)"])
        
        if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # Main area
        st.title("🤖 AI Spot Admin Dashboard")
        
        # Display stats
        display_stats(df)
        
        st.markdown("---")
        
        # Apply filters
        filtered_df = apply_filters(df, search_query, type_filter, approval_filter, state_filter)
        
        # Apply sorting
        if sort_option == "Date (Newest)":
            filtered_df = filtered_df.sort_values('created_at', ascending=False)
        elif sort_option == "Date (Oldest)":
            filtered_df = filtered_df.sort_values('created_at', ascending=True)
        elif sort_option == "Name (A-Z)":
            filtered_df = filtered_df.sort_values('name', ascending=True)
        elif sort_option == "Name (Z-A)":
            filtered_df = filtered_df.sort_values('name', ascending=False)
        
        # Show filter info
        active_filters = []
        if search_query:
            active_filters.append(f"Search: '{search_query}'")
        if type_filter != "All":
            active_filters.append(f"Type: {type_filter}")
        if approval_filter != "All":
            active_filters.append(f"Status: {approval_filter}")
        if state_filter != "All":
            active_filters.append(f"State: {state_filter}")
        
        if active_filters:
            st.info(f"**Active Filters:** {' | '.join(active_filters)} | **Results:** {len(filtered_df)} of {len(df)} records")
        else:
            st.info(f"**Showing all records:** {len(filtered_df)} AI Spots")
        
        # Check if editing or viewing HTML
        if st.session_state.editing_row:
            row_data = get_aispot_by_id(st.session_state.editing_row)
            if row_data:
                display_edit_form(row_data)
            return
        
        if st.session_state.viewing_html:
            row_data = get_aispot_by_id(st.session_state.viewing_html)
            if row_data:
                display_html_preview(row_data)
            return
        
        # Display table with action buttons
        st.markdown("### 📊 AI Spots Table")
        
        if filtered_df.empty:
            st.warning("No records match your filters.")
            return
        
        # Display each row with action buttons
        for idx, row in filtered_df.iterrows():
            # Row styling based on approval status
            row_style = "approved-row" if row['is_approved'] else "pending-row"
            
            with st.container():
                # Row header
                col_info, col_status = st.columns([4, 1])
                
                with col_info:
                    st.markdown(f"**{row['name']}** ({row['type_of_place']})")
                    st.caption(f"ID: {row['aispot_id_short']} | Manager: {row['owner_manager_name']} | Email: {row['email']} | Created: {row['created_at']}")
                
                with col_status:
                    if row['is_approved']:
                        st.success("✅ Approved")
                    else:
                        st.warning("⏳ Pending")
                
                # Action buttons
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    if not row['is_approved']:
                        if st.button("✅ Approve", key=f"approve_{row['aispot_id']}", use_container_width=True):
                            with st.spinner("Approving..."):
                                success = update_approval_status(row['aispot_id'], True)
                                if success:
                                    st.success("✅ Approved successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to approve")
                    else:
                        st.button("✅ Approved", key=f"approved_{row['aispot_id']}", disabled=True, use_container_width=True)
                
                with col2:
                    if row['is_approved']:
                        if st.button("❌ Disapprove", key=f"disapprove_{row['aispot_id']}", use_container_width=True):
                            with st.spinner("Disapproving..."):
                                success = update_approval_status(row['aispot_id'], False)
                                if success:
                                    st.warning("⚠️ Disapproved successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to disapprove")
                    else:
                        st.button("❌ Pending", key=f"pending_{row['aispot_id']}", disabled=True, use_container_width=True)
                
                with col3:
                    if st.button("✏️ Edit", key=f"edit_{row['aispot_id']}", use_container_width=True):
                        st.session_state.editing_row = row['aispot_id']
                        st.rerun()
                
                with col4:
                    if st.button("👁️ View HTML", key=f"view_html_{row['aispot_id']}", use_container_width=True):
                        st.session_state.viewing_html = row['aispot_id']
                        st.rerun()
                
                with col5:
                    # Generate PDF and provide download
                    if st.button("📄 Download PDF", key=f"pdf_{row['aispot_id']}", use_container_width=True):
                        with st.spinner("Generating PDF..."):
                            pdf_bytes = generate_standee_pdf(row)
                            if pdf_bytes:
                                st.download_button(
                                    label="⬇️ Download PDF",
                                    data=pdf_bytes,
                                    file_name=f"standee_{row['name'].replace(' ', '_')}_{row['aispot_id'][:8]}.pdf",
                                    mime="application/pdf",
                                    key=f"download_{row['aispot_id']}",
                                    use_container_width=True
                                )
                            else:
                                st.error("❌ Failed to generate PDF")
                
                with col6:
                    if st.button("📧 Send Email", key=f"email_{row['aispot_id']}", use_container_width=True):
                        with st.spinner("Sending email..."):
                            success = send_standee_email(row)
                            if success:
                                st.success("✅ Email sent successfully!")
                            else:
                                st.error("❌ Failed to send email")
                
                st.markdown("---")

if __name__ == "__main__":
    main()
