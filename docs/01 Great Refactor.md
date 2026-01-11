### 📋 Phase 1: The Great Refactor - Execution Plan

**Before you begin:**

1. Create a new folder: `src/calango/services/`.
2. Create a new folder: `tests/unit/` and `tests/e2e/`.
3. Ensure `__init__.py` exists in these new folders.

---

#### 🔹 Prompt 1: Modularization (Create Services)

*Copy and paste this into your AI coding assistant to create the business logic layer.*

> **Context:**
> I am refactoring a Streamlit application (`py-calango-ai`) to follow Domain-Driven Design principles. Currently, the business logic is mixed with the UI code.
> **Goal:**
> Create two new service classes in `src/calango/services/` that encapsulate the logic found in `src/ui/home.py` and `src/ui/rinha.py`.
> **Requirements:**
> 1. **Create `src/calango/services/chat_service.py**`:
> * Class `ChatService`.
> * **Dependency Injection**: The `__init__` method should accept `engine` (CalangoEngine) and `session_manager` (SessionManager).
> * **Methods**:
> * `get_messages(session_id)`: Wraps session manager logic.
> * `send_message(...)`: Handles the flow of adding a user message, calling the engine, and updating the history.
> * `calculate_usage(...)`: Move the token calculation logic here.
> 
> 
> 
> 
> 2. **Create `src/calango/services/arena_service.py**`:
> * Class `ArenaService`.
> * **Dependency Injection**: Accepts `engine`, `interaction_manager`, and a `persistence_adapter` (TinyDB instance).
> * **Methods**:
> * `run_battle_round(...)`: Logic to run a prompt against multiple models.
> * `save_round(...)`: Logic to persist results to TinyDB.
> * `calculate_usage(...)`: Same logic for token usage.
> 
> 
> 
> 
> 
> 
> **Files to Reference:**
> * `src/ui/home.py` (for chat logic)
> * `src/ui/rinha.py` (for battle logic)
> * `src/calango/core.py` (for engine signature)
> * `src/calango/database.py` (for DB managers)
> 
> 
> Please generate the code for `src/calango/services/chat_service.py` and `src/calango/services/arena_service.py`.

---

#### 🔹 Prompt 2: UI Cleanup (Implement Services)

*Once the services are created, use this prompt to clean up the UI files.*

> **Context:**
> We have created `ChatService` and `ArenaService` to handle business logic. Now we need to update the Streamlit UI files to use these services instead of calling the database and engine directly.
> **Goal:**
> Refactor `src/ui/home.py` and `src/ui/rinha.py`.
> **Requirements:**
> 1. **Refactor `src/ui/home.py**`:
> * Instantiate `ChatService` at the top.
> * Replace the manual message appending and `engine.run_chat` calls with `chat_service.send_message`.
> * Keep the Streamlit-specific code (widgets, session_state, `st.chat_message`) but delegate the data processing to the service.
> 
> 
> 2. **Refactor `src/ui/rinha.py**`:
> * Instantiate `ArenaService`.
> * Replace the complex loop for running battles with calls to `arena_service.run_battle_round`.
> * Ensure the "Friendly Error Message" logic for quotas is preserved (either in the UI or returned gracefully by the service).
> 
> 
> 3. **Refactor `src/app.py**`:
> * This is the entry point. Ensure any global initialization (like the Database or Engine) happens here and is passed down or accessible if necessary (though for Streamlit, initializing at the top of the UI files is acceptable for now).
> 
> 
> 
> 
> Please generate the updated code for `src/ui/home.py` and `src/ui/rinha.py`.

---

#### 🔹 Prompt 3: Unit Testing (Pytest)

*Now that logic is isolated, we can test it without running the UI.*

> **Context:**
> I need to add unit coverage for my new services in `src/calango/services/`.
> **Goal:**
> Create unit tests using `pytest` and `unittest.mock`.
> **Requirements:**
> 1. **Create `tests/unit/test_chat_service.py**`:
> * Mock `CalangoEngine` and `SessionManager`.
> * Test `send_message`: Verify it calls the engine and saves the result.
> * Test `calculate_usage`: Verify math is correct.
> 
> 
> 2. **Create `tests/unit/test_arena_service.py**`:
> * Mock the Engine and TinyDB.
> * Test `run_battle_round`: Verify it iterates through models and handles errors (like Quota Exceeded) if the service logic encapsulates that.
> 
> 
> 
> 
> Please generate the code for these two test files.

---

#### 🔹 Prompt 4: End-to-End Testing (Playwright)

*Finally, ensure the UI actually works for the user.*

> **Context:**
> The application uses Streamlit. I want to ensure the critical paths work using Playwright for Python.
> **Goal:**
> Create an E2E test file `tests/e2e/test_app_flow.py`.
> **Requirements:**
> 1. **Setup**:
> * Assume the app runs on `http://localhost:8501`.
> * Use `pytest-playwright`.
> 
> 
> 2. **Test Case 1: Chat Flow**:
> * Go to "Chats".
> * Type "Hello" in the input.
> * Click send.
> * Assert that a new message appears in the chat history.
> 
> 
> 3. **Test Case 2: Rinha Flow**:
> * Go to "A Rinha".
> * Select 2 fighters.
> * Type a prompt.
> * Assert that results appear for both fighters.
> 
> 
> 
> 
> Please generate the `tests/e2e/test_app_flow.py` file and provide the command to run it.