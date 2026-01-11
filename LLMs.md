# 🦎 Calango AI: Providers & Models Guide

This configuration setup allows **Calango AI** to access a wide range of intelligences, from cutting-edge reasoning engines to ultra-fast local models.


## 🟢 OpenAI (The Standard)

*The industry standard for general-purpose AI, offering a mix of creative, reasoning, and legacy models.*

### **Generation 5 (Latest)**

* **`gpt-5.2`**
  * **Role:** Flagship Model.
  * **Best For:** Complex coding tasks, autonomous agent behaviors, and high-difficulty problem solving.

* **`gpt-5.1`**
  * **Role:** The "Warmer" Alternative.
  * **Best For:** Creative writing, general chat, and scenarios requiring a more personable tone.

* **`gpt-5-mini`**
  * **Role:** Budget King.
  * **Best For:** High-speed tasks where cost is a factor. Replaces the older *4o-mini*.

### **Reasoning (Thinking Models)**

* **`o3-pro`**
  * **Role:** Deepest Thinker.
  * **Best For:** Complex mathematics, scientific research, and deep logic. (Note: Slower generation speed).

* **`o3`**
  * **Role:** Assertive Reasoning.
  * **Best For:** Logic puzzles and tasks requiring structured thinking. Faster than *Pro*.

* **`o1`**
  * **Role:** Legacy Reasoning.
  * **Best For:** A reliable fallback for chain-of-thought tasks.

### **Legacy / Reliable**

* **`gpt-4o`**
  * **Role:** The 2024 Standard.
  * **Best For:** Production environments requiring well-understood, reliable behavior.


## 🟠 Anthropic (Claude)

*Known for high safety standards, large context windows, and nuanced writing.*

### **Generation 4.5 (Latest)**

* **`claude-sonnet-4-5`**
  * **Role:** The Best All-Rounder.
  * **Best For:** Coding, nuanced conversation, and balancing speed with intelligence.

* **`claude-opus-4-5`**
  * **Role:** Max Intelligence.
  * **Best For:** Long-form writing, deep analysis, and complex instruction following.

* **`claude-haiku-4-5`**
  * **Role:** Speed Demon.
  * **Best For:** Extremely cheap, quick chats, and simple tasks.


## 🔵 Google (Gemini)

*Multimodal powerhouses with strong reasoning capabilities and integration with Google's ecosystem.*

### **Generation 3 (Frontier)**

* **`gemini-3-pro-preview`**
  * **Role:** New Reasoning Engine.
  * **Features:** Includes "Thought Signatures" to show its reasoning process.


* **`gemini-3-flash-preview`**
  * **Role:** Frontier Speed.
  * **Best For:** High intelligence delivered with low latency.

### **Generation 2.5 (Stable)**

* **`gemini-2.5-pro`**
  * **Role:** Stable Workhorse.
  * **Best For:** Business tasks and reliable production use.

* **`gemini-2.5-flash`**
  * **Role:** High Volume / Low Cost.
  * **Best For:** Summarizing long documents and processing massive amounts of text cheaply.


## 🏎️ Groq (Open Source Speed)

*Specialized hardware provider running open-source models at extreme speeds.*

### **Meta Llama 3 Series**

* **`llama-3.3-70b-versatile`**
  * **Role:** Powerhouse.
  * **Performance:** Comparable to GPT-4 class models, but using open weights.

* **`llama-3.1-8b-instant`**
  * **Role:** Instant Response.
  * **Best For:** Simple queries requiring immediate answers. The fastest option available.

* **`mixtral-8x7b-32768`**
  * **Role:** Large Context.
  * **Best For:** Processing large blocks of text very quickly.


## 🦙 Ollama (Local / Privacy)

*Run completely offline on your own machine. Ensures maximum privacy and zero cost.*
*(Note: Requires a local Ollama instance running at `http://localhost:11434`)*

* **`llama3`**
  * **Description:** Standard Llama 3 running locally. Good general performance.

* **`mistral`**
  * **Description:** Mistral 7B. Highly efficient and smart for its small size.

* **`gemma2`**
  * **Description:** Google's open model. Tuned for creative tasks.