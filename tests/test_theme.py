from unittest.mock import patch

from calango.themes import THEMES, apply_theme


@patch("streamlit.markdown")
def test_apply_existing_theme(mock_markdown):
    """Test applying a valid theme."""
    theme_name = list(THEMES.keys())[0]  # Pick the first available theme

    apply_theme(theme_name)

    # Ensure st.markdown was called (to inject CSS)
    mock_markdown.assert_called()

    # Check if the CSS contains the primary color of that theme
    injected_css = mock_markdown.call_args[0][0]
    expected_color = THEMES[theme_name]["primaryColor"]
    assert expected_color in injected_css


@patch("streamlit.markdown")
def test_apply_invalid_theme_fallback(mock_markdown):
    """Test that invalid theme names fall back to default."""
    apply_theme("NonExistentTheme")

    mock_markdown.assert_called()
