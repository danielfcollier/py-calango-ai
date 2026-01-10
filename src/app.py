import streamlit as st
from calango.database import ConfigManager
from calango.themes import apply_theme
import streamlit.components.v1 as components

st.set_page_config(page_title="Calango AI", page_icon="🦎", layout="wide")

try:
    db = ConfigManager()
    saved_theme = db.load_theme_setting()
    apply_theme(saved_theme)
except Exception as e:
    print(f"Theme load error: {e}")

home_page = st.Page("ui/home.py", title="Chat", icon="💬")
rinha_page = st.Page("ui/rinha.py", title="A Rinha", icon="🥊")
cuca_page = st.Page("ui/dashboard.py", title="A Cuca", icon="🧠")
settings_page = st.Page("ui/settings.py", title="Settings", icon="⚙️")

pg = st.navigation([home_page, rinha_page, cuca_page, settings_page])

with st.sidebar:
    st.markdown("---")

    # URLs
    livepix_url = "https://livepix.gg/danielcollier"
    bmc_url = "https://www.buymeacoffee.com/danielcollier"

    # --- 1. BRAZILIAN BUTTON (LivePix) ---
    st.caption("🇧🇷 Suporte Brasileiro")

    # We use the BMC API but with Portuguese text: "Me dê um café"
    # URL Encoded: Me%20d%C3%AA%20um%20caf%C3%A9
    st.markdown(
        f"""
        <a href="{livepix_url}" target="_blank" style="text-decoration: none; display: block; text-align: center;">
            <img src="https://img.buymeacoffee.com/button-api/?text=Me%20d%C3%AA%20um%20caf%C3%A9&emoji=☕&slug=danielcollier&button_colour=5F4B32&font_colour=ffffff&font_family=Cookie&outline_colour=ffffff&coffee_colour=FFDD00" 
                 alt="Me dê um café" 
                 style="width: 100%; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.write("")  # Spacer

    # --- 2. INTERNATIONAL BUTTON (Coffee) ---
    st.caption("🌍 International Support")

    # Standalone HTML block for Coffee (Brown Button)
    st.markdown(
        f"""
        <a href="{bmc_url}" target="_blank" style="text-decoration: none; display: block; text-align: center;">
            <img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=☕&slug=danielcollier&button_colour=5F4B32&font_colour=ffffff&font_family=Cookie&outline_colour=ffffff&coffee_colour=FFDD00" 
                 alt="Buy Me A Coffee" 
                 style="width: 100%; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
        </a>
        """,
        unsafe_allow_html=True,
    )

    # CREDITS
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.8em; margin-top: 30px;">
            <b>Calango AI</b> v1.0<br/>
            <i>Agile & Adaptable</i><br/>
            Created by <a href="https://github.com/danielfcollier" style="color: #666; text-decoration: none;">Daniel Collier</a><br/>
            © 2026 All Rights Reserved
        </div>
        """,
        unsafe_allow_html=True,
    )

pg.run()
