"""
PDF Generator utility module
Generates table standee PDFs using CloudConvert API
Creates 2x2 layout (4 standees per A4 page)
"""

import os
import requests
import time
from typing import Optional, Dict
import streamlit as st

# CloudConvert API configuration
CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY", "")

def generate_standee_pdf(row_data: Dict) -> Optional[bytes]:
    """
    Generate PDF with 2x2 layout using CloudConvert API
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        bytes: PDF file as bytes or None if failed
    """
    try:
        # Check if API key is configured
        if not CLOUDCONVERT_API_KEY:
            st.warning("⚠️ CloudConvert API key not configured. Downloading HTML file instead.")
            return generate_standee_html_fallback(row_data)
        
        # Load the standee template
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'tablestandee.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        # Replace placeholders with actual data
        html_content = html_template.replace('{{name}}', row_data.get('name', ''))
        html_content = html_content.replace('{{type_of_place}}', row_data.get('type_of_place', ''))
        html_content = html_content.replace('{{manager_name}}', row_data.get('owner_manager_name', ''))
        html_content = html_content.replace('{{aispot_id}}', row_data.get('aispot_id', '')[:8])
        html_content = html_content.replace('{{qr_code_link}}', row_data.get('qr_code_link', ''))
        
        # Remove download section for PDF
        html_content = html_content.replace('<div class="download-section">', '<div class="download-section" style="display: none;">')
        
        # Create 2x2 grid
        grid_html = create_2x2_grid_html(html_content)
        
        # Convert HTML to PDF using CloudConvert API
        pdf_bytes = convert_html_to_pdf_cloudconvert(grid_html, row_data.get('name', 'standee'))
        
        if pdf_bytes:
            return pdf_bytes
        else:
            st.warning("CloudConvert conversion failed. Downloading HTML file instead.")
            return generate_standee_html_fallback(row_data)
    
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return generate_standee_html_fallback(row_data)

