# 🦎 Calango AI

**Agile. Adaptable. Yours.**

**Calango AI** is a free, open-source desktop application that lets you chat with the world's smartest Artificial Intelligences in a private, customizable environment.

Named after the agile Brazilian lizard, this app is built to be fast, resilient, and completely under your control. Unlike web chats, **you** own the data, **you** pick the personality, and **you** decide how it looks.


## ✨ Why use Calango?

* **🦎 Mimetismo (Mimicry):** Don't just chat with a robot. Use the **Persona Engineering** tab to turn your AI into a **Python Expert**, a **Creative Writer**, or a **Pirate Captain**. It adapts to your needs like a lizard blending into the leaves.
* **🥊 A Rinha (The Ring):** Not sure which AI is smarter or cheaper? Pit two models against each other side-by-side in the arena to see who wins.
* **🧠 A Cuca (The Brain):** A comprehensive dashboard to track your token usage, costs, and chat history. "She sees everything."
* **🔒 Privacy First:** Your API keys and chat history are stored **locally on your computer**. We don't see them. Big Tech doesn't see them. Only you see them.
* **💸 Pay As You Go:** Use your own API keys. This is often significantly cheaper than a $20/month subscription if you aren't a heavy user.

## 🎨 The Brazilian Touch

We ditched the generic "Dark Mode" for themes that celebrate the vibrant colors of Brazil:

* **🟩 Calango (Default):** The agile survivor of the Cerrado. (Signature Green/Dark)
* **🟨 Girassol:** Inspired by the warm, vibrant sunflower fields. (Solar Yellow/Stone)
* **🟪 Ipê:** The resilient purple tree that blooms in the winter. (Deep Purple)
* **🟥 Tiê:** Inspired by the *Tiê-Sangue* (Brazilian Tanager), a bird with intense blood-red feathers.
* **🟦 Gralha:** The *Gralha Azul* (Azure Jay), the intelligent bird that plants the Araucaria forests in the south.
* **🌸 Boto:** The *Boto Cor-de-Rosa*, the shapeshifting legend of the Amazon rivers.

## 🚀 How to Install

No coding required. Just download and run.

### **Windows**

1. Download `CalangoAI_Windows.exe` from the **[Releases Page](https://www.google.com/search?q=%23)**.
2. Double-click to run.
3. *Note:* You might see a "Windows protected your PC" popup. Click **"More Info"** -> **"Run Anyway"**. (This happens because this is a free open-source project and we don't pay for expensive corporate certificates).

### **Mac**

1. Download the `CalangoAI_MacOS` file.
2. Right-click the file and select **Open**.
3. Click **Open** again to confirm.

### **Linux**

1. Download the `CalangoAI_Linux` file.
2. Right-click -> Properties -> Permissions -> Check **"Allow executing file"**.
3. Run it.

## 🛠️ For Developers (Run from Source)

Want to hack on the code? We use `uv` (or pip) to manage dependencies.

```bash
# 1. Clone the repository
git clone https://github.com/danielfcollier/calango-ai.git
cd calango-ai

# 2. Install dependencies
pip install -e .

# 3. Run the App
streamlit run src/app.py
```

## ⚡ Getting Started in 3 Steps

### 1. Get an API Key

Calango is the *engine*, but you need *gas* (an API Key) to run it.
Based on the context of your project (which uses `litellm`), you can connect almost any major provider.

Here are the **current main LLMs** and the specific URLs to generate their API keys:

#### **Google Gemini**

* **Models:** Gemini 1.5 Pro, Gemini 1.5 Flash
* **Get API Key:** [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
* *Note: Google offers a generous free tier for developers.*

#### **OpenAI**

* **Models:** GPT-4o, GPT-4-Turbo, GPT-3.5-Turbo
* **Get API Key:** [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

#### **Anthropic**

* **Models:** Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
* **Get API Key:** [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

#### **Groq**

* **Why use it:** It runs open-source models (like **Llama 3** and **Mistral**) at lightning speeds.
* **Models:** Llama-3-70b, Mixtral-8x7b
* **Get API Key:** [https://console.groq.com/keys](https://console.groq.com/keys)

> They should work immediately if you use the correct model names (e.g., `gemini/gemini-1.5-pro`, `groq/llama3-70b-8192`).

### 2. Enter Your Key

1. Open Calango AI.
2. Go to the **Settings (A Toca) ⚙️** tab.
3. Enter a name (e.g., "My OpenAI") and paste your key.
4. Click **Save Connection**.

### 3. Start Chatting

1. Go to the **Chat 💬** tab.
2. Select your Provider and Model on the left sidebar.
3. Type hello!

## ☕ Support the Project

I am a Brazilian developer building open-source tools for the world. If you enjoy Calango AI, consider supporting the development!

### 🇧🇷 Para Brasileiros (Pix)

[☕  Me dê um café](https://livepix.gg/danielcollier)

### 🌍 International Support

[☕  Buy me a coffee](https://www.buymeacoffee.com/danielcollier)

## ❓ FAQ

**Where is my data stored?**

Everything is saved in a hidden folder on your computer to ensure privacy:

* Windows: `C:\Users\You\.calango\`
* Mac/Linux: `/home/you/.calango/`

**Is this free?**

The software is 100% free and open source. However, the API keys you use (OpenAI/Anthropic) may charge you a small fee per message (usually fractions of a cent).

**I found a bug!**

Please open an issue on our [GitHub page](https://github.com/danielfcollier/py-calango-ai).

**Created by Daniel Collier**

*Licensed under MIT License - Share freely!*