# src/calango/themes.py

import json

import streamlit.components.v1 as components

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

    header[data-testid="stHeader"] {{
        background-color: {theme["backgroundColor"]} !important;
        border-bottom: 1px solid {theme["primaryColor"]};
    }}

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
    p, li, label, div.stText, span, div[data-testid="stMetricValue"], .stMarkdown p, .stMarkdown li {{
        color: {theme["textColor"]} !important;
    }}

    /* --- 4. BUTTONS & POPOVERS --- */
    /* General Buttons (Secondary) */
    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button,
    button[data-testid="stPopoverButton"] {{
        background-color: {theme["primaryColor"]} !important;
        color: {theme["buttonTextColor"]} !important;
        border: 1px solid {theme["headerColor"]} !important;
        font-weight: bold !important;
    }}

    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    button[data-testid="stPopoverButton"]:hover {{
        filter: brightness(1.2);
        box-shadow: 0 0 10px {theme["primaryColor"]};
        color: {theme["buttonTextColor"]} !important;
        border: 1px solid {theme["headerColor"]} !important;
    }}

    /* Popover Internals */
    button[data-testid="stPopoverButton"] div,
    button[data-testid="stPopoverButton"] p,
    button[data-testid="stPopoverButton"] span,
    button[data-testid="stPopoverButton"] svg {{
        color: {theme["buttonTextColor"]} !important;
        fill: {theme["buttonTextColor"]} !important;
    }}

    /* --- SPECIAL: PRIMARY BUTTONS (DELETE) --- */
    /* Forces RED background and WHITE text/icon for any Primary button (like Delete) */
    div.stButton > button[kind="primary"] {{
        background-color: #EF4444 !important; /* Bright Red */
        color: #FFFFFF !important;            /* White Text */
        border: 1px solid #B91C1C !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background-color: #DC2626 !important; /* Darker Red on Hover */
        box-shadow: 0 0 8px #EF4444 !important;
        color: #FFFFFF !important;
    }}
    /* Ensure the Icon inside inherits the white color */
    div.stButton > button[kind="primary"] span[data-testid="stIconMaterial"],
    div.stButton > button[kind="primary"] svg {{
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }}


    /* --- 5. THE IMPORT BACKUP BOX (FILE UPLOADER) --- */
    [data-testid="stFileUploader"] section {{
        background-color: {theme["backgroundColor"]} !important;
        border: 2px dashed {theme["primaryColor"]} !important;
        color: {theme["textColor"]} !important;
    }}
    [data-testid="stFileUploaderDropzone"] {{
        background-color: {theme["backgroundColor"]} !important;
    }}
    [data-testid="stFileUploader"] button {{
        background-color: {theme["primaryColor"]} !important;
        color: {theme["buttonTextColor"]} !important;
        border: 1px solid {theme["headerColor"]} !important;
    }}
    [data-testid="stFileUploader"] label p {{
        color: {theme["headerColor"]} !important;
    }}
    [data-testid="stFileUploader"] svg {{
        fill: {theme["primaryColor"]} !important;
    }}
    [data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span {{
        color: {theme["textColor"]} !important;
    }}

    /* --- 6. CODE BLOCKS --- */
    code {{
        background-color: #1e1e1e !important;
        color: #4ade80 !important;
        padding: 0.2em 0.4em !important;
        border-radius: 4px !important;
    }}
    pre {{
        background-color: #1e1e1e !important;
        border: 1px solid {theme["primaryColor"]} !important;
        border-radius: 8px !important;
        padding: 1em !important;
    }}
    pre code {{
        background-color: transparent !important;
        color: inherit !important;
        padding: 0 !important;
    }}
    .stMarkdown span {{
        color: inherit;
    }}

    /* --- 7. SIDEBAR --- */
    section[data-testid="stSidebar"] {{
        background-color: {theme["backgroundColor"]};
        border-right: 1px solid {theme["primaryColor"]};
    }}

    /* --- 8. INPUTS & DROPDOWNS --- */
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

    /* --- 9. EXPANDERS (Rinha Config) --- */
    div[data-testid="stExpander"] details {{
        background-color: {theme["backgroundColor"]} !important;
        border: 1px solid {theme["primaryColor"]} !important;
        color: {theme["textColor"]} !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stExpander"] details > summary {{
        background-color: {theme["primaryColor"]} !important;
        color: {theme["buttonTextColor"]} !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stExpander"] details > summary:hover {{
        filter: brightness(1.2) !important;
        color: {theme["buttonTextColor"]} !important;
    }}
    div[data-testid="stExpander"] details > summary svg,
    div[data-testid="stExpander"] details > summary p,
    div[data-testid="stExpander"] details > summary span {{
        color: {theme["buttonTextColor"]} !important;
        fill: {theme["buttonTextColor"]} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# --- NON-NATIVE COMPONENT: JS COPY BUTTON ---
def render_copy_button(text, theme_name="Calango (Default)"):
    if theme_name not in THEMES:
        theme_name = "Calango (Default)"

    theme = THEMES[theme_name]
    primary = theme["primaryColor"]
    btn_text = theme["buttonTextColor"]

    safe_text = json.dumps(text)

    html_code = f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0; padding: 0;
            background-color: transparent;
            font-family: sans-serif;
            display: flex; align-items: center;
        }}
        .copy-btn {{
            background-color: transparent;
            color: {primary};
            border: 1px solid {primary};
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 14px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
            display: flex; align-items: center; gap: 6px;
        }}
        .copy-btn:hover {{
            background-color: {primary};
            color: {btn_text};
        }}
        .copy-btn:active {{
            transform: scale(0.96);
        }}
    </style>
    <script>
    function copyToClipboard() {{
        navigator.clipboard.writeText({safe_text}).then(function() {{
            const btn = document.getElementById("btn");
            btn.innerHTML = "✅ Copiado!";
            setTimeout(() => {{ btn.innerHTML = "📄 Copiar Resposta"; }}, 2000);
        }}, function(err) {{
            console.error('Copy failed: ', err);
        }});
    }}
    </script>
    </head>
    <body>
        <button id="btn" class="copy-btn" onclick="copyToClipboard()">
            📄 Copiar Resposta
        </button>
    </body>
    </html>
    """
    components.html(html_code, height=45)
