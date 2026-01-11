# Contributing to Calango AI 🦎

First off, thank you for considering contributing to Calango AI! It's people like you that make open source tools great.

Whether you're fixing a bug, adding a new Brazilian theme, or improving the documentation, we welcome your help.

## 🛠️ Tech Stack

Before you start, here is what we use under the hood:
* **Language:** Python 3.12+
* **Framework:** Streamlit
* **LLM Orchestration:** LiteLLM
* **Database:** TinyDB (Local JSON)
* **Package Manager:** `uv` (Fast Python package installer)
* **Linting/Formatting:** Ruff & Mypy

## ⚡ Getting Started

### 1. Fork & Clone
Fork this repository to your own GitHub account and then clone it to your local machine:

```bash
git clone https://github.com/danielfcollier/py-calango-ai.git
cd py-calango-ai
```

### 2. Set Up Environment

We use `uv` for lightning-fast dependency management, but standard `pip` works too. We have a `Makefile` to automate this.

```bash
# Installs dependencies and creates a virtual environment (.venv)
make install
```

### 3. Run the App

To start the development server:

```bash
make run
```

The app should open automatically at `http://localhost:8501`.

## 🧪 Development Workflow

### Code Quality

We enforce strict linting and formatting to keep the code clean. Before submitting a Pull Request, please run:

```bash
# Formats your code (Ruff)
make format

# Runs type checks and linter (MyPy & Ruff)
make lint
```

### Building the Executable

If you are working on the desktop binary build process:

```bash
# Builds the .exe (Windows) or binary (Mac/Linux) using PyInstaller
make build
```

The output will be in the `dist/` folder.

## 📂 Project Structure

* **`src/app.py`**: The main entry point and navigation logic.
* **`src/calango/`**: Core logic.
  * `core.py`: LLM interaction logic (LiteLLM wrapper).
  * `database.py`: TinyDB handling (History, Configs, Personas).
  * `themes.py`: The color palettes and CSS injection.

* **`src/ui/`**: Streamlit pages.
  * `home.py`: The main Chat interface.
  * `rinha.py`: The "Danger Room" (Model Comparison).
  * `dashboard.py`: "A Cuca" (Analytics).
  * `settings.py`: "A Toca" (Config & Personas).

## 🎨 How to Add a New Theme

We love new themes! To add one:

1. Open `src/calango/themes.py`.
2. Add a new entry to the `THEMES` dictionary.
3. Use the existing keys (`primaryColor`, `backgroundColor`, etc.).
4. **Naming Convention:** Use a Brazilian name if possible (e.g., "Jabuticaba", "Caatinga").

**Example:**

```python
"Jabuticaba (Dark)": {
    "primaryColor": "#FFFFFF",
    "headerColor": "#F0F0F0",
    "backgroundColor": "#120a1f", # Deep purple/black
    "textColor": "#E0E0E0",
    "buttonTextColor": "#000000",
},
```

## 🚀 Submitting a Pull Request

1. **Create a Branch:** `git checkout -b feature/my-amazing-feature`.
2. **Commit:** Keep messages clear (e.g., `feat: add new Amazonia theme`).
3. **Push:** `git push origin feature/my-amazing-feature`.
4. **Open a PR:** Go to the GitHub repo and click "Compare & pull request".

### Checklist for PRs

* [ ] Code runs locally without errors.
* [ ] `make check` passes (no linting errors).
* [ ] If you added a new dependency, you ran `uv pip compile pyproject.toml`.

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License defined in the `LICENSE` file.