def convert_html_to_pdf_cloudconvert(html_content: str, filename_prefix: str = "standee") -> Optional[bytes]:
    """
    Convert HTML to PDF using CloudConvert API
    
    Args:
        html_content: HTML string
        filename_prefix: Prefix for the filename
    
    Returns:
        bytes: PDF content or None if failed
    """
    try:
        headers = {
            "Authorization": f"Bearer {CLOUDCONVERT_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Step 1: Create a job with filename specified
        job_data = {
            "tasks": {
                "import-html": {
                    "operation": "import/raw",
                    "filename": "standee.html"
                },
                "convert-to-pdf": {
                    "operation": "convert",
                    "input": "import-html",
                    "output_format": "pdf",
                    "engine": "chrome",
                    "page_width": 210,
                    "page_height": 297,
                    "margin_top": 8,
                    "margin_right": 9,
                    "margin_bottom": 8,
                    "margin_left": 9,
                    "print_background": True,
                    "display_header_footer": False
                },
                "export-pdf": {
                    "operation": "export/url",
                    "input": "convert-to-pdf"
                }
            }
        }
        
        # Create job
        response = requests.post(
            "https://api.cloudconvert.com/v2/jobs",
            headers=headers,
            json=job_data,
            timeout=30
        )
        
        if response.status_code != 201:
            error_msg = response.json() if response.text else response.text
            st.error(f"CloudConvert job creation failed: {error_msg}")
            return None
        
        job_response = response.json()
        job_id = job_response['data']['id']
        
        # Step 2: Upload HTML content
        import_task = next(task for task in job_response['data']['tasks'] if task['name'] == 'import-html')
        upload_url = import_task['result']['form']['url']
        upload_params = import_task['result']['form']['parameters']
        
        # Add filename to upload params if not present
        if 'filename' not in upload_params:
            upload_params['filename'] = 'standee.html'
        
        # Upload HTML as file
        files = {'file': ('standee.html', html_content.encode('utf-8'), 'text/html')}
        upload_response = requests.post(upload_url, data=upload_params, files=files, timeout=60)
        
        if upload_response.status_code not in [200, 201]:
            st.error(f"HTML upload failed: {upload_response.text}")
            return None
        
        # Step 3: Wait for job completion
        max_wait = 60  # 60 seconds timeout
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Check job status
            status_response = requests.get(
                f"https://api.cloudconvert.com/v2/jobs/{job_id}",
                headers=headers,
                timeout=10
            )
            
            if status_response.status_code != 200:
                st.error(f"Job status check failed: {status_response.text}")
                return None
            
            job_status = status_response.json()
            status = job_status['data']['status']
            
            if status == 'finished':
                # Get download URL
                export_task = next(task for task in job_status['data']['tasks'] if task['name'] == 'export-pdf')
                download_url = export_task['result']['files'][0]['url']
                
                # Download PDF
                pdf_response = requests.get(download_url, timeout=30)
                if pdf_response.status_code == 200:
                    return pdf_response.content
                else:
                    st.error(f"PDF download failed: {pdf_response.text}")
                    return None
            
            elif status == 'error':
                error_details = job_status.get('data', {}).get('tasks', [])
                st.error(f"CloudConvert job failed: {error_details}")
                return None
            
            # Wait before checking again
            time.sleep(2)
        
        st.error("CloudConvert job timeout")
        return None
    
    except Exception as e:
        st.error(f"CloudConvert API error: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None

def generate_standee_html_fallback(row_data: Dict) -> bytes:
    """
    Fallback: Generate HTML file when CloudConvert is not available
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        bytes: HTML file as bytes
    """
    try:
        # Load the standee template
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'tablestandee.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        # Replace placeholders with actual data
        html_content = html_template.replace('{{name}}', row_data.get('name', ''))
        html_content = html_content.replace('{{type_of_place}}', row_data.get('type_of_place', ''))
        html_content = html_content.replace('{{manager_name}}', row_data.get('owner_manager_name', ''))
        html_content = html_content.replace('{{aispot_id}}', row_data.get('aispot_id', '')[:8])
        html_content = html_content.replace('{{qr_code_link}}', row_data.get('qr_code_link', ''))
        
        # Remove download section
        html_content = html_content.replace('<div class="download-section">', '<div class="download-section" style="display: none;">')
        
        # Create 2x2 grid
        grid_html = create_2x2_grid_html(html_content)
        
        return grid_html.encode('utf-8')
    
    except Exception as e:
        st.error(f"Error generating HTML fallback: {str(e)}")
        return None

def create_2x2_grid_html(standee_html: str) -> str:
    """
    Create 2x2 grid layout with 4 identical standees on A4
    
    Args:
        standee_html: HTML content of single standee
    
    Returns:
        str: HTML with 2x2 grid layout optimized for printing
    """
    
    # Extract the page div content
    page_start = standee_html.find('<div class="page"')
    
    if page_start == -1:
        page_content = standee_html
    else:
        # Find the end of the page div (before download section)
        download_start = standee_html.find('<div class="download-section">')
        if download_start != -1:
            page_end = standee_html.rfind('</div>', 0, download_start)
            page_end = standee_html.rfind('</div>', 0, page_end) + 6
        else:
            page_end = standee_html.rfind('</div></body>')
        
        page_content = standee_html[page_start:page_end]
    
    # Extract styles
    style_start = standee_html.find('<style>')
    style_end = standee_html.find('</style>') + 8
    original_styles = standee_html[style_start:style_end] if style_start != -1 else ""
    
    # Create 2x2 grid HTML
    grid_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Spot Standee - 2x2 Grid</title>
    {original_styles}
    <style>
        @page {{
            size: A4 portrait;
            margin: 0.3in 0.35in;
        }}
        
        body {{
            margin: 0;
            padding: 0;
            background: white;
        }}
        
        .grid-container {{
            width: 100%;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            grid-template-rows: repeat(2, 1fr);
            gap: 0.2in;
            page-break-inside: avoid;
        }}
        
        .grid-item {{
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .grid-item .page {{
            width: 3.8in !important;
            height: 5.7in !important;
            margin: 0;
            transform: scale(0.95);
            transform-origin: center center;
        }}
        
        .cutting-guide {{
            position: fixed;
            background: none;
            z-index: 1000;
            pointer-events: none;
        }}
        
        .cutting-guide.horizontal {{
            height: 0;
            width: 100%;
            left: 0;
            border-top: 1px dashed #cccccc;
        }}
        
        .cutting-guide.vertical {{
            width: 0;
            height: 100%;
            top: 0;
            border-left: 1px dashed #cccccc;
        }}
        
        .cutting-guide.h1 {{ top: 50%; }}
        .cutting-guide.v1 {{ left: 50%; }}
    </style>
</head>
<body>
    <div class="cutting-guide horizontal h1"></div>
    <div class="cutting-guide vertical v1"></div>
    
    <div class="grid-container">
        <div class="grid-item">{page_content}</div>
        <div class="grid-item">{page_content}</div>
        <div class="grid-item">{page_content}</div>
        <div class="grid-item">{page_content}</div>
    </div>
</body>
</html>"""
    
    return grid_html

def generate_preview_html(row_data: Dict) -> str:
    """
    Generate HTML preview for display in Streamlit
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        str: HTML content for preview
    """
    try:
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'tablestandee.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        html_content = html_template.replace('{{name}}', row_data.get('name', ''))
        html_content = html_content.replace('{{type_of_place}}', row_data.get('type_of_place', ''))
        html_content = html_content.replace('{{manager_name}}', row_data.get('owner_manager_name', ''))
        html_content = html_content.replace('{{aispot_id}}', row_data.get('aispot_id', '')[:8])
        html_content = html_content.replace('{{qr_code_link}}', row_data.get('qr_code_link', ''))
        
        return html_content
    
    except Exception as e:
        st.error(f"Error generating HTML preview: {str(e)}")
        return ""
