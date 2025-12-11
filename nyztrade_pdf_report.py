"""
NYZTrade Pro - Professional PDF Report Generator
================================================
A comprehensive PDF report generation module for stock valuation analysis.
Features: Cover page, executive summary, valuation analysis, charts, and financial tables.

Author: NYZTrade
Version: 1.0.0
"""

import io
import os
import math
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, HRFlowable, KeepTogether, ListFlowable, ListItem
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Wedge, Polygon
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# For chart generation
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle as MplCircle, Wedge as MplWedge
import numpy as np


# ============================================================================
# COLOR SCHEME - NYZTrade Brand Colors
# ============================================================================
class NYZColors:
    """NYZTrade brand color palette"""
    # Primary colors
    PRIMARY_PURPLE = colors.HexColor('#7c3aed')
    PRIMARY_INDIGO = colors.HexColor('#6366f1')
    PRIMARY_VIOLET = colors.HexColor('#8b5cf6')
    
    # Dark backgrounds
    DARK_BG_1 = colors.HexColor('#1a1a2e')
    DARK_BG_2 = colors.HexColor('#16213e')
    DARK_BG_3 = colors.HexColor('#0f3460')
    
    # Text colors
    WHITE = colors.HexColor('#ffffff')
    LIGHT_GRAY = colors.HexColor('#e2e8f0')
    LIGHT_PURPLE = colors.HexColor('#a78bfa')
    
    # Status colors
    SUCCESS_GREEN = colors.HexColor('#34d399')
    WARNING_YELLOW = colors.HexColor('#fbbf24')
    ERROR_RED = colors.HexColor('#f87171')
    
    # Chart colors
    CHART_BLUE = colors.HexColor('#3b82f6')
    CHART_CYAN = colors.HexColor('#06b6d4')
    CHART_EMERALD = colors.HexColor('#10b981')
    CHART_AMBER = colors.HexColor('#f59e0b')
    CHART_ROSE = colors.HexColor('#f43f5e')
    
    # Gauge zones
    GAUGE_GREEN = colors.HexColor('#22c55e')
    GAUGE_YELLOW = colors.HexColor('#eab308')
    GAUGE_ORANGE = colors.HexColor('#f97316')
    GAUGE_RED = colors.HexColor('#ef4444')


