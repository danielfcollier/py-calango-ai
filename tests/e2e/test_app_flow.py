import os
import pytest
from playwright.sync_api import Page, expect

# Apply marker for easy filtering: make test-e2e
pytestmark = pytest.mark.e2e

# Constants
BASE_URL = "http://localhost:8501"

@pytest.fixture(scope="session", autouse=True)
def mock_db_env(tmp_path_factory):
    """
    Priority: 
    1. Use existing CALANGO_HOME (set in CI)
    2. Fallback to a temporary directory (for local testing)
    """
    if "CALANGO_HOME" in os.environ:
        return os.environ["CALANGO_HOME"]
        
    tmp_dir = tmp_path_factory.mktemp("calango_test_home")
    os.environ["CALANGO_HOME"] = str(tmp_dir)
    return tmp_dir

@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """Go to the base URL before each test."""
    page.goto(BASE_URL)

def test_chat_flow(page: Page):
    """
    Test Case 1: Chat Flow
    - Navigate to 'Chats'
    - Send a message and verify response
    """
    # 1. Navigate to Chats
    page.get_by_test_id("stSidebarNav").get_by_text("Chats").click()
    expect(page.get_by_text("Calango AI 🦎")).to_be_visible()

    # 2. Send message
    chat_input = page.get_by_test_id("stChatInputTextArea")
    chat_input.fill("Hello")
    chat_input.press("Enter")

    # 3. Assert User message and Assistant response exist
    expect(page.get_by_test_id("stChatMessage").filter(has_text="Hello")).to_be_visible()
    # Wait for the total count to reach 2 (User + Assistant)
    expect(page.get_by_test_id("stChatMessage")).to_have_count(2, timeout=20000)

def test_rinha_flow(page: Page):
    """
    Test Case 2: Rinha Flow
    - Navigate to 'A Rinha'
    - Reset state and ensure 2 fighters
    - Verify results and token stats
    """
    # 1. Navigate to A Rinha
    page.get_by_test_id("stSidebarNav").get_by_text("A Rinha").click()
    expect(page.get_by_text("🥊 A Rinha (The Arena)")).to_be_visible()
    
    # 2. Clear previous history to ensure a predictable message count
    page.get_by_role("button", name="Limpar Rinha").click()
    
    # 3. Adjust Slider (Matches the label in src/ui/rinha.py: 'Número de Lutadores')
    slider = page.get_by_label("Número de Lutadores")
    if slider.is_visible():
        slider.click()  # Focus the slider
        # Default is 2 in code, but if it was 4, move left to ensure 2 fighters
        page.keyboard.press("ArrowLeft")
        page.keyboard.press("ArrowLeft")
        page.wait_for_timeout(1000)

    # 4. Send challenge
    prompt_text = "Compare Python vs Javascript in one sentence."
    challenge_input = page.get_by_test_id("stChatInputTextArea")
    challenge_input.fill(prompt_text)
    challenge_input.press("Enter")

    # 5. Verify results
    # We expect 3 chat messages: 1 User prompt + 2 Model responses
    expect(page.get_by_test_id("stChatMessage")).to_have_count(3, timeout=45000)
    
    # Check that the model responses were generated (checks for text presence)
    expect(page.get_by_test_id("stChatMessage").filter(has_text=prompt_text)).to_be_visible()

    # 6. Verify token stats (rendered as st.success/stNotification)
    # It only renders AFTER the LLM stream is finished.
    notifications = page.get_by_test_id("stNotification")
    expect(notifications.first).to_be_visible(timeout=45000)
    expect(notifications).to_have_count(2, timeout=10000)