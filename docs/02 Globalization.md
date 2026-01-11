### 🌍 Phase 2: Globalization (i18n) - Execution Plan

**Before you begin:**

1. Create a new folder: `src/locales/`.
2. Ensure you have your refactored code from Phase 1 ready.

---

#### 🔹 Prompt 1: The Translation Engine & Extraction

*First, we need to extract all hardcoded strings and build the translation infrastructure.*

> **Context:**
> I am adding Internationalization (i18n) to my Streamlit app. Currently, all text is hardcoded in English/Portuguese mix within the UI files.
> **Goal:**
> 1. Create a dictionary of all text strings found in `src/ui/home.py`, `src/ui/rinha.py`, `src/ui/dashboard.py`, and `src/ui/settings.py`.
> 2. Create two JSON files: `src/locales/en.json` (English) and `src/locales/pt_br.json` (Portuguese).
> 3. Create a helper class `src/calango/services/i18n.py` to load these files.
> 
> 
> **Requirements:**
> * **JSON Structure:** Use nested keys for organization. Example:
> ```json
> {
>   "sidebar": {
>     "config_header": "Configuration",
>     "provider_label": "Provider"
>   },
>   "dashboard": { ... },
>   "rinha": { ... }
> }
> 
> ```
> 
> 
> * **`TranslationService` Class:**
> * Method `load_locales(path)`: Loads both JSONs into memory.
> * Method `t(key, lang='en')`: Returns the translated string. Supports dot notation (e.g., `t("sidebar.config_header")`). Returns the key itself if missing.
> 
> 
> 
> 
> **Files to Analyze for Strings:**
> * `src/ui/home.py`
> * `src/ui/rinha.py`
> * `src/ui/dashboard.py`
> * `src/ui/settings.py`
> * `src/app.py` (Sidebar footer)
> 
> 
> Please generate the content for `src/locales/en.json`, `src/locales/pt_br.json`, and `src/calango/services/i18n.py`.

---

#### 🔹 Prompt 2: Persistence & State Management

*Now we need to save the user's language preference in the database.*

> **Context:**
> I have a `TranslationService`. Now I need to persist the user's language choice (defaulting to 'en') using my existing TinyDB configuration.
> **Goal:**
> Update `src/calango/database.py` and create a Streamlit helper.
> **Requirements:**
> 1. **Update `ConfigManager` (in `database.py`)**:
> * Add `load_language_setting()`: Returns 'en' or 'pt_br'.
> * Add `save_language_setting(lang_code)`: Updates the 'settings' table.
> 
> 
> 2. **Create `src/calango/utils/streamlit_i18n.py**`:
> * Create a function `init_i18n()`:
> * Instantiates `TranslationService`.
> * Loads the language from `ConfigManager` into `st.session_state['language']`.
> * Injects a `t(key)` function into `st.session_state` that automatically uses the current language.
> 
> 
> 
> 
> 
> 
> Please generate the updated `src/calango/database.py` and the new `src/calango/utils/streamlit_i18n.py`.

---

#### 🔹 Prompt 3: UI Implementation & Switcher

*Finally, apply the translations to the frontend.*

> **Context:**
> I have the JSON locales and the `t()` helper function. I need to refactor the UI to use them and add a language selector.
> **Goal:**
> Refactor the UI files and add a Language Switcher in Settings.
> **Requirements:**
> 1. **Refactor `src/ui/settings.py**`:
> * Add a new Selectbox for "Language" (English / Português) in the "Appearance" (Camuflagem) tab.
> * When changed, call `db.save_language_setting` and `st.rerun()`.
> * Replace all hardcoded strings with `st.session_state.t("key")`.
> 
> 
> 2. **Refactor `src/ui/home.py`, `rinha.py`, `dashboard.py**`:
> * Initialize i18n at the top: `from calango.utils.streamlit_i18n import init_i18n; init_i18n()`.
> * Replace all strings (titles, buttons, warnings, captions) with `t(...)` calls corresponding to the JSON keys generated in Prompt 1.
> 
> 
> 
> 
> Please generate the updated code for `src/ui/settings.py` and `src/ui/home.py` as examples of how to apply this pattern.