# ============================================================================
# CUSTOM STYLES
# ============================================================================
def get_nyz_styles():
    """Create custom paragraph styles for NYZTrade reports"""
    styles = getSampleStyleSheet()
    
    # Cover page title
    styles.add(ParagraphStyle(
        name='CoverTitle',
        parent=styles['Title'],
        fontSize=36,
        textColor=NYZColors.PRIMARY_PURPLE,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    ))
    
    # Cover subtitle
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=NYZColors.DARK_BG_2,
        alignment=TA_CENTER,
        spaceAfter=10,
        fontName='Helvetica'
    ))
    
    # Section headers
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=NYZColors.PRIMARY_PURPLE,
        spaceBefore=20,
        spaceAfter=12,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=NYZColors.PRIMARY_PURPLE,
        borderPadding=5
    ))
    
    # Subsection headers
    styles.add(ParagraphStyle(
        name='SubsectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=NYZColors.PRIMARY_INDIGO,
        spaceBefore=15,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))
    
    # Body text - custom NYZ style
    styles.add(ParagraphStyle(
        name='NYZBodyText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=NYZColors.DARK_BG_1,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14,
        fontName='Helvetica'
    ))
    
    # Metric label
    styles.add(ParagraphStyle(
        name='MetricLabel',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    # Metric value
    styles.add(ParagraphStyle(
        name='MetricValue',
        parent=styles['Normal'],
        fontSize=14,
        textColor=NYZColors.DARK_BG_1,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Recommendation - Strong Buy
    styles.add(ParagraphStyle(
        name='RecommendationStrongBuy',
        parent=styles['Normal'],
        fontSize=14,
        textColor=NYZColors.SUCCESS_GREEN,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Recommendation - Buy
    styles.add(ParagraphStyle(
        name='RecommendationBuy',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#22d3ee'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Recommendation - Hold
    styles.add(ParagraphStyle(
        name='RecommendationHold',
        parent=styles['Normal'],
        fontSize=14,
        textColor=NYZColors.WARNING_YELLOW,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Recommendation - Avoid
    styles.add(ParagraphStyle(
        name='RecommendationAvoid',
        parent=styles['Normal'],
        fontSize=14,
        textColor=NYZColors.ERROR_RED,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Footer text
    styles.add(ParagraphStyle(
        name='FooterText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    # Disclaimer text
    styles.add(ParagraphStyle(
        name='DisclaimerText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_JUSTIFY,
        leading=11,
        fontName='Helvetica'
    ))
    
    # Table header
    styles.add(ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        textColor=NYZColors.WHITE,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Table cell
    styles.add(ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        fontSize=9,
        textColor=NYZColors.DARK_BG_1,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    return styles


# ============================================================================
# CHART GENERATION FUNCTIONS
# ============================================================================

def create_gauge_chart(value: float, min_val: float, max_val: float, 
                       title: str, unit: str = 'x') -> str:
    """
    Create a professional gauge chart and save as image.
    Returns the path to the saved image.
    """
    fig = plt.figure(figsize=(4, 2.8))
    ax = fig.add_subplot(111, projection='polar')
    
    # Configure the gauge (semi-circle)
    ax.set_theta_offset(np.pi)
    ax.set_theta_direction(-1)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    
    # Remove radial ticks and labels
    ax.set_rticks([])
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    
    # Define color zones
    zones = [
        (0, 0.25, '#22c55e'),      # Green - Undervalued
        (0.25, 0.5, '#84cc16'),    # Light green
        (0.5, 0.75, '#eab308'),    # Yellow - Fair
        (0.75, 0.9, '#f97316'),    # Orange
        (0.9, 1.0, '#ef4444'),     # Red - Overvalued
    ]
    
    # Draw color zones using bar chart
    for start, end, color in zones:
        theta_center = (start + end) / 2 * np.pi
        theta_width = (end - start) * np.pi
        ax.bar(theta_center, 0.35, width=theta_width, bottom=0.55, color=color, alpha=0.8)
    
    # Calculate needle position
    normalized = min(max((value - min_val) / (max_val - min_val), 0), 1)
    needle_angle = normalized * np.pi
    
    # Draw needle using plot
    ax.plot([needle_angle, needle_angle], [0, 0.85], color='#1e293b', lw=3, solid_capstyle='round')
    ax.scatter([needle_angle], [0.85], color='#1e293b', s=50, zorder=5)
    
    # Center circle
    ax.scatter([0], [0], color='#7c3aed', s=200, zorder=10)
    
    # Add value text below
    fig.text(0.5, 0.15, f'{value:.1f}{unit}', ha='center', va='center',
             fontsize=16, fontweight='bold', color='#1e293b')
    
    # Add title above
    fig.text(0.5, 0.92, title, ha='center', va='center',
             fontsize=11, fontweight='bold', color='#7c3aed')
    
    # Add min/max labels
    fig.text(0.12, 0.25, f'{min_val:.0f}', ha='center', fontsize=8, color='#64748b')
    fig.text(0.88, 0.25, f'{max_val:.0f}', ha='center', fontsize=8, color='#64748b')
    
    ax.spines['polar'].set_visible(False)
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    
    # Save to file (sanitize filename)
    safe_title = title.replace(" ", "_").replace("/", "_").replace("\\", "_").lower()
    img_path = f'/tmp/gauge_{safe_title}.png'
    plt.savefig(img_path, dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none', pad_inches=0.1)
    plt.close(fig)
    
    return img_path


def create_valuation_comparison_chart(current_price: float, fair_value_pe: float,
                                      fair_value_ev: float, blended_fair_value: float) -> str:
    """Create a bar chart comparing current price vs fair values"""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    
    categories = ['Current\nPrice', 'PE Method\nFair Value', 'EV/EBITDA\nFair Value', 'Blended\nFair Value']
    values = [current_price, fair_value_pe, fair_value_ev, blended_fair_value]
    colors_list = ['#6366f1', '#22c55e', '#06b6d4', '#8b5cf6']
    
    bars = ax.bar(categories, values, color=colors_list, width=0.6, edgecolor='white', linewidth=1.5)
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'₹{val:,.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold',
                    color='#1e293b')
    
    # Add reference line for current price
    ax.axhline(y=current_price, color='#f43f5e', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.text(3.5, current_price * 1.02, 'Current Price', fontsize=8, 
            color='#f43f5e', ha='right', va='bottom')
    
    # Styling
    ax.set_ylabel('Price (₹)', fontsize=10, color='#475569')
    ax.set_title('Valuation Comparison', fontsize=12, fontweight='bold', 
                 color='#7c3aed', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e2e8f0')
    ax.spines['bottom'].set_color('#e2e8f0')
    ax.tick_params(colors='#64748b')
    ax.set_facecolor('#fafafa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    
    img_path = '/tmp/valuation_comparison.png'
    plt.savefig(img_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    return img_path


def create_52week_range_chart(low_52w: float, high_52w: float, current_price: float) -> str:
    """Create a 52-week price range visualization"""
    fig, ax = plt.subplots(figsize=(6, 1.5))
    
    # Calculate position
    range_val = high_52w - low_52w
    position = (current_price - low_52w) / range_val if range_val > 0 else 0.5
    position = max(0, min(1, position))
    
    # Draw gradient bar
    gradient = np.linspace(0, 1, 100).reshape(1, -1)
    ax.imshow(gradient, aspect='auto', cmap='RdYlGn', extent=[0, 1, 0, 1], alpha=0.8)
    
    # Draw border
    rect = plt.Rectangle((0, 0), 1, 1, fill=False, edgecolor='#e2e8f0', linewidth=2)
    ax.add_patch(rect)
    
    # Current price marker
    ax.plot([position], [0.5], marker='v', markersize=15, color='#7c3aed', zorder=5)
    ax.axvline(x=position, color='#7c3aed', linestyle='-', linewidth=2, alpha=0.7)
    
    # Labels
    ax.text(0, -0.5, f'52W Low\n₹{low_52w:,.0f}', ha='left', va='top', 
            fontsize=9, color='#ef4444', fontweight='bold')
    ax.text(1, -0.5, f'52W High\n₹{high_52w:,.0f}', ha='right', va='top',
            fontsize=9, color='#22c55e', fontweight='bold')
    ax.text(position, 1.5, f'Current: ₹{current_price:,.0f}\n({position*100:.1f}%)',
            ha='center', va='bottom', fontsize=10, color='#7c3aed', fontweight='bold')
    
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-1.5, 2)
    ax.axis('off')
    ax.set_title('52-Week Price Range', fontsize=11, fontweight='bold', 
                 color='#7c3aed', pad=10)
    
    fig.patch.set_facecolor('white')
    plt.tight_layout()
    
    img_path = '/tmp/52week_range.png'
    plt.savefig(img_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    return img_path


def create_radar_chart(metrics: Dict[str, float], title: str = "Performance Metrics") -> str:
    """Create a radar/spider chart for multiple metrics"""
    categories = list(metrics.keys())
    values = list(metrics.values())
    
    # Number of variables
    num_vars = len(categories)
    
    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    # Complete the loop
    values += values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    
    # Draw the outline
    ax.plot(angles, values, 'o-', linewidth=2, color='#7c3aed')
    ax.fill(angles, values, alpha=0.25, color='#7c3aed')
    
    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=9, color='#475569')
    
    # Add gridlines
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], size=7, color='#94a3b8')
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Title
    ax.set_title(title, size=12, fontweight='bold', color='#7c3aed', pad=20)
    
    fig.patch.set_facecolor('white')
    plt.tight_layout()
    
    img_path = '/tmp/radar_chart.png'
    plt.savefig(img_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    return img_path


def create_upside_potential_chart(upside_pct: float) -> str:
    """Create a visual representation of upside/downside potential"""
    fig, ax = plt.subplots(figsize=(4, 2))
    
    # Determine color based on upside
    if upside_pct >= 25:
        color = '#22c55e'
        label = 'Strong Upside'
    elif upside_pct >= 10:
        color = '#06b6d4'
        label = 'Good Upside'
    elif upside_pct >= 0:
        color = '#eab308'
        label = 'Fair Value'
    else:
        color = '#ef4444'
        label = 'Overvalued'
    
    # Create horizontal bar
    bar_width = min(abs(upside_pct), 100)
    direction = 1 if upside_pct >= 0 else -1
    
    ax.barh([0], [bar_width * direction], height=0.5, color=color, alpha=0.8)
    ax.axvline(x=0, color='#475569', linewidth=2)
    
    # Add percentage label
    ax.text(upside_pct/2, 0, f'{upside_pct:+.1f}%', ha='center', va='center',
            fontsize=14, fontweight='bold', color='white' if abs(upside_pct) > 15 else color)
    
    # Add label
    ax.text(0, 0.7, label, ha='center', va='bottom', fontsize=10, 
            fontweight='bold', color=color)
    
    ax.set_xlim(-60, 60)
    ax.set_ylim(-1, 1.5)
    ax.axis('off')
    ax.set_title('Upside Potential', fontsize=11, fontweight='bold', 
                 color='#7c3aed', pad=10)
    
    fig.patch.set_facecolor('white')
    plt.tight_layout()
    
    img_path = '/tmp/upside_potential.png'
    plt.savefig(img_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    return img_path


# ============================================================================
# PDF DOCUMENT BUILDER
# ============================================================================

class NYZTradePDFReport:
    """
    Professional PDF Report Generator for NYZTrade Stock Valuation
    """
    
    def __init__(self, output_path: str, logo_path: Optional[str] = None):
        """
        Initialize the PDF report generator.
        
        Args:
            output_path: Path where the PDF will be saved
            logo_path: Optional path to the company logo image
        """
        self.output_path = output_path
        self.logo_path = logo_path
        self.styles = get_nyz_styles()
        self.width, self.height = A4
        self.story = []
        
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header line
        canvas.setStrokeColor(NYZColors.PRIMARY_PURPLE)
        canvas.setLineWidth(2)
        canvas.line(50, self.height - 40, self.width - 50, self.height - 40)
        
        # Header text
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(NYZColors.PRIMARY_PURPLE)
        canvas.drawString(50, self.height - 35, "NYZTrade Pro")
        
        # Date on right
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#64748b'))
        canvas.drawRightString(self.width - 50, self.height - 35, 
                               datetime.now().strftime("%B %d, %Y"))
        
        # Footer
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(1)
        canvas.line(50, 40, self.width - 50, 40)
        
        # Footer text
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#94a3b8'))
        canvas.drawString(50, 28, "© NYZTrade - Professional Stock Valuation")
        canvas.drawRightString(self.width - 50, 28, f"Page {doc.page}")
        
        # Confidential watermark (light)
        canvas.setFont('Helvetica', 6)
        canvas.setFillColor(colors.HexColor('#e2e8f0'))
        canvas.drawCentredString(self.width / 2, 28, "For Educational Purposes Only")
        
        canvas.restoreState()
    
    def _create_cover_page(self, stock_data: Dict[str, Any]):
        """Create the cover page with logo and stock info"""
        elements = []
        
        # Spacer from top
        elements.append(Spacer(1, 1.5 * inch))
        
        # Logo (if provided)
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=2*inch, height=2*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.3 * inch))
            except Exception as e:
                print(f"Logo error: {e}")
        
        # Title
        elements.append(Paragraph("NYZTrade Pro", self.styles['CoverTitle']))
        elements.append(Paragraph("Stock Valuation Report", self.styles['CoverSubtitle']))
        elements.append(Spacer(1, 0.5 * inch))
        
        # Horizontal line
        elements.append(HRFlowable(
            width="60%", thickness=2, color=NYZColors.PRIMARY_PURPLE,
            spaceBefore=10, spaceAfter=20, hAlign='CENTER'
        ))
        
        # Stock name and ticker
        stock_name = stock_data.get('name', 'Unknown Company')
        ticker = stock_data.get('ticker', 'N/A')
        sector = stock_data.get('sector', 'N/A')
        
        elements.append(Paragraph(
            f"<font size='24' color='#1e293b'><b>{stock_name}</b></font>",
            self.styles['CoverSubtitle']
        ))
        elements.append(Paragraph(
            f"<font size='14' color='#64748b'>{ticker} | {sector}</font>",
            self.styles['CoverSubtitle']
        ))
        
        elements.append(Spacer(1, 0.8 * inch))
        
        # Key metrics summary box
        current_price = stock_data.get('current_price', 0)
        fair_value = stock_data.get('fair_value', 0)
        upside = stock_data.get('upside_pct', 0)
        recommendation = stock_data.get('recommendation', 'Hold')
        
        # Create summary table
        summary_data = [
            ['Current Price', 'Fair Value', 'Upside', 'Recommendation'],
            [f'₹{current_price:,.2f}', f'₹{fair_value:,.2f}', 
             f'{upside:+.1f}%', recommendation]
        ]
        
        summary_table = Table(summary_data, colWidths=[1.5*inch]*4)
        
        # Get recommendation color
        rec_color = NYZColors.SUCCESS_GREEN
        if 'Buy' in recommendation:
            rec_color = NYZColors.SUCCESS_GREEN if 'Strong' in recommendation else NYZColors.CHART_CYAN
        elif 'Hold' in recommendation or 'Accumulate' in recommendation:
            rec_color = NYZColors.WARNING_YELLOW
        elif 'Avoid' in recommendation:
            rec_color = NYZColors.ERROR_RED
        
        summary_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), NYZColors.PRIMARY_PURPLE),
            ('TEXTCOLOR', (0, 0), (-1, 0), NYZColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 12),
            # Data row
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('TEXTCOLOR', (0, 1), (0, 1), NYZColors.PRIMARY_INDIGO),
            ('TEXTCOLOR', (1, 1), (1, 1), NYZColors.SUCCESS_GREEN),
            ('TEXTCOLOR', (2, 1), (2, 1), NYZColors.CHART_CYAN if upside > 0 else NYZColors.ERROR_RED),
            ('TEXTCOLOR', (3, 1), (3, 1), rec_color),
            # Borders
            ('BOX', (0, 0), (-1, -1), 2, NYZColors.PRIMARY_PURPLE),
            ('LINEBELOW', (0, 0), (-1, 0), 1, NYZColors.PRIMARY_PURPLE),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))
        
        elements.append(summary_table)
        
        elements.append(Spacer(1, 1 * inch))
        
        # Report date
        elements.append(Paragraph(
            f"<font size='10' color='#94a3b8'>Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</font>",
            self.styles['CoverSubtitle']
        ))
        
        # Page break
        elements.append(PageBreak())
        
        return elements
    
    def _create_executive_summary(self, stock_data: Dict[str, Any], 
                                  valuation_data: Dict[str, Any]):
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Company overview
        stock_name = stock_data.get('name', 'Unknown')
        ticker = stock_data.get('ticker', 'N/A')
        sector = stock_data.get('sector', 'N/A')
        current_price = stock_data.get('current_price', 0)
        fair_value = valuation_data.get('blended_fair_value', 0)
        upside = valuation_data.get('upside_pct', 0)
        recommendation = valuation_data.get('recommendation', 'Hold')
        
        overview_text = f"""
        This valuation report analyzes <b>{stock_name} ({ticker})</b> operating in the 
        <b>{sector}</b> sector. Based on comprehensive fundamental analysis using multiple 
        valuation methodologies, the stock is currently trading at <b>₹{current_price:,.2f}</b> 
        against our estimated fair value of <b>₹{fair_value:,.2f}</b>, representing a 
        potential {'upside' if upside > 0 else 'downside'} of <b>{abs(upside):.1f}%</b>.
        """
        elements.append(Paragraph(overview_text, self.styles['NYZBodyText']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Investment thesis
        elements.append(Paragraph("Investment Thesis", self.styles['SubsectionHeader']))
        
        if upside >= 25:
            thesis = f"""
            <b>STRONG BUY</b> - The stock presents an attractive investment opportunity with 
            significant upside potential. Current market price appears to substantially undervalue 
            the company's fundamentals and growth prospects.
            """
        elif upside >= 10:
            thesis = f"""
            <b>BUY</b> - The stock offers good upside potential based on our valuation analysis. 
            The current price provides a reasonable entry point for investors seeking exposure to 
            this sector.
            """
        elif upside >= 0:
            thesis = f"""
            <b>ACCUMULATE/HOLD</b> - The stock is trading near fair value. Consider accumulating 
            on dips or holding existing positions. Limited immediate upside but fundamentals 
            remain supportive.
            """
        else:
            thesis = f"""
            <b>CAUTION/AVOID</b> - The stock appears to be trading above our estimated fair value. 
            Consider booking profits if holding or waiting for better entry points. Current 
            valuation does not offer adequate margin of safety.
            """
        
        elements.append(Paragraph(thesis, self.styles['NYZBodyText']))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Key metrics table
        elements.append(Paragraph("Key Valuation Metrics", self.styles['SubsectionHeader']))
        
        pe_ratio = valuation_data.get('pe_ratio', 0)
        industry_pe = valuation_data.get('industry_pe', 0)
        ev_ebitda = valuation_data.get('ev_ebitda', 0)
        industry_ev_ebitda = valuation_data.get('industry_ev_ebitda', 0)
        
        metrics_data = [
            ['Metric', 'Current', 'Industry Avg', 'Status'],
            ['P/E Ratio', f'{pe_ratio:.2f}x', f'{industry_pe:.2f}x', 
             '✓ Undervalued' if pe_ratio < industry_pe else '⚠ Premium'],
            ['EV/EBITDA', f'{ev_ebitda:.2f}x', f'{industry_ev_ebitda:.2f}x',
             '✓ Undervalued' if ev_ebitda < industry_ev_ebitda else '⚠ Premium'],
            ['Current Price', f'₹{current_price:,.2f}', f'₹{fair_value:,.2f} (Fair)', 
             '✓ Buy Zone' if upside > 10 else ('⚠ Hold' if upside > -10 else '✗ Expensive')],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.3*inch, 1.5*inch, 1.3*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NYZColors.PRIMARY_PURPLE),
            ('TEXTCOLOR', (0, 0), (-1, 0), NYZColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#f1f5f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('BOX', (0, 0), (-1, -1), 1, NYZColors.PRIMARY_PURPLE),
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _create_valuation_analysis(self, valuation_data: Dict[str, Any]):
        """Create detailed valuation analysis section with charts"""
        elements = []
        
        elements.append(Paragraph("Valuation Analysis", self.styles['SectionHeader']))
        
        # PE Multiple Analysis
        elements.append(Paragraph("1. P/E Multiple Valuation", self.styles['SubsectionHeader']))
        
        pe_ratio = valuation_data.get('pe_ratio', 0)
        industry_pe = valuation_data.get('industry_pe', 0)
        historical_pe = valuation_data.get('historical_pe', 0)
        eps = valuation_data.get('eps', 0)
        fair_value_pe = valuation_data.get('fair_value_pe', 0)
        
        pe_text = f"""
        The Price-to-Earnings (P/E) multiple analysis values the stock based on its earnings 
        capacity relative to industry peers. The current P/E ratio of <b>{pe_ratio:.2f}x</b> 
        compares to the industry average of <b>{industry_pe:.2f}x</b> and historical average 
        of <b>{historical_pe:.2f}x</b>. Using blended PE methodology with EPS of 
        <b>₹{eps:.2f}</b>, we arrive at a fair value of <b>₹{fair_value_pe:,.2f}</b>.
        """
        elements.append(Paragraph(pe_text, self.styles['NYZBodyText']))
        
        # Create and add PE gauge chart
        try:
            pe_gauge_path = create_gauge_chart(pe_ratio, 0, industry_pe * 2, "P/E Ratio", "x")
            pe_gauge = Image(pe_gauge_path, width=3*inch, height=2*inch)
            pe_gauge.hAlign = 'CENTER'
            elements.append(pe_gauge)
        except Exception as e:
            print(f"PE gauge error: {e}")
        
        elements.append(Spacer(1, 0.2 * inch))
        
        # EV/EBITDA Analysis
        elements.append(Paragraph("2. EV/EBITDA Valuation", self.styles['SubsectionHeader']))
        
        ev_ebitda = valuation_data.get('ev_ebitda', 0)
        industry_ev_ebitda = valuation_data.get('industry_ev_ebitda', 0)
        ebitda = valuation_data.get('ebitda', 0)
        enterprise_value = valuation_data.get('enterprise_value', 0)
        fair_value_ev = valuation_data.get('fair_value_ev', 0)
        
        ev_text = f"""
        Enterprise Value to EBITDA (EV/EBITDA) provides a capital structure-neutral valuation 
        metric. Current EV/EBITDA of <b>{ev_ebitda:.2f}x</b> versus industry benchmark of 
        <b>{industry_ev_ebitda:.2f}x</b>. With EBITDA of <b>₹{ebitda/10000000:,.2f} Cr</b> 
        and Enterprise Value of <b>₹{enterprise_value/10000000:,.2f} Cr</b>, the implied 
        fair value is <b>₹{fair_value_ev:,.2f}</b>.
        """
        elements.append(Paragraph(ev_text, self.styles['NYZBodyText']))
        
        # Create and add EV/EBITDA gauge chart
        try:
            ev_gauge_path = create_gauge_chart(ev_ebitda, 0, industry_ev_ebitda * 2, "EV/EBITDA", "x")
            ev_gauge = Image(ev_gauge_path, width=3*inch, height=2*inch)
            ev_gauge.hAlign = 'CENTER'
            elements.append(ev_gauge)
        except Exception as e:
            print(f"EV gauge error: {e}")
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Valuation comparison chart
        elements.append(Paragraph("3. Valuation Comparison", self.styles['SubsectionHeader']))
        
        current_price = valuation_data.get('current_price', 0)
        blended_fair_value = valuation_data.get('blended_fair_value', 0)
        
        try:
            comparison_path = create_valuation_comparison_chart(
                current_price, fair_value_pe, fair_value_ev, blended_fair_value
            )
            comparison_img = Image(comparison_path, width=5*inch, height=3*inch)
            comparison_img.hAlign = 'CENTER'
            elements.append(comparison_img)
        except Exception as e:
            print(f"Comparison chart error: {e}")
        
        # Blended valuation summary
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph("Blended Fair Value Calculation", self.styles['SubsectionHeader']))
        
        blend_text = f"""
        Our blended fair value of <b>₹{blended_fair_value:,.2f}</b> is derived by combining 
        the P/E method (₹{fair_value_pe:,.2f}) and EV/EBITDA method (₹{fair_value_ev:,.2f}) 
        with equal weightage. This provides a more robust estimate by incorporating multiple 
        valuation perspectives.
        """
        elements.append(Paragraph(blend_text, self.styles['NYZBodyText']))
        
        elements.append(PageBreak())
        
        return elements
    
    def _create_price_analysis(self, stock_data: Dict[str, Any], valuation_data: Dict[str, Any]):
        """Create price analysis section with 52-week range and upside charts"""
        elements = []
        
        elements.append(Paragraph("Price Analysis", self.styles['SectionHeader']))
        
        # 52-week range
        elements.append(Paragraph("52-Week Price Range", self.styles['SubsectionHeader']))
        
        low_52w = stock_data.get('low_52w', 0)
        high_52w = stock_data.get('high_52w', 0)
        current_price = stock_data.get('current_price', 0)
        
        range_text = f"""
        The stock has traded between <b>₹{low_52w:,.2f}</b> (52-week low) and 
        <b>₹{high_52w:,.2f}</b> (52-week high) over the past year. Current price of 
        <b>₹{current_price:,.2f}</b> is positioned at <b>{((current_price - low_52w) / (high_52w - low_52w) * 100):.1f}%</b> 
        of this range.
        """
        elements.append(Paragraph(range_text, self.styles['NYZBodyText']))
        
        # 52-week range chart
        try:
            range_path = create_52week_range_chart(low_52w, high_52w, current_price)
            range_img = Image(range_path, width=5*inch, height=1.5*inch)
            range_img.hAlign = 'CENTER'
            elements.append(range_img)
        except Exception as e:
            print(f"Range chart error: {e}")
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Upside potential
        elements.append(Paragraph("Upside/Downside Potential", self.styles['SubsectionHeader']))
        
        upside = valuation_data.get('upside_pct', 0)
        
        upside_text = f"""
        Based on our blended fair value estimate, the stock offers a 
        <b>{'potential upside' if upside > 0 else 'potential downside'} of {abs(upside):.1f}%</b> 
        from current levels. This assessment considers both relative valuation metrics and 
        absolute price levels.
        """
        elements.append(Paragraph(upside_text, self.styles['NYZBodyText']))
        
        # Upside chart
        try:
            upside_path = create_upside_potential_chart(upside)
            upside_img = Image(upside_path, width=3.5*inch, height=1.8*inch)
            upside_img.hAlign = 'CENTER'
            elements.append(upside_img)
        except Exception as e:
            print(f"Upside chart error: {e}")
        
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _create_financial_summary(self, financial_data: Dict[str, Any]):
        """Create comprehensive financial metrics table"""
        elements = []
        
        elements.append(Paragraph("Financial Summary", self.styles['SectionHeader']))
        
        # Prepare data for table
        metrics = [
            ('Market Capitalization', f"₹{financial_data.get('market_cap', 0)/10000000:,.2f} Cr"),
            ('Enterprise Value', f"₹{financial_data.get('enterprise_value', 0)/10000000:,.2f} Cr"),
            ('Revenue (TTM)', f"₹{financial_data.get('revenue', 0)/10000000:,.2f} Cr"),
            ('EBITDA (TTM)', f"₹{financial_data.get('ebitda', 0)/10000000:,.2f} Cr"),
            ('Net Profit (TTM)', f"₹{financial_data.get('net_income', 0)/10000000:,.2f} Cr"),
            ('EPS (TTM)', f"₹{financial_data.get('eps', 0):,.2f}"),
            ('Book Value per Share', f"₹{financial_data.get('book_value', 0):,.2f}"),
            ('P/E Ratio', f"{financial_data.get('pe_ratio', 0):.2f}x"),
            ('P/B Ratio', f"{financial_data.get('pb_ratio', 0):.2f}x"),
            ('EV/EBITDA', f"{financial_data.get('ev_ebitda', 0):.2f}x"),
            ('EV/Sales', f"{financial_data.get('ev_sales', 0):.2f}x"),
            ('ROE', f"{financial_data.get('roe', 0)*100:.2f}%"),
            ('ROA', f"{financial_data.get('roa', 0)*100:.2f}%"),
            ('Debt to Equity', f"{financial_data.get('debt_equity', 0):.2f}x"),
            ('Current Ratio', f"{financial_data.get('current_ratio', 0):.2f}x"),
            ('Dividend Yield', f"{financial_data.get('dividend_yield', 0)*100:.2f}%"),
            ('52-Week High', f"₹{financial_data.get('high_52w', 0):,.2f}"),
            ('52-Week Low', f"₹{financial_data.get('low_52w', 0):,.2f}"),
        ]
        
        # Split into two columns
        mid = len(metrics) // 2
        left_metrics = metrics[:mid]
        right_metrics = metrics[mid:]
        
        # Create table data
        table_data = [['Metric', 'Value', 'Metric', 'Value']]
        for i in range(max(len(left_metrics), len(right_metrics))):
            row = []
            if i < len(left_metrics):
                row.extend([left_metrics[i][0], left_metrics[i][1]])
            else:
                row.extend(['', ''])
            if i < len(right_metrics):
                row.extend([right_metrics[i][0], right_metrics[i][1]])
            else:
                row.extend(['', ''])
            table_data.append(row)
        
        # Create table
        fin_table = Table(table_data, colWidths=[1.6*inch, 1.2*inch, 1.6*inch, 1.2*inch])
        fin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NYZColors.PRIMARY_PURPLE),
            ('TEXTCOLOR', (0, 0), (-1, 0), NYZColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#f1f5f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('BOX', (0, 0), (-1, -1), 1, NYZColors.PRIMARY_PURPLE),
            # Add vertical line between the two metric sets
            ('LINEAFTER', (1, 0), (1, -1), 1, NYZColors.PRIMARY_PURPLE),
        ]))
        
        elements.append(fin_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _create_performance_radar(self, performance_data: Dict[str, float]):
        """Create performance radar chart section"""
        elements = []
        
        elements.append(Paragraph("Performance Scorecard", self.styles['SubsectionHeader']))
        
        # Default metrics if not provided
        if not performance_data:
            performance_data = {
                'Valuation': 65,
                'Growth': 70,
                'Profitability': 75,
                'Momentum': 60,
                'Quality': 80,
                'Dividend': 50
            }
        
        try:
            radar_path = create_radar_chart(performance_data, "Multi-Factor Score")
            radar_img = Image(radar_path, width=4*inch, height=4*inch)
            radar_img.hAlign = 'CENTER'
            elements.append(radar_img)
        except Exception as e:
            print(f"Radar chart error: {e}")
        
        # Explanation
        radar_text = """
        The performance scorecard evaluates the stock across multiple dimensions including 
        valuation attractiveness, growth potential, profitability metrics, price momentum, 
        business quality, and dividend profile. Higher scores indicate stronger performance 
        in each category.
        """
        elements.append(Paragraph(radar_text, self.styles['NYZBodyText']))
        
        return elements
    
    def _create_disclaimer(self):
        """Create disclaimer page"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Important Disclaimer", self.styles['SectionHeader']))
        
        disclaimer_text = """
        <b>FOR EDUCATIONAL PURPOSES ONLY</b><br/><br/>
        
        This report has been prepared by NYZTrade for educational and informational purposes 
        only. The information contained herein is based on sources believed to be reliable, 
        but no representation or warranty, express or implied, is made as to the accuracy, 
        completeness, or reliability of such information.<br/><br/>
        
        <b>NOT INVESTMENT ADVICE</b><br/><br/>
        
        This report does not constitute investment advice, financial advice, trading advice, 
        or any other sort of advice. The valuation methodologies and fair value estimates 
        presented are based on quantitative models and may not reflect all factors relevant 
        to investment decisions.<br/><br/>
        
        <b>RISK DISCLOSURE</b><br/><br/>
        
        Investments in securities are subject to market risks. Past performance is not 
        indicative of future results. The value of investments and income from them may 
        go down as well as up. Investors should conduct their own due diligence and/or 
        consult with a qualified financial advisor before making any investment decisions.<br/><br/>
        
        <b>NO LIABILITY</b><br/><br/>
        
        NYZTrade, its owners, employees, and affiliates shall not be liable for any direct, 
        indirect, incidental, special, consequential, or exemplary damages resulting from 
        the use of or reliance on this report.<br/><br/>
        
        <b>DATA SOURCES</b><br/><br/>
        
        Financial data used in this report is sourced from publicly available information 
        including but not limited to company filings, stock exchanges, and third-party 
        data providers. Data accuracy is subject to the reliability of these sources.<br/><br/>
        
        <b>REGULATORY COMPLIANCE</b><br/><br/>
        
        This report is prepared in accordance with general educational content guidelines. 
        It is not a research report as defined by SEBI (Research Analysts) Regulations, 2014. 
        NYZTrade is not registered as a Research Analyst with SEBI.<br/><br/>
        
        By using this report, you acknowledge that you have read, understood, and agree 
        to be bound by this disclaimer.
        """
        
        elements.append(Paragraph(disclaimer_text, self.styles['DisclaimerText']))
        
        elements.append(Spacer(1, 0.5 * inch))
        
        # Contact info
        contact_text = """
        <b>Contact & Support</b><br/>
        YouTube: NYZTrade<br/>
        Email: contact@nyztrade.com<br/>
        Website: www.nyztrade.com
        """
        elements.append(Paragraph(contact_text, self.styles['NYZBodyText']))
        
        return elements
    
    def generate_report(self, stock_data: Dict[str, Any], valuation_data: Dict[str, Any],
                        financial_data: Dict[str, Any], performance_data: Optional[Dict[str, float]] = None):
        """
        Generate the complete PDF report.
        
        Args:
            stock_data: Dictionary containing stock information (name, ticker, sector, prices)
            valuation_data: Dictionary containing valuation metrics and fair values
            financial_data: Dictionary containing financial metrics
            performance_data: Optional dictionary for radar chart scores
        """
        # Create document
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=60,
            bottomMargin=50
        )
        
        # Build story
        self.story = []
        
        # Cover page
        self.story.extend(self._create_cover_page(stock_data))
        
        # Executive summary
        self.story.extend(self._create_executive_summary(stock_data, valuation_data))
        
        # Valuation analysis with charts
        self.story.extend(self._create_valuation_analysis(valuation_data))
        
        # Price analysis
        self.story.extend(self._create_price_analysis(stock_data, valuation_data))
        
        # Performance radar
        self.story.extend(self._create_performance_radar(performance_data))
        
        # Financial summary
        self.story.extend(self._create_financial_summary(financial_data))
        
        # Disclaimer
        self.story.extend(self._create_disclaimer())
        
        # Build PDF
        doc.build(self.story, onFirstPage=self._add_header_footer, 
                  onLaterPages=self._add_header_footer)
        
        return self.output_path


# ============================================================================
# STREAMLIT INTEGRATION FUNCTION
# ============================================================================

def generate_valuation_pdf(ticker: str, stock_info: Dict, valuation_results: Dict,
                           logo_path: Optional[str] = None) -> bytes:
    """
    Generate PDF report and return as bytes for Streamlit download.
    
    This function is designed to integrate with the NYZTrade Streamlit app.
    
    Args:
        ticker: Stock ticker symbol
        stock_info: Dictionary from yfinance with stock information
        valuation_results: Dictionary containing calculated valuation metrics
        logo_path: Optional path to logo image file
    
    Returns:
        PDF file as bytes for Streamlit download button
    """
    
    # Prepare stock data
    stock_data = {
        'name': stock_info.get('longName', stock_info.get('shortName', ticker)),
        'ticker': ticker,
        'sector': stock_info.get('sector', 'N/A'),
        'industry': stock_info.get('industry', 'N/A'),
        'current_price': stock_info.get('currentPrice', stock_info.get('regularMarketPrice', 0)),
        'fair_value': valuation_results.get('blended_fair_value', 0),
        'upside_pct': valuation_results.get('upside_pct', 0),
        'recommendation': valuation_results.get('recommendation', 'Hold'),
        'low_52w': stock_info.get('fiftyTwoWeekLow', 0),
        'high_52w': stock_info.get('fiftyTwoWeekHigh', 0),
    }
    
    # Prepare valuation data
    valuation_data = {
        'current_price': stock_data['current_price'],
        'pe_ratio': stock_info.get('trailingPE', 0) or 0,
        'industry_pe': valuation_results.get('industry_pe', 20),
        'historical_pe': valuation_results.get('historical_pe', 18),
        'eps': stock_info.get('trailingEps', 0) or 0,
        'fair_value_pe': valuation_results.get('fair_value_pe', 0),
        'ev_ebitda': stock_info.get('enterpriseToEbitda', 0) or 0,
        'industry_ev_ebitda': valuation_results.get('industry_ev_ebitda', 12),
        'ebitda': stock_info.get('ebitda', 0) or 0,
        'enterprise_value': stock_info.get('enterpriseValue', 0) or 0,
        'fair_value_ev': valuation_results.get('fair_value_ev', 0),
        'blended_fair_value': valuation_results.get('blended_fair_value', 0),
        'upside_pct': valuation_results.get('upside_pct', 0),
        'recommendation': valuation_results.get('recommendation', 'Hold'),
    }
    
    # Prepare financial data
    financial_data = {
        'market_cap': stock_info.get('marketCap', 0) or 0,
        'enterprise_value': stock_info.get('enterpriseValue', 0) or 0,
        'revenue': stock_info.get('totalRevenue', 0) or 0,
        'ebitda': stock_info.get('ebitda', 0) or 0,
        'net_income': stock_info.get('netIncomeToCommon', 0) or 0,
        'eps': stock_info.get('trailingEps', 0) or 0,
        'book_value': stock_info.get('bookValue', 0) or 0,
        'pe_ratio': stock_info.get('trailingPE', 0) or 0,
        'pb_ratio': stock_info.get('priceToBook', 0) or 0,
        'ev_ebitda': stock_info.get('enterpriseToEbitda', 0) or 0,
        'ev_sales': stock_info.get('enterpriseToRevenue', 0) or 0,
        'roe': stock_info.get('returnOnEquity', 0) or 0,
        'roa': stock_info.get('returnOnAssets', 0) or 0,
        'debt_equity': stock_info.get('debtToEquity', 0) / 100 if stock_info.get('debtToEquity') else 0,
        'current_ratio': stock_info.get('currentRatio', 0) or 0,
        'dividend_yield': stock_info.get('dividendYield', 0) or 0,
        'high_52w': stock_info.get('fiftyTwoWeekHigh', 0) or 0,
        'low_52w': stock_info.get('fiftyTwoWeekLow', 0) or 0,
    }
    
    # Calculate performance scores for radar chart
    pe_score = max(0, min(100, 100 - (valuation_data['pe_ratio'] / valuation_data['industry_pe'] * 50))) if valuation_data['industry_pe'] > 0 else 50
    ev_score = max(0, min(100, 100 - (valuation_data['ev_ebitda'] / valuation_data['industry_ev_ebitda'] * 50))) if valuation_data['industry_ev_ebitda'] > 0 else 50
    
    performance_data = {
        'Valuation': round((pe_score + ev_score) / 2),
        'Growth': round(min(100, max(0, 50 + (stock_info.get('earningsGrowth', 0) or 0) * 100))),
        'Profitability': round(min(100, max(0, (financial_data['roe'] * 200)))),
        'Quality': round(min(100, max(0, 80 - financial_data['debt_equity'] * 20))),
        'Momentum': round(min(100, max(0, 50 + valuation_data['upside_pct']))),
        'Dividend': round(min(100, max(0, financial_data['dividend_yield'] * 1000))),
    }
    
    # Generate PDF
    output_path = f'/tmp/NYZTrade_{ticker}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    report = NYZTradePDFReport(output_path, logo_path)
    report.generate_report(stock_data, valuation_data, financial_data, performance_data)
    
    # Read and return as bytes
    with open(output_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Cleanup
    try:
        os.remove(output_path)
        # Clean up chart images
        for img_file in ['/tmp/gauge_p_e_ratio.png', '/tmp/gauge_ev_ebitda.png',
                         '/tmp/valuation_comparison.png', '/tmp/52week_range.png',
                         '/tmp/upside_potential.png', '/tmp/radar_chart.png']:
            if os.path.exists(img_file):
                os.remove(img_file)
    except:
        pass
    
    return pdf_bytes


# ============================================================================
# EXAMPLE USAGE / TESTING
# ============================================================================

if __name__ == "__main__":
    # Example data for testing
    sample_stock_data = {
        'name': 'Reliance Industries Limited',
        'ticker': 'RELIANCE.NS',
        'sector': 'Energy',
        'industry': 'Oil & Gas Refining',
        'current_price': 2450.50,
        'fair_value': 2850.00,
        'upside_pct': 16.3,
        'recommendation': 'Buy',
        'low_52w': 2180.00,
        'high_52w': 2856.00,
    }
    
    sample_valuation_data = {
        'current_price': 2450.50,
        'pe_ratio': 22.5,
        'industry_pe': 18.5,
        'historical_pe': 20.0,
        'eps': 108.91,
        'fair_value_pe': 2178.20,
        'ev_ebitda': 10.8,
        'industry_ev_ebitda': 9.5,
        'ebitda': 1250000000000,  # in INR
        'enterprise_value': 13500000000000,
        'fair_value_ev': 2650.00,
        'blended_fair_value': 2414.10,
        'upside_pct': -1.5,
        'recommendation': 'Hold',
    }
    
    sample_financial_data = {
        'market_cap': 16000000000000,
        'enterprise_value': 13500000000000,
        'revenue': 8500000000000,
        'ebitda': 1250000000000,
        'net_income': 680000000000,
        'eps': 108.91,
        'book_value': 1250.50,
        'pe_ratio': 22.5,
        'pb_ratio': 1.96,
        'ev_ebitda': 10.8,
        'ev_sales': 1.59,
        'roe': 0.095,
        'roa': 0.065,
        'debt_equity': 0.45,
        'current_ratio': 1.25,
        'dividend_yield': 0.004,
        'high_52w': 2856.00,
        'low_52w': 2180.00,
    }
    
    sample_performance = {
        'Valuation': 65,
        'Growth': 72,
        'Profitability': 78,
        'Quality': 85,
        'Momentum': 58,
        'Dividend': 35,
    }
    
    # Generate test report
    output_file = '/tmp/NYZTrade_Test_Report.pdf'
    report = NYZTradePDFReport(output_file)
    report.generate_report(sample_stock_data, sample_valuation_data, 
                          sample_financial_data, sample_performance)
    
    print(f"✅ Test report generated: {output_file}")
