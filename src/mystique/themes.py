import streamlit as st

THEMES = {
    "Mystique (Default)": {
        "primaryColor": "#8A2BE2",      # Deep Purple
        "headerColor": "#BF5AF2",       # Vibrant Violet
        "backgroundColor": "#0E1117",   # Dark Slate
        "textColor": "#E0E0E0",         # Light Grey
        "buttonTextColor": "#FFFFFF",
    },
    "Wolverine": {
        "primaryColor": "#FFC107",      # Amber (Darker Gold)
        "headerColor": "#FFD700",       # Pure Gold
        "backgroundColor": "#0F172A",   # Deep Blue
        "textColor": "#E2E8F0",         # White-ish
        "buttonTextColor": "#000000",   # Black text
    },
    "Psylocke": {
        "primaryColor": "#D946EF",      # Magenta
        "headerColor": "#FF00FF",       # Neon Magenta
        "backgroundColor": "#180818",   # Very Dark Purple
        "textColor": "#F3E8FF",         # Pale Purple
        "buttonTextColor": "#FFFFFF",
    },
    "Storm": {
        "primaryColor": "#0284C7",      # Deep Blue
        "headerColor": "#38BDF8",       # Electric Blue
        "backgroundColor": "#111827",   # Dark Grey
        "textColor": "#F9FAFB",         # Pure White
        "buttonTextColor": "#FFFFFF",   
    },
    "Juggernaut": {
        "primaryColor": "#DC2626",      # Crimson
        "headerColor": "#FF4500",       # Orange Red
        "backgroundColor": "#1C0505",   # Dark Red/Brown
        "textColor": "#FFE4E6",         # Pale Rose
        "buttonTextColor": "#FFFFFF",
    }
}

def apply_theme(theme_name):
    theme = THEMES.get(theme_name, THEMES["Mystique (Default)"])
    
    css = f"""
    <style>
    /* --- 1. MAIN APP & TOP BAR COLORS --- */
    .stApp {{
        background-color: {theme['backgroundColor']};
        color: {theme['textColor']};
    }}
    
    /* THE TOP NAVIGATION BAR (The "Deploy" area) */
    header[data-testid="stHeader"] {{
        background-color: {theme['backgroundColor']} !important;
        border-bottom: 1px solid {theme['primaryColor']}; /* Optional: Adds a cool glowing line */
    }}
    
    /* The Hamburger Menu & Icons */
    header[data-testid="stHeader"] svg, 
    header[data-testid="stHeader"] button {{
        fill: {theme['headerColor']} !important;
        color: {theme['headerColor']} !important;
    }}
    
    /* --- 2. CONTENT HEADERS --- */
    h1, h2, h3, h4, h5, h6, 
    .stHeadingContainer, 
    span[data-testid="stHeader"] {{
        color: {theme['headerColor']} !important;
        font-weight: 800 !important;
        text-shadow: 0px 0px 1px rgba(0,0,0,0.5);
    }}
    
    /* --- 3. TEXT & LABELS --- */
    p, li, label, .stMarkdown, div.stText, span, div[data-testid="stMetricValue"] {{
        color: {theme['textColor']} !important;
    }}
    
    /* --- 4. BUTTONS --- */
    div.stButton > button, 
    div[data-testid="stFormSubmitButton"] > button {{
        background-color: {theme['primaryColor']} !important;
        color: {theme['buttonTextColor']} !important;
        border: 1px solid {theme['headerColor']} !important;
        font-weight: bold !important;
    }}
    div.stButton > button:hover {{
        filter: brightness(1.2);
        box-shadow: 0 0 10px {theme['primaryColor']};
    }}

    /* --- 5. THE IMPORT BACKUP BOX (File Uploader) --- */
    div[data-testid="stFileUploader"] section {{
        background-color: {theme['backgroundColor']} !important;
        border: 2px dashed {theme['primaryColor']} !important;
    }}
    div[data-testid="stFileUploader"] button {{
        background-color: {theme['primaryColor']} !important;
        color: {theme['buttonTextColor']} !important;
        border: none !important;
    }}
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] small {{
        color: {theme['textColor']} !important;
    }}
    label[data-testid="stWidgetLabel"] p {{
        color: {theme['headerColor']} !important;
        font-weight: bold !important;
    }}

    /* --- 6. SIDEBAR --- */
    section[data-testid="stSidebar"] {{
        background-color: {theme['backgroundColor']};
        border-right: 1px solid {theme['primaryColor']};
    }}
    
    /* --- 7. INPUTS & DROPDOWNS --- */
    .stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {{
        background-color: {theme['backgroundColor']} !important;
        color: {theme['textColor']} !important;
        border: 1px solid {theme['primaryColor']} !important;
    }}
    
    div[data-baseweb="popover"], div[data-baseweb="menu"] {{
        background-color: {theme['backgroundColor']} !important;
        border: 1px solid {theme['primaryColor']} !important;
    }}
    li[role="option"] {{
        color: {theme['textColor']} !important;
        background-color: {theme['backgroundColor']} !important;
    }}
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
        background-color: {theme['primaryColor']} !important;
        color: {theme['buttonTextColor']} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)