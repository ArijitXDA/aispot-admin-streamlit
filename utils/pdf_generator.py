"""
PDF Generator utility module
Generates table standee PDFs with 2x2 layout using ReportLab
Optimized for Streamlit Cloud deployment
"""

import os
from io import BytesIO
from typing import Optional, Dict
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode

def generate_standee_pdf(row_data: Dict) -> Optional[bytes]:
    """
    Generate PDF with 2x2 layout (4 identical standees on A4)
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        bytes: PDF file as bytes or None if failed
    """
    try:
        # Create BytesIO buffer
        buffer = BytesIO()
        
        # Create PDF canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Standee dimensions (3.8" x 5.7")
        standee_width = 3.8 * inch
        standee_height = 5.7 * inch
        
        # Calculate positions for 2x2 grid with margins
        margin_x = 0.35 * inch
        margin_y = 0.3 * inch
        gap = 0.2 * inch
        
        positions = [
            (margin_x, height - margin_y - standee_height),  # Top-left
            (margin_x + standee_width + gap, height - margin_y - standee_height),  # Top-right
            (margin_x, height - margin_y - 2*standee_height - gap),  # Bottom-left
            (margin_x + standee_width + gap, height - margin_y - 2*standee_height - gap)  # Bottom-right
        ]
        
        # Draw cutting guides (dashed lines)
        c.setDash(3, 3)
        c.setStrokeColor(HexColor('#cccccc'))
        c.setLineWidth(0.5)
        
        # Horizontal cutting guide
        mid_y = height / 2
        c.line(0, mid_y, width, mid_y)
        
        # Vertical cutting guide
        mid_x = width / 2
        c.line(mid_x, 0, mid_x, height)
        
        # Reset dash for standees
        c.setDash()
        
        # Draw 4 identical standees
        for x, y in positions:
            draw_standee(c, x, y, standee_width, standee_height, row_data)
        
        # Save PDF
        c.save()
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None

def draw_standee(c, x, y, width, height, data: Dict):
    """
    Draw a single standee at specified position
    
    Args:
        c: ReportLab canvas
        x, y: Position coordinates
        width, height: Standee dimensions
        data: AI Spot data dictionary
    """
    
    # Draw border
    c.setStrokeColor(HexColor('#0055aa'))
    c.setLineWidth(2)
    c.rect(x, y, width, height)
    
    # Header background
    header_height = 0.8 * inch
    c.setFillColor(HexColor('#0055aa'))
    c.rect(x, y + height - header_height, width, header_height, fill=1, stroke=0)
    
    # Header text - AI Spot Name
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 16)
    name = data.get('name', '')[:30]  # Limit to 30 chars
    text_width = c.stringWidth(name, "Helvetica-Bold", 16)
    c.drawString(x + (width - text_width) / 2, y + height - 0.5 * inch, name)
    
    # Type of place
    c.setFont("Helvetica", 10)
    type_place = data.get('type_of_place', '')
    text_width = c.stringWidth(type_place, "Helvetica", 10)
    c.drawString(x + (width - text_width) / 2, y + height - 0.7 * inch, type_place)
    
    # Body section
    current_y = y + height - 1.2 * inch
    
    # Generate QR code
    try:
        qr_link = data.get('qr_code_link', 'https://aiwithArijit.com')
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(qr_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to buffer
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Draw QR code (centered)
        qr_size = 1.5 * inch
        qr_x = x + (width - qr_size) / 2
        qr_y = current_y - qr_size - 0.2 * inch
        c.drawImage(ImageReader(qr_buffer), qr_x, qr_y, qr_size, qr_size)
        
        current_y = qr_y - 0.3 * inch
        
    except Exception as e:
        # If QR generation fails, just skip it
        current_y -= 0.3 * inch
    
    # Manager name
    c.setFillColor(HexColor('#333333'))
    c.setFont("Helvetica-Bold", 11)
    manager_label = "Manager:"
    c.drawString(x + 0.2 * inch, current_y, manager_label)
    
    c.setFont("Helvetica", 11)
    manager_name = data.get('owner_manager_name', '')[:25]
    c.drawString(x + 0.2 * inch, current_y - 0.2 * inch, manager_name)
    
    current_y -= 0.6 * inch
    
    # AI Spot ID
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor('#666666'))
    aispot_id = data.get('aispot_id', '')[:8]
    id_text = f"ID: {aispot_id}"
    text_width = c.stringWidth(id_text, "Helvetica", 9)
    c.drawString(x + (width - text_width) / 2, current_y, id_text)
    
    # Footer
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(HexColor('#0055aa'))
    footer_text = "Scan QR to Learn More"
    text_width = c.stringWidth(footer_text, "Helvetica-Bold", 10)
    c.drawString(x + (width - text_width) / 2, y + 0.3 * inch, footer_text)
    
    # Branding
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor('#999999'))
    brand_text = "AI with Arijit"
    text_width = c.stringWidth(brand_text, "Helvetica", 8)
    c.drawString(x + (width - text_width) / 2, y + 0.15 * inch, brand_text)

def generate_preview_html(row_data: Dict) -> str:
    """
    Generate HTML preview for display in Streamlit
    Note: This returns a simple HTML representation
    
    Args:
        row_data: Dictionary containing AI Spot data
    
    Returns:
        str: HTML content for preview
    """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .standee-preview {{
                width: 380px;
                height: 570px;
                border: 2px solid #0055aa;
                margin: 20px auto;
                font-family: Arial, sans-serif;
                background: white;
            }}
            .header {{
                background: #0055aa;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .header h2 {{
                margin: 0;
                font-size: 18px;
            }}
            .header p {{
                margin: 5px 0 0 0;
                font-size: 12px;
            }}
            .body {{
                padding: 20px;
                text-align: center;
            }}
            .qr-placeholder {{
                width: 150px;
                height: 150px;
                margin: 20px auto;
                background: #f0f0f0;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px dashed #999;
            }}
            .manager {{
                margin: 20px 0;
                text-align: left;
            }}
            .manager strong {{
                color: #333;
            }}
            .id {{
                color: #666;
                font-size: 11px;
                margin: 15px 0;
            }}
            .footer {{
                position: absolute;
                bottom: 20px;
                width: 100%;
                text-align: center;
            }}
            .footer strong {{
                color: #0055aa;
            }}
            .footer small {{
                color: #999;
                display: block;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="standee-preview">
            <div class="header">
                <h2>{row_data.get('name', '')}</h2>
                <p>{row_data.get('type_of_place', '')}</p>
            </div>
            <div class="body">
                <div class="qr-placeholder">
                    QR Code<br>Here
                </div>
                <div class="manager">
                    <strong>Manager:</strong><br>
                    {row_data.get('owner_manager_name', '')}
                </div>
                <div class="id">
                    ID: {row_data.get('aispot_id', '')[:8]}
                </div>
            </div>
            <div class="footer">
                <strong>Scan QR to Learn More</strong>
                <small>AI with Arijit</small>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

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
