"""
PDF Generator utility module
Generates table standee PDFs using WeasyPrint to preserve HTML design
Creates 2x2 layout (4 standees per A4 page)
"""

import os
from io import BytesIO
from typing import Optional, Dict
import streamlit as st
from weasyprint import HTML, CSS

def generate_standee_pdf(row_data: Dict) -> Optional[bytes]:
    """
    Generate PDF with 2x2 layout (4 identical standees on A4) preserving HTML design
    
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
        
        # Remove download section for PDF
        html_content = html_content.replace('<div class="download-section">', '<div class="download-section" style="display: none;">')
        
        # Create 2x2 grid
        grid_html = create_2x2_grid_html(html_content)
        
        # Generate PDF using WeasyPrint
        html_obj = HTML(string=grid_html)
        pdf_bytes = html_obj.write_pdf()
        
        return pdf_bytes
    
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
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
    page_end = standee_html.rfind('</div>', 0, standee_html.find('<div class="download-section">'))
    
    if page_start == -1:
        # Fallback: just use the body
        page_content = standee_html
    else:
        # Get everything from page div to its closing tag
        page_end = standee_html.find('</div><!--container-->', page_start)
        if page_end == -1:
            page_end = standee_html.find('</div>', page_start + 100)  # Find next closing div
        page_end += len('</div>')
        if '<!--container-->' in standee_html[page_end:page_end+20]:
            page_end += len('<!--container-->') + 6  # Include closing page div
        
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
        
        .grid-wrapper {{
            width: 100%;
            height: 100%;
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
            position: relative;
        }}
        
        .grid-item .page {{
            width: 3.8in !important;
            height: 5.7in !important;
            margin: 0;
            transform: scale(0.95);
            transform-origin: center center;
        }}
        
        /* Cutting guides */
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
        
        /* Print optimization */
        @media print {{
            html, body {{
                width: 100%;
                height: 100%;
            }}
            .grid-container {{
                page-break-inside: avoid;
            }}
            .grid-item {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <!-- Cutting guides -->
    <div class="cutting-guide horizontal h1"></div>
    <div class="cutting-guide vertical v1"></div>
    
    <div class="grid-wrapper">
        <div class="grid-container">
            <div class="grid-item">{page_content}</div>
            <div class="grid-item">{page_content}</div>
            <div class="grid-item">{page_content}</div>
            <div class="grid-item">{page_content}</div>
        </div>
    </div>
</body>
</html>"""
    
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
