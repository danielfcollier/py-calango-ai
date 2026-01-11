# 🗺️ The Strategic Roadmap

## 🏗️ Phase 1: The Great Refactor (Foundation)

**Goal:** Decouple the UI from the Business Logic to enable testing and future growth.

* **1.1 Modularize Architecture:**
* Create a `src/services/` directory.
* Extract logic from `src/ui/home.py` → `src/services/chat_service.py`.
* Extract logic from `src/ui/rinha.py` → `src/services/arena_service.py`.
* Ensure UI files (`ui/*.py`) **only** handle Streamlit rendering, not database calls or LLM logic.


* **1.2 Dependency Injection:**
* Refactor `CalangoEngine` and `InteractionManager` to be passed into services (e.g., `ChatService(db=db, engine=engine)`). This is critical for Phase 4.


* **1.3 comprehensive Testing:**
* **Unit Tests:** Add `pytest` for `src/calango/core.py` and the new services.
* **Integration Tests:** Test the full flow of "User Prompt -> Engine -> Response".
* **E2E Tests:** Implement **Playwright** to verify the Streamlit UI works (e.g., clicking "Nova Conversa" actually clears the chat).



## 🌍 Phase 2: Globalization (i18n)

**Goal:** Make Calango accessible to English and Portuguese speakers immediately.

* **2.1 Translation Engine:**
* Create a simple JSON-based locale system: `src/locales/en.json` and `src/locales/pt_br.json`.
* Implement a helper function `t(key)` that reads the current language from `st.session_state`.


* **2.2 UI Integration:**
* Replace all hardcoded strings (e.g., `"🦎 A Cuca (The Brain)"`) with dynamic calls like `t("dashboard.title")`.
* Add a **Language Toggle** (🇧🇷/🇺🇸) in the Sidebar/Settings.



## 🧠 Phase 3: Local RAG (Knowledge Base)

**Goal:** Give Calango "Long-Term Memory" using a local Vector Database.

* **3.1 Qdrant Integration:**
* Add `qdrant-client` to dependencies.
* Implement `src/services/vector_service.py` to handle `upsert` (save) and `search` (retrieve) operations.


* **3.2 Ingestion Pipeline:**
* Create a **"Knowledge" Page** in the UI to upload PDFs/Text files.
* Implement **Chunking** (splitting text into pieces) and **Embedding** (converting text to numbers using a lightweight model like `all-MiniLM-L6-v2` or OpenAI embeddings).


* **3.3 Augmented Generation:**
* Update `CalangoEngine.run_chat` to accept a `context` parameter.
* Before answering, search Qdrant for relevant chunks and inject them into the System Prompt.



## 🗄️ Phase 4: Multi-Database Support (SQLAlchemy)

**Goal:** Move off TinyDB to support heavy concurrent usage and complex queries.

* **4.1 ORM Definition:**
* Introduce **SQLAlchemy**. Define models: `User`, `Session`, `Message`, `Log`.
* Implement the **Repository Pattern** to separate SQL queries from the Service layer.


* **4.2 Dual-Mode Engine:**
* Configure `src/calango/database.py` to switch modes based on an environment variable (`CALANGO_MODE`):
* `DESKTOP`: Uses **SQLite** (local file).
* `SERVER`: Uses **PostgreSQL** (production DB).




* **4.3 Migration System:**
* Set up **Alembic** to manage database schema changes automatically.



## ⚡ Phase 5: Async Chat & Queueing

**Goal:** Prevent the UI from freezing during heavy tasks (like 4-model Rinha battles).

* **5.1 Async Engine:**
* Refactor `CalangoEngine` methods to be `async def`.
* Update Streamlit calls to use `asyncio.run()` or proper async wrappers where supported.


* **5.2 Task Queue:**
* Offload heavy tasks (e.g., ingesting a 100-page PDF for RAG, or running a 10-round Rinha) to a background worker.
* Use a lightweight queue (like standard `asyncio` tasks for Desktop, or Celery/Redis for Server).



## 🔐 Phase 6: Identity & Control

**Goal:** Secure the application for multi-user environments.

* **6.1 Authentication Layer:**
* **Desktop:** Simple "Local User" profile (no password needed, just identity).
* **Server:** Implement **Streamlit Authenticator** (hashed passwords) or OAuth (Google/GitHub Login).


* **6.2 User Quotas:**
* Add `token_balance` to the `User` model.
* Implement a **Quota Guard** in the `ChatService`: check balance before generation -> deduct cost after generation.



## 🔭 Phase 7: Observability & Tracing

**Goal:** Professional-grade monitoring to debug "why did the AI say that?"

* **7.1 Tracing Integration:**
* Integrate **Langfuse** (self-hosted or cloud).
* Wrap the `CalangoEngine` generation step to log: Input Prompt, Retrieved Context (from RAG), Model Used, Latency, and Cost.


* **7.2 Feedback Loop:**
* Add "👍 / 👎" buttons to chat messages.
* Log this feedback to the observability platform to improve future prompts.
