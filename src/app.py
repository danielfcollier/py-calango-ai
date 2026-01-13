import streamlit as st
from calango.database import ConfigManager
from calango.themes import apply_theme

st.set_page_config(page_title="Calango AI", page_icon="🦎", layout="wide")

try:
    db = ConfigManager()
    saved_theme = db.load_theme_setting()
    apply_theme(saved_theme)
except Exception as e:
    print(f"Theme load error: {e}")

home_page = st.Page("ui/home.py", title="Chats", icon="💬")
rinha_page = st.Page("ui/rinha.py", title="A Rinha", icon="🥊")
cuca_page = st.Page("ui/dashboard.py", title="A Cuca", icon="🧠")
settings_page = st.Page("ui/settings.py", title="Settings", icon="⚙️")

pg = st.navigation([home_page, rinha_page, cuca_page, settings_page])

# --- CSS: SIDEBAR LAYOUT & SUPPORT BUTTONS ---
st.markdown(
    """
    <style>
    /* Import Cookie Font for the 'Buy Me a Coffee' feel */
    @import url('https://fonts.googleapis.com/css2?family=Cookie&display=swap');

    /* Force sidebar content to use flex layout (pushes footer down) */
    section[data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .sidebar-spacer {
        flex-grow: 1;
    }

    /* --- SHARED BUTTON STYLES --- */
    .support-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 260px;
        margin: 8px auto; /* Centers the button */
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: 600; /* Default bold for normal buttons */
        transition: 0.3s ease;
        box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.2);
        gap: 10px; /* Space between icon and text */
        line-height: 1.2;
    }

    .support-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
        text-decoration: none !important;
        opacity: 0.95;
    }

    /* Icon styling */
    .btn-icon {
        width: 24px;
        height: 24px;
        fill: currentColor;
        flex-shrink: 0;
    }

    /* --- 1. LivePix / Pix Button (Green) --- */
    .livepix-btn {
        background-color: #32BCAD;
        color: #FFFFFF !important;
        border: 1px solid #289d90;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
    }

    /* --- 2. Buy Me A Coffee Button (Yellow + Cookie Font) --- */
    .bmc-btn {
        background-color: #FFDD00; /* Classic BMC Yellow */
        /* Changed color from black to coffee brown */
        color: #4b3621 !important;
        border: 1px solid transparent;

        /* Cookie Font settings */
        font-family: 'Cookie', cursive, sans-serif;
        font-size: 26px; /* Slightly larger for Cookie font readability */
        font-weight: 400 !important; /* Force normal weight */
        padding-top: 8px; /* Visual adjustment for cursive font baseline */
        padding-bottom: 8px;
    }

/* Force SVG color to match the new brown text in BMC */
    .bmc-btn .btn-icon {
        fill: #4b3621;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- EXECUTION ORDER ---
pg.run()
# ---------------------

# --- GLOBAL SIDEBAR FOOTER ---
with st.sidebar:
    st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
    st.markdown("---")

    livepix_url = "https://livepix.gg/danielcollier"
    bmc_url = "https://www.buymeacoffee.com/danielcollier"

    # --- BRAZILIAN SUPPORT ---
    st.caption("🇧🇷 Suporte Brasileiro")
    st.markdown(
        f"""
        <div style="margin-bottom: 15px;">
            <a href="{livepix_url}" target="_blank" class="support-btn livepix-btn">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.216 6.415l-.132-.666c-.119-.596-.385-1.162-1.008-1.528-.485-.285-1.162-.485-1.956
                    -.566l-.666-.076C16.326 3.52 16.208 2 13.91 2H6.946c-2.617 0-4.632 2.13-4.632 4.743l.235 7.373c.175
                     4.39 3.73 7.857 8.136 7.857h.03c4.405 0 8.018-3.525 8.163-7.935.615-.17 1.637-.626 2.053-2.025.267
                    -.9.17-1.885-.715-2.6zm-2.585 3.24c-.167.562-.63.856-1.15.912l-.18.02c-.13.013-.26.014-.386.002l.147
                     -4.613c.805.08 1.157.29 1.258.35.213.124.305.318.346.522.04.204.09.845-.035 2.807z"/>
                </svg>
                <span>Um café PIX</span>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- INTERNATIONAL SUPPORT ---
    st.caption("🌍 International Support")
    st.markdown(
        f"""
        <div style="margin-bottom: 15px;">
            <a href="{bmc_url}" target="_blank" class="support-btn bmc-btn">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.216 6.415l-.132-.666c-.119-.596-.385-1.162-1.008-1.528-.485-.285-1.162-.485
                    -1.956-.566l-.666-.076C16.326 3.52 16.208 2 13.91 2H6.946c-2.617 0-4.632 2.13-4.632
                     4.743l.235 7.373c.175 4.39 3.73 7.857 8.136 7.857h.03c4.405 0 8.018-3.525 8.163-7.935.615
                     -.17 1.637-.626 2.053-2.025.267-.9.17-1.885-.715-2.6zm-2.585 3.24c-.167.562-.63.856-1.15.912l
                     -.18.02c-.13.013-.26.014-.386.002l.147-4.613c.805.08
                      1.157.29 1.258.35.213.124.305.318.346.522.04.204.09.845-.035 2.807z"/>
                </svg>
                <div style="color: currentColor">Buy me a coffee</div>
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.8em; margin-top: 20px;">
            <b>Calango AI</b> v1.0<br/>
            <i>Agile & Adaptable</i>
            <br/>
                Created by
                <a href="https://github.com/danielfcollier" style="color: #666; text-decoration: none;">
                    Daniel Collier
                </a>
            <br/>
            © 2026 All Rights Reserved
        </div>
        """,
        unsafe_allow_html=True,
    )
