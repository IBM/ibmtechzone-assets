from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# Create a PDF file
pdf_file = "output_PDF.pdf"
pdf = SimpleDocTemplate(pdf_file, pagesize=A4)

# Get styles for the Paragraphs
# Change fontsize as per your requirements.

styles = getSampleStyleSheet()
style_normal = styles['Normal']
style_normal.fontSize = 10
style_normal.leading = 12
style_normal.alignment = TA_LEFT

style_title = styles['Title']
style_title.fontSize = 14
style_title.leading = 16
style_title.alignment = TA_CENTER

style_header = styles['Heading1']
style_header.fontSize = 12
style_header.alignment = TA_CENTER

# Add text above the table
title = Paragraph("Title of the PDF", style_title)
description = Paragraph("Any description or text you want to add after title. Like I'm going to create a table with a merged cell", style_normal)

# Table data with merged cells
data = [
    # Header row
    [Paragraph('Column1', style_header), '',
     Paragraph('Column2', style_header)],

    # First row, spans vertically for first section
    [Paragraph('Merged cell', style_normal), Paragraph('Text',style_normal),''],

    # Second row, merged vertically for second part of first column
    [Paragraph('', style_normal), Paragraph('Text2',style_normal),'']
    
]

# CAdjust the width of your table columns.
table = Table(data, colWidths=[ 5 * cm, 5 * cm])

# Style the table (no background colors, just grid and padding)
table.setStyle(TableStyle([
     ('SPAN', (0, 0), (1, 0)), # span for header row
    ('SPAN', (0, 1), (0, 2)), 
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), # 'Helvetica-Bold' to make the text in bold characters.
    ('FONTSIZE', (0, 0), (-1, 0), 12),  # Header font size
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('GRID', (0, 0), (-1, -1), 1, colors.blue),  # Grid for the table
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Align recruiter and AI columns centrally
]))

text1 = 'Here is a short intro of WatsonX.'

other_text = Paragraph(f'{text1}<br></br>IBM WatsonX is a comprehensive AI and data platform designed to help businesses scale and accelerate their use of artificial intelligence. <font color=green>It offers a suite of tools and services for building, training, and deploying AI models, enabling companies to harness the power of both traditional machine learning and next-generation generative AI technologies.</font> WatsonX includes features for data management, model development, and AI governance, ensuring that AI solutions are trustworthy, transparent, and compliant. <br></br>By integrating AI with business workflows, WatsonX empowers organizations to drive innovation and efficiency at scale.',style_normal)

# Add elements (text and table) to the PDF
elements = [title, Spacer(1, 12), description, Spacer(1, 12), table, Spacer(1, 12), other_text]

# Build the PDF
pdf.build(elements)

print(f"Table PDF created: {pdf_file}")
