"""
Database utility module for Supabase operations
Handles all CRUD operations for AI Spot data
Updated for Streamlit Cloud deployment
"""

import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, List
import os
from datetime import datetime

def get_config():
    """Get configuration from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        if hasattr(st, 'secrets') and 'secrets' in st.secrets:
            return {
                'url': st.secrets['secrets']['SUPABASE_URL'],
                'key': st.secrets['secrets']['SUPABASE_KEY']
            }
        elif hasattr(st, 'secrets') and 'SUPABASE_URL' in st.secrets:
            return {
                'url': st.secrets['SUPABASE_URL'],
                'key': st.secrets['SUPABASE_KEY']
            }
    except:
        pass
    
    # Fallback to environment variables (for local development)
    return {
        'url': os.getenv("SUPABASE_URL", "https://enszifyeqnwcnxaqrmrq.supabase.co"),
        'key': os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVuc3ppZnllcW53Y254YXFybXJxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQxMTIyNTcsImV4cCI6MjA2OTY4ODI1N30.eCMgm8ayfG2RNkOSk8iOBEfZMl64gY7a8dLs1W3m79o")
    }

@st.cache_resource
def get_supabase_client() -> Client:
    """
    Get Supabase client (cached)
    """
    try:
        config = get_config()
        client = create_client(config['url'], config['key'])
        return client
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_aispot_data() -> Optional[object]:
    """
    Load all AI Spot data from Supabase
    Returns: pandas DataFrame or None
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        # Fetch all records from aispot_master table
        response = client.table('aispot_master').select('*').order('created_at', desc=True).execute()
        
        if response.data:
            import pandas as pd
            df = pd.DataFrame(response.data)
            return df
        else:
            return None
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def update_approval_status(aispot_id: str, is_approved: bool) -> bool:
    """
    Update approval status for an AI Spot
    
    Args:
        aispot_id: UUID of the AI Spot
        is_approved: Boolean approval status
    
    Returns:
        bool: Success status
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        # Update record
        response = client.table('aispot_master').update({
            'is_approved': is_approved,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('aispot_id', aispot_id).execute()
        
        # Clear cache to refresh data
        st.cache_data.clear()
        
        return True
    
    except Exception as e:
        st.error(f"Error updating approval status: {str(e)}")
        return False

def update_aispot_record(aispot_id: str, data: Dict) -> bool:
    """
    Update AI Spot record with new data
    
    Args:
        aispot_id: UUID of the AI Spot
        data: Dictionary with fields to update
    
    Returns:
        bool: Success status
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        # Add updated_at timestamp
        data['updated_at'] = datetime.utcnow().isoformat()
        
        # Update record
        response = client.table('aispot_master').update(data).eq('aispot_id', aispot_id).execute()
        
        # Clear cache to refresh data
        st.cache_data.clear()
        
        return True
    
    except Exception as e:
        st.error(f"Error updating record: {str(e)}")
        return False

def get_aispot_by_id(aispot_id: str) -> Optional[Dict]:
    """
    Get a specific AI Spot by ID
    
    Args:
        aispot_id: UUID of the AI Spot
    
    Returns:
        dict: AI Spot data or None
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        response = client.table('aispot_master').select('*').eq('aispot_id', aispot_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        else:
            return None
    
    except Exception as e:
        st.error(f"Error fetching record: {str(e)}")
        return None

def delete_aispot(aispot_id: str) -> bool:
    """
    Delete an AI Spot record (use with caution)
    
    Args:
        aispot_id: UUID of the AI Spot
    
    Returns:
        bool: Success status
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        response = client.table('aispot_master').delete().eq('aispot_id', aispot_id).execute()
        
        # Clear cache to refresh data
        st.cache_data.clear()
        
        return True
    
    except Exception as e:
        st.error(f"Error deleting record: {str(e)}")
        return False

def get_statistics() -> Dict:
    """
    Get statistics about AI Spots
    
    Returns:
        dict: Statistics data
    """
    try:
        client = get_supabase_client()
        if not client:
            return {
                'total': 0,
                'approved': 0,
                'pending': 0
            }
        
        # Get all records
        response = client.table('aispot_master').select('is_approved').execute()
        
        if response.data:
            total = len(response.data)
            approved = sum(1 for item in response.data if item.get('is_approved', False))
            pending = total - approved
            
            return {
                'total': total,
                'approved': approved,
                'pending': pending
            }
        else:
            return {
                'total': 0,
                'approved': 0,
                'pending': 0
            }
    
    except Exception as e:
        st.error(f"Error getting statistics: {str(e)}")
        return {
            'total': 0,
            'approved': 0,
            'pending': 0
        }
