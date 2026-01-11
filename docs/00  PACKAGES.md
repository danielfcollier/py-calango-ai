# 📦 Recommended Tooling

To support the **Calango AI** roadmap (Refactor, Async Rinha, RAG), these packages are highly recommended additions to the stack.

## 1. Tenacity (Resilience)
**Why:** The "Rinha" (Phase 5) and RAG (Phase 3) rely on external APIs and complex pipelines that *will* fail occasionally. Standard `try/except` blocks create messy code.
* **Use Case:** Automatically retry a failed model generation or a database lock error with exponential backoff.
* **Fit:** Decorate critical methods like `@retry(stop=stop_after_attempt(3))` to make the application robust without polluting the logic.

## 2. Loguru (Logging)
**Why:** As the app moves to an Async/Threaded architecture (Desktop App), debugging via `print()` becomes impossible.
* **Use Case:** Replace all `print()` calls. Loguru handles file rotation (saving logs to `~/.calango/logs/`) so you can debug user issues remotely.
* **Fit:** Supports structured JSON logging out-of-the-box, which is essential for the **Observability (Phase 7)** integration with Langfuse.

## 3. Streamlit-Extras (UI Polish)
**Why:** Streamlit's core widgets are limited. This library adds the "missing" components for a professional feel.
* **Use Case:**
    * **Badges:** Display tags like "Reasoning" or "Fast" next to models in the Rinha.
    * **Stateful Button:** Prevent the UI from resetting when clicking "Ingest PDF".
    * **Toggle:** A cleaner switch for "Server Mode" vs "Desktop Mode".

## 4. Faker (Testing Data)
**Why:** Phase 1 (Testing) and Phase 6 (Identity) require realistic test data. Manually creating users and chat sessions is inefficient.
* **Use Case:** Generate 100 fake users, persona names, and chat histories to test performance and pagination.
* **Fit:** Crucial for `pytest` fixtures and E2E testing with Playwright.
