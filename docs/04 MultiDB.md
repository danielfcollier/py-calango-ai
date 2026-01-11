Here are the **4 Strategic Prompts** to execute Phase 4 (Multi-Database with SQLAlchemy).

### 🗄️ Phase 4: Multi-Database Support - Execution Plan

**Before you begin:**

1. Run `pip install sqlalchemy psycopg2-binary alembic python-dotenv`.
2. Create a folder `src/calango/db/`.

---

#### 🔹 Prompt 1: The Data Models (ORM)

*First, we define the structure of our data using SQLAlchemy.*

> **Context:**
> I am migrating my application from TinyDB to SQLAlchemy to support both SQLite (Desktop mode) and PostgreSQL (Server mode).
> **Goal:**
> Create the database connection logic and ORM models in `src/calango/db/`.
> **Requirements:**
> 1. **Create `src/calango/db/engine.py**`:
> * Function `get_engine()`: Checks `os.getenv("CALANGO_MODE", "DESKTOP")`.
> * If `DESKTOP`: Returns engine for `sqlite:///calango.db` (ensure it uses the app directory path defined in `src/calango/database.py`).
> * If `SERVER`: Returns engine for `os.getenv("DATABASE_URL")` (Postgres).
> 
> 
> * Create a `SessionLocal` factory.
> 
> 
> 2. **Create `src/calango/db/models.py**`:
> * **Base**: `DeclarativeBase`.
> * **Model `Provider**`: `id`, `name` (unique), `api_key` (encrypted if possible, or plain text for now), `models` (store as JSON or comma-separated string).
> * **Model `Persona**`: `id`, `name` (unique), `prompt`.
> * **Model `ChatSession**`: `id` (UUID), `title`, `created_at`.
> * **Model `ChatMessage**`: `id`, `session_id` (FK), `role` (user/assistant), `content`, `timestamp`, `model`, `provider`, `persona`, `token_usage` (JSON), `cost` (Float).
> * **Model `Setting**`: `key` (PK), `value` (JSON or String) - for Theme/Language.
> 
> 
> 
> 
> Please generate the code for `src/calango/db/engine.py` and `src/calango/db/models.py`.

---

#### 🔹 Prompt 2: The Repository Pattern

*Now we implement the logic to access these models, replacing the direct TinyDB calls.*

> **Context:**
> I have the SQLAlchemy models. Now I need Repositories to handle CRUD operations. These will eventually replace the Managers in `src/calango/database.py`.
> **Goal:**
> Create repository classes in `src/calango/db/repositories.py`.
> **Requirements:**
> 1. **`ProviderRepository`**: `get_by_name`, `upsert` (if name exists update, else insert).
> 2. **`PersonaRepository`**: `get_all`, `get_by_name`, `create`, `delete`.
> 3. **`SessionRepository`**: `create_session`, `get_all` (sorted desc), `update_title`, `delete`.
> 4. **`MessageRepository`**:
> * `add_message(session_id, role, content, meta_info)`: Saves a message.
> * `get_by_session(session_id)`: Returns list of messages.
> 
> 
> 5. **`SettingsRepository`**: `get_theme`, `save_theme`, `get_language`, `save_language`.
> 
> 
> **Note:** All methods should accept a DB Session object or manage their own `with SessionLocal() as db:` context.
> Please generate `src/calango/db/repositories.py`.

---

#### 🔹 Prompt 3: The Swap (Adapter Integration)

*We modify the existing `database.py` to use the new SQL repositories while keeping the method signatures compatible with the rest of the app.*

> **Context:**
> I have the new SQL Repositories. Currently, `src/calango/database.py` uses TinyDB directly in classes like `ConfigManager`, `SessionManager`, etc.
> **Goal:**
> Refactor `src/calango/database.py` to act as an Adapter that delegates to the SQL Repositories.
> **Requirements:**
> 1. **Imports**: Import `get_engine`, `SessionLocal`, and the repositories from `src/calango/db/`.
> 2. **`ConfigManager`**:
> * Init: `self.repo = SettingsRepository(SessionLocal())`.
> * Methods: Delegate `load_theme_setting` -> `repo.get_theme`.
> 
> 
> 3. **`PersonaManager`**: Delegate to `PersonaRepository`.
> 4. **`SessionManager`**: Delegate to `SessionRepository` and `MessageRepository`.
> * **Critical**: Ensure `get_messages` returns the dictionary structure expected by the UI (e.g., `{"role": "user", "content": "..."}`), converting from the SQLAlchemy model if necessary.
> 
> 
> 5. **`InteractionManager`**: Delegate logging to `MessageRepository`.
> 
> 
> Please generate the updated `src/calango/database.py` file.

---

#### 🔹 Prompt 4: Migrations (Alembic)

*Finally, we set up the tool that will create the tables in your database.*

> **Context:**
> I have set up SQLAlchemy models. I need to initialize the database schema using Alembic.
> **Goal:**
> Provide the steps and `alembic.ini` configuration instructions.
> **Requirements:**
> 1. Tell me how to run `alembic init alembic`.
> 2. Provide the code to update `alembic/env.py`:
> * It needs to import my `Base` from `src/calango/db/models.py`.
> * It needs to set `target_metadata = Base.metadata`.
> * It needs to load the DB URL from `src/calango/db/engine.py` or environment variables.
> 
> 
> 3. Provide the command to generate the first migration (`alembic revision --autogenerate`) and apply it (`alembic upgrade head`).
> 
> 
> Please generate the instructions and the code snippet for `alembic/env.py`.