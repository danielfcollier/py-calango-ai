import streamlit as st

THEMES = {
    "Calango (Default)": {
        "primaryColor": "#22c55e",
        "headerColor": "#4ade80",
        "backgroundColor": "#022c22",
        "textColor": "#ecfdf5",
        "buttonTextColor": "#000000",
    },
    "Ipê (Deep Purple)": {
        "primaryColor": "#8A2BE2",
        "headerColor": "#D8B4FE",
        "backgroundColor": "#0E1117",
        "textColor": "#E0E0E0",
        "buttonTextColor": "#FFFFFF",
    },
    "Girassol (Sunflower)": {
        "primaryColor": "#FACC15",
        "headerColor": "#FEF08A",
        "backgroundColor": "#1C1917",
        "textColor": "#F5F5F4",
        "buttonTextColor": "#1C1917",
    },
    "Boto (Pink)": {
        "primaryColor": "#D946EF",
        "headerColor": "#FF00FF",
        "backgroundColor": "#180818",
        "textColor": "#F3E8FF",
        "buttonTextColor": "#FFFFFF",
    },
    "Gralha (Blue)": {
        "primaryColor": "#0284C7",
        "headerColor": "#38BDF8",
        "backgroundColor": "#111827",
        "textColor": "#F9FAFB",
        "buttonTextColor": "#FFFFFF",
    },
    "Tiê (Red)": {
        "primaryColor": "#DC2626",
        "headerColor": "#FF4500",
        "backgroundColor": "#1C0505",
        "textColor": "#FFE4E6",
        "buttonTextColor": "#FFFFFF",
    },
}


def apply_theme(theme_name):
    if theme_name not in THEMES:
        theme_name = "Calango (Default)"

    theme = THEMES[theme_name]

    css = f"""
    <style>
    /* --- 1. MAIN APP & TOP BAR COLORS --- */
    .stApp {{
        background-color: {theme["backgroundColor"]};
        color: {theme["textColor"]};
    }}

    /* THE TOP NAVIGATION BAR */
    header[data-testid="stHeader"] {{
        background-color: {theme["backgroundColor"]} !important;
        border-bottom: 1px solid {theme["primaryColor"]};
    }}

    /* The Hamburger Menu & Icons */
    header[data-testid="stHeader"] svg,
    header[data-testid="stHeader"] button {{
        fill: {theme["headerColor"]} !important;
        color: {theme["headerColor"]} !important;
    }}

    /* --- 2. CONTENT HEADERS --- */
    h1, h2, h3, h4, h5, h6,
    .stHeadingContainer,
    span[data-testid="stHeader"] {{
        color: {theme["headerColor"]} !important;
        font-weight: 800 !important;
        text-shadow: 0px 0px 1px rgba(0,0,0,0.5);
    }}

    /* --- 3. TEXT & LABELS --- */
    p, li, label, .stMarkdown, div.stText, span, div[data-testid="stMetricValue"] {{
        color: {theme["textColor"]} !important;
    }}

    /* --- 4. BUTTONS --- */
    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {{
        background-color: {theme["primaryColor"]} !important;
        color: {theme["buttonTextColor"]} !important;
        border: 1px solid {theme["headerColor"]} !important;
        font-weight: bold !important;
    }}
    div.stButton > button:hover {{
        filter: brightness(1.2);
        box-shadow: 0 0 10px {theme["primaryColor"]};
    }}

    /* --- 5. THE IMPORT BACKUP BOX --- */
    div[data-testid="stFileUploader"] section {{
        background-color: {theme["backgroundColor"]} !important;
        border: 2px dashed {theme["primaryColor"]} !important;
    }}
    div[data-testid="stFileUploader"] button {{
        background-color: {theme["primaryColor"]} !important;
        color: {theme["buttonTextColor"]} !important;
        border: none !important;
    }}
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] small {{
        color: {theme["textColor"]} !important;
    }}
    label[data-testid="stWidgetLabel"] p {{
        color: {theme["headerColor"]} !important;
        font-weight: bold !important;
    }}

    /* --- 6. SIDEBAR --- */
    section[data-testid="stSidebar"] {{
        background-color: {theme["backgroundColor"]};
        border-right: 1px solid {theme["primaryColor"]};
    }}

    /* --- 7. INPUTS & DROPDOWNS --- */
    .stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {{
        background-color: {theme["backgroundColor"]} !important;
        color: {theme["textColor"]} !important;
        border: 1px solid {theme["primaryColor"]} !important;
    }}

    div[data-baseweb="popover"], div[data-baseweb="menu"] {{
        background-color: {theme["backgroundColor"]} !important;
        border: 1px solid {theme["primaryColor"]} !important;
    }}
    li[role="option"] {{
        color: {theme["textColor"]} !important;
        background-color: {theme["backgroundColor"]} !important;
    }}
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
        background-color: {theme["primaryColor"]} !important;
        color: {theme["buttonTextColor"]} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
