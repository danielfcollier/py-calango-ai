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

# Inject CSS to push buttons to bottom
st.markdown(
    """
    <style>
    /* Force sidebar content to use flex layout */
    section[data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    /* Push the spacer div to fill remaining space */
    .sidebar-spacer {
        flex-grow: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    # This spacer will be pushed by the content below
    st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)

    st.markdown("---")

    livepix_url = "https://livepix.gg/danielcollier"
    bmc_url = "https://www.buymeacoffee.com/danielcollier"

    st.caption("🇧🇷 Suporte Brasileiro")
    st.markdown(
        f"""
        <a href="{livepix_url}" target="_blank" style="text-decoration: none; display: block; text-align: center;">
            <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
                 alt="Me dê um café"
                 style="width: 100%; max-width: 217px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    st.caption("🌍 International Support")
    st.markdown(
        f"""
        <a href="{bmc_url}" target="_blank" style="text-decoration: none; display: block; text-align: center;">
            <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png"
                 alt="Buy Me A Coffee"
                 style="width: 100%; max-width: 217px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.8em; margin-top: 30px;">
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

pg.run()
