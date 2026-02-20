"""
UI Theme System - Methanex color palette and animation utilities
Based on Methanex branding: https://www.methanex.com/
"""

# Methanex Color Palette
COLORS = {
    'primary': '#1E3A8A',        # Navy Blue - Main brand color
    'secondary': '#3B82F6',      # Royal Blue - Accents
    'light_blue': '#60A5FA',     # Light Blue - Highlights
    'success': '#10B981',        # Green - Success states
    'warning': '#F59E0B',        # Orange - Warnings
    'error': '#EF4444',          # Red - Critical alerts
    'critical': '#991B1B',       # Dark Red - Critical
    'background': '#F8FAFC',      # Light Gray - Page background
    'card': '#FFFFFF',           # White - Card backgrounds
    'text_primary': '#1F2937',   # Dark Gray - Main text
    'text_secondary': '#6B7280', # Medium Gray - Secondary text
    'border': '#E5E7EB',         # Light Gray - Borders
}

# Severity Colors
SEVERITY_COLORS = {
    'Low': COLORS['success'],
    'Medium': COLORS['warning'],
    'High': COLORS['error'],
    'Critical': COLORS['critical']
}


def get_css_theme():
    """
    Get complete CSS theme with Methanex colors and animations
    """
    return f"""
    <style>
    /* Methanex Color Variables */
    :root {{
        --methanex-primary: {COLORS['primary']};
        --methanex-secondary: {COLORS['secondary']};
        --methanex-light-blue: {COLORS['light_blue']};
        --methanex-success: {COLORS['success']};
        --methanex-warning: {COLORS['warning']};
        --methanex-error: {COLORS['error']};
        --methanex-critical: {COLORS['critical']};
        --methanex-background: {COLORS['background']};
        --methanex-card: {COLORS['card']};
        --methanex-text-primary: {COLORS['text_primary']};
        --methanex-text-secondary: {COLORS['text_secondary']};
    }}
    
    /* Global Styles */
    .stApp {{
        background-color: {COLORS['background']};
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes slideIn {{
        from {{
            opacity: 0;
            transform: translateX(-20px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{
            opacity: 1;
        }}
        50% {{
            opacity: 0.7;
        }}
    }}
    
    @keyframes spin {{
        from {{
            transform: rotate(0deg);
        }}
        to {{
            transform: rotate(360deg);
        }}
    }}
    
    /* Card Styles */
    .methanex-card {{
        background-color: {COLORS['card']};
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeIn 0.4s ease-out;
    }}
    
    .methanex-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(30, 58, 138, 0.15);
    }}
    
    /* Large hero-style cards (e.g. home page options) */
    .methanex-card.methanex-card-hero {{
        padding: 3rem 2rem;
    }}
    .methanex-card .card-title {{
        color: {COLORS['primary']};
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }}
    .methanex-card .card-desc {{
        color: {COLORS['text_secondary']};
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }}
    .methanex-card .card-features {{
        font-size: 0.9rem;
        color: {COLORS['text_secondary']};
    }}
    @media (max-width: 480px) {{
        .methanex-card .card-title {{
            font-size: 1.25rem;
        }}
        .methanex-card .card-desc {{
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }}
        .methanex-card .card-features {{
            font-size: 0.85rem;
        }}
    }}
    
    /* Button Styles */
    .methanex-button-primary {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .methanex-button-primary:hover {{
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
    }}
    
    /* Metric Styles */
    .methanex-metric {{
        background: {COLORS['card']};
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid {COLORS['primary']};
        animation: fadeIn 0.5s ease-out;
    }}
    
    /* Alert Styles */
    .methanex-alert {{
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        animation: slideIn 0.3s ease-out;
    }}
    
    .methanex-alert-success {{
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 4px solid {COLORS['success']};
        color: {COLORS['text_primary']};
    }}
    
    .methanex-alert-warning {{
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 4px solid {COLORS['warning']};
        color: {COLORS['text_primary']};
    }}
    
    .methanex-alert-error {{
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid {COLORS['error']};
        color: {COLORS['text_primary']};
    }}
    
    .methanex-alert-critical {{
        background-color: rgba(153, 27, 27, 0.1);
        border-left: 4px solid {COLORS['critical']};
        color: {COLORS['text_primary']};
        animation: pulse 2s infinite;
    }}
    
    /* Severity Badges */
    .severity-badge {{
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        animation: fadeIn 0.4s ease-out;
    }}
    
    .severity-low {{
        background-color: rgba(16, 185, 129, 0.1);
        color: {COLORS['success']};
    }}
    
    .severity-medium {{
        background-color: rgba(245, 158, 11, 0.1);
        color: {COLORS['warning']};
    }}
    
    .severity-high {{
        background-color: rgba(239, 68, 68, 0.1);
        color: {COLORS['error']};
    }}
    
    .severity-critical {{
        background-color: rgba(153, 27, 27, 0.1);
        color: {COLORS['critical']};
        animation: pulse 2s infinite;
    }}
    
    /* Recommendation cards – compact, scannable */
    .rec-card {{
        background: {COLORS['card']};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border-left: 4px solid {COLORS['border']};
        animation: fadeIn 0.35s ease-out;
    }}
    .rec-card.rec-priority-critical {{ border-left-color: {COLORS['critical']}; }}
    .rec-card.rec-priority-high {{ border-left-color: {COLORS['error']}; }}
    .rec-card.rec-priority-medium {{ border-left-color: {COLORS['warning']}; }}
    .rec-card.rec-priority-low {{ border-left-color: {COLORS['success']}; }}
    .rec-card-header {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
    }}
    .rec-title {{
        font-weight: 600;
        color: {COLORS['text_primary']};
        font-size: 1rem;
        margin: 0;
    }}
    .rec-priority-badge {{
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    .rec-priority-badge.critical {{ background: rgba(153, 27, 27, 0.15); color: {COLORS['critical']}; }}
    .rec-priority-badge.high {{ background: rgba(239, 68, 68, 0.15); color: {COLORS['error']}; }}
    .rec-priority-badge.medium {{ background: rgba(245, 158, 11, 0.15); color: {COLORS['warning']}; }}
    .rec-priority-badge.low {{ background: rgba(16, 185, 129, 0.15); color: {COLORS['success']}; }}
    .rec-desc {{
        color: {COLORS['text_secondary']};
        font-size: 0.9rem;
        line-height: 1.4;
        margin: 0 0 0.5rem 0;
    }}
    .rec-timeline {{
        font-size: 0.8rem;
        color: {COLORS['primary']};
        font-weight: 500;
    }}
    .rec-actions-list {{
        margin: 0.5rem 0 0 0;
        padding-left: 1.2rem;
        font-size: 0.85rem;
        color: {COLORS['text_secondary']};
        line-height: 1.5;
    }}
    .rec-actions-list li {{
        margin-bottom: 0.25rem;
    }}
    
    /* Loading Spinner */
    .methanex-spinner {{
        border: 3px solid rgba(30, 58, 138, 0.1);
        border-top: 3px solid {COLORS['primary']};
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }}
    
    /* Progress Bar */
    .methanex-progress {{
        width: 100%;
        height: 8px;
        background-color: rgba(30, 58, 138, 0.1);
        border-radius: 4px;
        overflow: hidden;
    }}
    
    .methanex-progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
        animation: pulse 2s infinite;
    }}
    
    /* Fade In Animation */
    .fade-in {{
        animation: fadeIn 0.4s ease-out;
    }}
    
    /* Slide In Animation */
    .slide-in {{
        animation: slideIn 0.3s ease-out;
    }}
    
    /* Pulse Animation */
    .pulse {{
        animation: pulse 2s infinite;
    }}
    
    /* Hero Section */
    .hero-section {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        animation: fadeIn 0.6s ease-out;
    }}
    
    .hero-title {{
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }}
    
    .hero-subtitle {{
        font-size: 1.2rem;
        opacity: 0.9;
    }}
    
    /* ========== Mobile & cross-device responsive ========== */
    /* Prevent horizontal overflow on all devices */
    html, body, .stApp, [data-testid="stAppViewContainer"], .main .block-container {{
        max-width: 100vw;
        overflow-x: hidden;
        box-sizing: border-box;
    }}
    /* Allow long text and alerts to wrap on small screens */
    .methanex-alert, .stMarkdown p, .stMarkdown li {{
        word-wrap: break-word;
        overflow-wrap: break-word;
    }}
    * {{
        box-sizing: border-box;
    }}
    /* Smooth touch scrolling on iOS */
    .stApp {{
        -webkit-overflow-scrolling: touch;
    }}
    /* Stack Streamlit columns on tablet and mobile */
    @media (max-width: 1024px) {{
        [data-testid="column"] {{
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }}
        /* Streamlit horizontal block: allow flex wrap */
        [data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap !important;
        }}
    }}
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 100%;
        }}
        .hero-title {{
            font-size: 1.75rem;
        }}
        .hero-subtitle {{
            font-size: 0.95rem;
        }}
        .hero-section {{
            padding: 2rem 1rem;
        }}
        .methanex-card {{
            padding: 1.25rem;
        }}
        .methanex-card.methanex-card-hero {{
            padding: 2rem 1rem;
        }}
        /* Touch-friendly tap targets (min 44px) */
        button, [role="button"], .stButton > button {{
            min-height: 44px;
            min-width: 44px;
        }}
    }}
    @media (max-width: 480px) {{
        .hero-title {{
            font-size: 1.4rem;
        }}
        .hero-subtitle {{
            font-size: 0.875rem;
        }}
        .hero-section {{
            padding: 1.5rem 0.75rem;
        }}
        .methanex-card {{
            padding: 1rem;
        }}
        .methanex-card.methanex-card-hero {{
            padding: 1.5rem 0.75rem;
        }}
        .severity-badge {{
            padding: 0.35rem 0.75rem;
            font-size: 0.8rem;
        }}
    }}
    /* Scrollable data/table containers on small screens */
    @media (max-width: 768px) {{
        [data-testid="stDataFrame"], [data-testid="stDataFrameResizable"] {{
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}
        .stPlotlyChart {{
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}
    }}
    </style>
    """


