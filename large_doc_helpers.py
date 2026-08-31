"""
Complete 40-50+ Page Engineering Textbook & Technical Interview Encyclopedia Generator.
Compiles:
- Yashpreet_Master_Interview_Preparation_Guide.pdf
- INTERVIEW_PREPARATION_MASTER_GUIDE.md
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from pdf_setup import get_styles, NumberedCanvas, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_BRAND, COLOR_PURPLE, COLOR_EMERALD, COLOR_BG_LIGHT, COLOR_CARD_BG, COLOR_BORDER

def create_section_header(title, subtitle, styles):
    story = []
    story.append(Paragraph(title, styles['h1']))
    if subtitle:
        story.append(Paragraph(subtitle, styles['callout']))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_ACCENT, spaceBefore=2, spaceAfter=8))
    return story

def make_qa(q_text, a_text, styles):
    return [
        Paragraph(f"<b>{q_text}</b>", styles['qa_q']),
        Paragraph(a_text, styles['qa_a'])
    ]

def make_table(headers, rows, col_widths, styles):
    table_data = [[Paragraph(f"<b>{h}</b>", styles['body_bold']) for h in headers]]
    for row in rows:
        formatted_row = []
        for cell in row:
            if isinstance(cell, str):
                formatted_row.append(Paragraph(cell, styles['body']))
            else:
                formatted_row.append(cell)
        table_data.append(formatted_row)
    
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [COLOR_BG_LIGHT, COLOR_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t

print("Helper functions defined successfully.")
