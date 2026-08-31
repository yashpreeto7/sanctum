"""
Master Technical Interview Encyclopedia & Engineering Manual (40-50+ Pages)
Generates:
1. Yashpreet_Master_Interview_Preparation_Guide.pdf (Full 40-50+ Page ReportLab PDF)
2. INTERVIEW_PREPARATION_MASTER_GUIDE.md (Exhaustive Markdown Manual)
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Palette Definition
COLOR_PRIMARY = colors.HexColor("#0f172a")    # Slate 900
COLOR_SECONDARY = colors.HexColor("#1e293b")  # Slate 800
COLOR_ACCENT = colors.HexColor("#0284c7")     # Sky 600
COLOR_BRAND = colors.HexColor("#d97706")      # Amber 600
COLOR_PURPLE = colors.HexColor("#7c3aed")     # Violet 600
COLOR_EMERALD = colors.HexColor("#059669")    # Emerald 600
COLOR_ROSE = colors.HexColor("#e11d48")       # Rose 600
COLOR_BG_LIGHT = colors.HexColor("#f8fafc")   # Slate 50
COLOR_CARD_BG = colors.HexColor("#f1f5f9")    # Slate 100
COLOR_TEXT = colors.HexColor("#334155")       # Slate 700
COLOR_MUTED = colors.HexColor("#64748b")      # Slate 500
COLOR_BORDER = colors.HexColor("#cbd5e1")     # Slate 300

class NumberedCanvas(canvas.Canvas):
    """Adds running headers and 'Page X of Y' dynamic footers across all pages."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_MUTED)

        # Header on pages > 1
        if self._pageNumber > 1:
            self.drawString(40, 752, "Yashpreet — Technical Interview Master Dossier & Engineering Manual")
            self.drawRightString(612 - 40, 752, "SovereignOS • MERN • Core CS • AI Systems")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(40, 744, 612 - 40, 744)

        # Footer on all pages
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(40, 42, 612 - 40, 42)
        
        self.drawString(40, 30, "Confidential • Prepared for Technical Interview • VIT Bhopal CSE (2026)")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 40, 30, page_str)
        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=COLOR_PRIMARY,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=COLOR_ACCENT,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=COLOR_BRAND,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=COLOR_TEXT,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    qa_q_style = ParagraphStyle(
        'QA_Question',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        textColor=COLOR_PRIMARY,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    qa_a_style = ParagraphStyle(
        'QA_Answer',
        parent=body_style,
        fontSize=8.8,
        leading=13,
        textColor=COLOR_TEXT,
        leftIndent=8,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13.5,
        textColor=COLOR_PRIMARY
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=COLOR_PRIMARY,
        backColor=COLOR_CARD_BG,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'h1': h1_style,
        'h2': h2_style,
        'h3': h3_style,
        'body': body_style,
        'body_bold': body_bold,
        'qa_q': qa_q_style,
        'qa_a': qa_a_style,
        'callout': callout_style,
        'code': code_style
    }

print("Loaded generator module successfully.")
