"""
PDF Generator utility module
Generates table standee PDFs with 2x2 layout using WeasyPrint
"""

import os
from io import BytesIO
from typing import Optional, Dict
from weasyprint import HTML, CSS
from jinja2 import Template
import streamlit as st

def generate_standee_pdf(row_data: Dict) -> Optional[bytes]:
    """
    Generate PDF with 2x2 layout (4 identical standees on A4)
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        bytes: PDF file as bytes or None if failed
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
        
        # Remove the download section for PDF generation
        html_content = html_content.replace('<div class="download-section">', '<div class="download-section" style="display: none;">')
        
        # Create 2x2 grid wrapper
        grid_html = create_2x2_grid(html_content)
        
        # Generate PDF using WeasyPrint
        pdf_bytes = HTML(string=grid_html).write_pdf()
        
        return pdf_bytes
    
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

def create_2x2_grid(standee_html: str) -> str:
    """
    Create 2x2 grid layout with 4 identical standees on A4
    
    Args:
        standee_html: HTML content of single standee
    
    Returns:
        str: HTML with 2x2 grid layout
    """
    
    # Extract the standee page content (without html/body tags)
    # We need to extract just the .page div
    start_idx = standee_html.find('<div class="page"')
    end_idx = standee_html.find('</div>', standee_html.find('</div>', standee_html.find('</div>', start_idx) + 1) + 1) + 6
    
    if start_idx == -1 or end_idx == -1:
        # Fallback: use entire body content
        standee_content = standee_html
    else:
        standee_content = standee_html[start_idx:end_idx]
    
    # Extract styles from original HTML
    style_start = standee_html.find('<style>')
    style_end = standee_html.find('</style>') + 8
    original_styles = standee_html[style_start:style_end] if style_start != -1 else ""
    
    # Create 2x2 grid HTML
    grid_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Spot Standee - 2x2 Grid</title>
    {original_styles}
    <style>
        /* Override page settings for A4 grid */
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
            height: 100%;
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
            transform: scale(0.95);
            transform-origin: center center;
            box-sizing: border-box;
        }}
        
        /* Print optimization */
        @media print {{
            .grid-container {{
                page-break-inside: avoid;
            }}
            
            .grid-item {{
                page-break-inside: avoid;
            }}
        }}
        
        /* Cutting guides */
        .cutting-guide {{
            position: fixed;
            background: none;
            z-index: 1000;
        }}
        
        .cutting-guide.horizontal {{
            height: 1px;
            width: 100%;
            left: 0;
            border-top: 1px dashed #cccccc;
        }}
        
        .cutting-guide.vertical {{
            width: 1px;
            height: 100%;
            top: 0;
            border-left: 1px dashed #cccccc;
        }}
        
        .cutting-guide.h1 {{ top: 50%; }}
        .cutting-guide.v1 {{ left: 50%; }}
    </style>
</head>
<body>
    <!-- Cutting guides -->
    <div class="cutting-guide horizontal h1"></div>
    <div class="cutting-guide vertical v1"></div>
    
    <div class="grid-container">
        <div class="grid-item">
            {standee_content}
        </div>
        <div class="grid-item">
            {standee_content}
        </div>
        <div class="grid-item">
            {standee_content}
        </div>
        <div class="grid-item">
            {standee_content}
        </div>
    </div>
</body>
</html>
"""
    
    return grid_html

def generate_preview_html(row_data: Dict) -> str:
    """
    Generate HTML preview (single standee) for display in Streamlit
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        str: HTML content for preview
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
        
        return html_content
    
    except Exception as e:
        st.error(f"Error generating HTML preview: {str(e)}")
        return ""

def test_pdf_generation():
    """
    Test PDF generation with sample data
    """
    sample_data = {
        'name': 'Tech Hub Cafe',
        'type_of_place': 'Cafe & Co-working Space',
        'owner_manager_name': 'John Smith',
        'aispot_id': '12345678-1234-1234-1234-123456789012',
        'qr_code_link': 'https://aiwithArijit.com/ai-spot/test'
    }
    
    pdf_bytes = generate_standee_pdf(sample_data)
    
    if pdf_bytes:
        print("✅ PDF generated successfully!")
        print(f"PDF size: {len(pdf_bytes)} bytes")
        
        # Save test PDF
        with open('test_standee.pdf', 'wb') as f:
            f.write(pdf_bytes)
        print("💾 Test PDF saved as 'test_standee.pdf'")
        
        return True
    else:
        print("❌ PDF generation failed")
        return False

if __name__ == "__main__":
    # Run test when module is executed directly
    print("Testing PDF generation...")
    test_pdf_generation()