def get_severity_badge_html(severity_level):
    """
    Get HTML for severity badge
    """
    color = SEVERITY_COLORS.get(severity_level, COLORS['text_secondary'])
    return f"""
    <span class="severity-badge severity-{severity_level.lower()}" style="background-color: rgba({_hex_to_rgb(color)}, 0.1); color: {color};">
        {severity_level}
    </span>
    """


def _hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return ','.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))


# Priority badge for recommendations (Critical, High, Medium, Low)
PRIORITY_COLORS = {
    'Critical': COLORS['critical'],
    'High': COLORS['error'],
    'Medium': COLORS['warning'],
    'Low': COLORS['success'],
}


def get_priority_badge_html(priority):
    """Return HTML for a recommendation priority badge."""
    p = (priority or 'Medium').lower()
    return f'<span class="rec-priority-badge {p}">{priority}</span>'


def get_recommendation_card_html(rec, index, include_actions=True):
    """
    Return HTML for one recommendation card (compact, scannable).
    rec: dict with title, priority, description, timeline, actions (list)
    index: 1-based number
    include_actions: if True, render actions list inside the card; if False, card is summary-only (actions in expander).
    """
    priority = (rec.get('priority') or 'Medium').strip()
    pclass = priority.lower()
    title = rec.get('title', 'Recommendation')
    desc = rec.get('description', '')
    timeline = rec.get('timeline', '')
    actions = rec.get('actions') or []
    badge = get_priority_badge_html(priority)
    actions_html = ''
    if include_actions and actions:
        lis = ''.join(f'<li>{a}</li>' for a in actions)
        actions_html = f'<ul class="rec-actions-list">{lis}</ul>'
    return f"""
    <div class="rec-card rec-priority-{pclass}">
        <div class="rec-card-header">
            <span class="rec-priority-badge {pclass}">{priority}</span>
            <span class="rec-title">{index}. {title}</span>
        </div>
        <p class="rec-desc">{desc}</p>
        <p class="rec-timeline">⏱ {timeline}</p>
        {actions_html}
    </div>
    """

