"""
Utility modules for AI Spot Admin Dashboard
"""

from .database import (
    get_supabase_client,
    load_aispot_data,
    update_approval_status,
    update_aispot_record,
    get_aispot_by_id,
    get_statistics
)

from .pdf_generator import (
    generate_standee_pdf,
    generate_preview_html
)

from .email_sender import (
    send_standee_email,
    test_email_configuration
)

__all__ = [
    'get_supabase_client',
    'load_aispot_data',
    'update_approval_status',
    'update_aispot_record',
    'get_aispot_by_id',
    'get_statistics',
    'generate_standee_pdf',
    'generate_preview_html',
    'send_standee_email',
    'test_email_configuration'
]
