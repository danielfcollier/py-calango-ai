# 🦎 Calango AI

**Agile. Adaptable. Yours.**

**Calango AI** is a free, open-source desktop application that lets you chat with the world's smartest Artificial Intelligences in a private, customizable environment.

Named after the agile Brazilian lizard, this app is built to be fast, resilient, and completely under your control. Unlike web chats, **you** own the data, **you** pick the personality, and **you** decide how it looks.

## 🔭 Project Scope & Philosophy

Calango AI is designed to be a **privacy-first LLM aggregator**. I believe that:

1. **Your Data is Yours:** Chat history and API keys should live on your filesystem, not on a third-party cloud.
2. **Agility is Key:** Switching between GPT-4, Claude 3.5, and a local Llama 3 should take one click.
3. **Local First:** Prioritize features that run on your machine, reducing dependency on internet connection and subscription services where possible.

## ✨ Why use Calango?

* **🦎 Mimetismo (Mimicry):** Don't just chat with a robot. Use the **Persona Engineering** tab to turn your AI into a **Python Expert**, a **Creative Writer**, or a **Pirate Captain**. It adapts to your needs like a lizard blending into the leaves.
* **🥊 A Rinha (The Ring):** Not sure which AI is smarter or cheaper? Pit **multiple models (up to 4)** against each other side-by-side in the arena to see who wins.
* **🧬 DNA Injection:** Instantly configure your providers and preferences by uploading a `config.yaml` backup file.
* **🧠 A Cuca (The Brain):** A comprehensive dashboard to track your token usage, costs, and chat history. "She sees everything."
* **🔒 Privacy First:** Your API keys and chat history are stored **locally on your computer**. I don't see them. Big Tech doesn't see them. Only you see them.
* **💸 Pay As You Go:** Use your own API keys. This is often significantly cheaper than a fixed monthly subscription.

## 🎨 The Brazilian Touch

I've ditched the generic "Dark Mode" for themes that celebrate the vibrant colors of Brazil:

* **🟩 Calango (Default):** The agile survivor of the Cerrado. (Signature Green/Dark)
* **🟨 Girassol:** Inspired by the warm, vibrant sunflower fields. (Solar Yellow/Stone)
* **🟪 Ipê:** The resilient purple tree that blooms in the winter. (Deep Purple)
* **🟥 Tiê:** Inspired by the *Tiê-Sangue* (Brazilian Tanager).
* **🟦 Gralha:** The *Gralha Azul* (Azure Jay), the planter of Araucaria forests.
* **🌸 Boto:** The *Boto Cor-de-Rosa*, the shapeshifting legend of the Amazon.

## 🛠️ For Developers (Quick Start)

Use `make` to handle dependencies, environments, and local services.

### Prerequisites

* Python 3.10+
* **Docker** (Required only if running Local LLMs/Ollama)

### 1. Installation & Run

```bash
# Clone the repository
git clone [https://github.com/danielfcollier/calango-ai.git](https://github.com/danielfcollier/calango-ai.git)
cd calango-ai

# Install dependencies (creates virtualenv automatically)
make install

# Run the Application
make run
```

### 2. Managing API Keys (The Secure Way)

Instead of pasting keys into the UI every time, developers can use a `.env` file.

1. Copy the example file:

```bash
cp .env.example .env
```

2. Edit `.env` and add your keys:

```ini
OPENAI_API_KEY="<YOUR_API_KEY>"
ANTHROPIC_API_KEY="<YOUR_API_KEY>"
GOOGLE_API_KEY="<YOUR_API_KEY>"
GROQ_API_KEY="<YOUR_API_KEY>"
```

> **⚠️ CAUTION:** Never commit your `.env` file to version control! It is included in `.gitignore` by default to prevent accidental leaks.

### 3. Local LLMs (Ollama + Docker)

Want to run **Llama 3**, **Mistral**, or **Gemma** completely offline? I've provided a Dockerized Ollama setup.

```bash
# Pulls the Ollama image, starts the container, and downloads default models
make setup-ollama
```

*Once finished, select "Ollama" as your provider in the Calango UI.*

### 4. Running Tests

Ensure the architecture is sound before pushing changes.

```bash
# Run Unit Tests
pytest tests/unit

# Run E2E UI Tests
pytest tests/e2e
```

## 🚀 How to Install (For Users)

No coding required. Just download and run.

### **Windows**

1. Download `CalangoAI_Windows.exe` from the **[Releases Page](https://www.google.com/search?q=https://github.com/danielfcollier/calango-ai/releases)**.
2. Double-click to run.
3. *Note:* If you see "Windows protected your PC", click **"More Info"** -> **"Run Anyway"**.

### **Mac**

1. Download the `CalangoAI_MacOS` file.
2. Right-click the file -> **Open**.
3. Click **Open** again to confirm.

### **Linux**

1. Download `CalangoAI_Linux`.
2. Right-click -> Properties -> Permissions -> Check **"Allow executing file"**.
3. Run it.

## 🗺️ Roadmap & Goals

We are actively evolving Calango from a local tool to a production-grade platform:

* **🌍 Globalization:** Native multi-language support (English/Portuguese).
* **🧠 Local RAG:** Give the AI "Long-Term Memory" by chatting with your local PDFs and documents.
* **🔐 Identity & Control:** Multi-user support with authentication, quotas, and budgets.
* **🗄️ Scalable Architecture:** Support for PostgreSQL and Async processing for high-performance deployments.

## ⚡ Supported Providers

Calango is the *engine*, but you need *gas* (an API Key) to run it.

#### **Cloud Providers**

* **Google Gemini:** [Get Key](https://aistudio.google.com/app/apikey) (Free tier available)
* **OpenAI:** [Get Key](https://platform.openai.com/api-keys)
* **Anthropic:** [Get Key](https://console.anthropic.com/settings/keys)
* **Groq:** [Get Key](https://console.groq.com/keys) (High speed open-source models)

#### **Local Providers**

* **Ollama:** Runs locally via Docker (see Developer instructions).

## ☕ Support the Project

I am a Brazilian developer building open-source tools for the world. If you enjoy Calango AI, consider supporting the development!

### 🇧🇷 Para Brasileiros (Pix)

[☕  Me dê um café](https://livepix.gg/danielcollier)

### 🌍 International Support

[☕  Buy me a coffee](https://www.buymeacoffee.com/danielcollier)

## ❓ FAQ

**Where is my data stored?**
Everything is saved in a hidden folder on your computer:

* Windows: `C:\Users\You\.calango\`
* Mac/Linux: `/home/you/.calango/`

**Is this free?**
The software is 100% free and open source. However, cloud API keys (like OpenAI) may charge per message. Local models (Ollama) are free to run.

**I found a bug!**
Please open an issue on our [GitHub page](https://www.google.com/search?q=https://github.com/danielfcollier/calango-ai).

**Created by Daniel Collier**
*Licensed under MIT License - Share freely!*