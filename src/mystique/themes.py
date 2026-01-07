import streamlit as st

THEMES = {
    "Mystique (Default)": {
        "primaryColor": "#4B0082",  # Indigo
        "backgroundColor": "#0E1117",
        "textColor": "#FAFAFA",
    },
    "Magneto (Red)": {
        "primaryColor": "#FF4B4B",
        "backgroundColor": "#262730",
        "textColor": "#FAFAFA",
    },
    "Cerebro (Blue)": {
        "primaryColor": "#00B4D8",
        "backgroundColor": "#FFFFFF",
        "textColor": "#31333F",
    },
}


def apply_theme(theme_name):
    """
    Injects CSS to override Streamlit variables visually.
    Note: Deep structural changes require .streamlit/config.toml edits.
    """
    theme = THEMES.get(theme_name, THEMES["Mystique (Default)"])

    css = f"""
    <style>
    /* Global Background */
    .stApp {{
        background-color: {theme["backgroundColor"]};
        color: {theme["textColor"]};
    }}
    /* Primary Buttons */
    div.stButton > button {{
        background-color: {theme["primaryColor"]};
        color: white;
        border: none;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
