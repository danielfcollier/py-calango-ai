### ⚡ Phase 5: Async Chat & Queueing - Execution Plan

**Before you begin:**

* Ensure `litellm` is installed (it supports async out of the box).
* This phase drastically improves the "Rinha" performance by running models in parallel instead of sequentially.

---

#### 🔹 Prompt 1: The Asynchronous Engine

*First, we must teach the engine to use non-blocking I/O.*

> **Context:**
> I am optimizing my `CalangoEngine` to support asynchronous execution. Currently, `src/calango/core.py` is synchronous and blocks execution while waiting for LLM responses.
> **Goal:**
> Refactor `src/calango/core.py` to support `async`.
> **Requirements:**
> 1. **Refactor `CalangoEngine**`:
> * Rename `run_chat` to `run_chat_async` (or keep the name but make it `async def`).
> * Use `await litellm.acompletion(...)` instead of `litellm.completion`.
> * Ensure the method yields chunks asynchronously (`async yield` or similar pattern) for streaming.
> 
> 
> 2. **Update `ChatService` (`src/calango/services/chat_service.py`)**:
> * Make `send_message` an `async def`.
> * Await the engine's response.
> 
> 
> 
> 
> **Note:** Ensure you handle the generator correctly (using `async for` in the consuming code).
> Please generate the updated code for `src/calango/core.py` and `src/calango/services/chat_service.py`.

---

#### 🔹 Prompt 2: Parallel Rinha (The Speed Boost)

*Now we implement the true power of async: running 4 battle models at the exact same time.*

> **Context:**
> I have an async Engine. Now I want to optimize the "Rinha" (Arena) mode. Currently, it runs contenders sequentially (Model A finishes -> Model B starts), which is slow.
> **Goal:**
> Refactor `src/calango/services/arena_service.py` to run battles concurrently.
> **Requirements:**
> 1. **Update `ArenaService**`:
> * Make `run_battle_round` an `async def`.
> * Instead of a `for` loop that awaits each model, create a list of **Tasks**.
> * Use `await asyncio.gather(*tasks)` to run all models in parallel.
> * **Important:** Since we want to stream results to the UI, `asyncio.gather` might wait for *all* to finish. Ideally, we want to process them as they stream.
> * *Alternative Strategy for Prompt:* Implement a method `fight_contender_async(contender, messages)` that returns the full response (or a generator). The main `run_battle_round` should return the list of tasks or await them.
> 
> 
> 2. **Token Usage**: Ensure `calculate_usage` is called for each result asynchronously.
> 
> 
> Please generate the updated `src/calango/services/arena_service.py` using `asyncio` patterns.

---

#### 🔹 Prompt 3: UI Integration (The Event Loop)

*Streamlit runs synchronously by default. We need to bridge the gap.*

> **Context:**
> My services are now `async`, but my Streamlit UI (`src/ui/home.py`, `src/ui/rinha.py`) is synchronous. I need to run the async event loop within Streamlit.
> **Goal:**
> Update the UI files to handle async calls.
> **Requirements:**
> 1. **Imports**: `import asyncio`.
> 2. **Refactor `src/ui/home.py**`:
> * Wrap the chat generation logic in an `async def main_chat():`.
> * Use `async for chunk in chat_service.send_message(...)` to feed `st.write_stream` (Note: `st.write_stream` might support async generators directly, or you may need to iterate manually).
> * Run the function with `asyncio.run(main_chat())`.
> 
> 
> 3. **Refactor `src/ui/rinha.py**`:
> * This is tricky. We want to update 2-4 columns *simultaneously*.
> * Create an `async def run_battle():` function.
> * Use `asyncio.create_task` for each contender.
> * Pass specific Streamlit containers (e.g., `col1.empty()`, `col2.empty()`) to the service or handle the streaming callbacks within the UI loop.
> * *Simplified Approach:* Just await all results using `asyncio.gather` and display them when finished (fastest implementation), OR implement a complex consumer loop for parallel streaming. Let's aim for **Parallel Execution, Sequential Rendering** (wait for all, then show) OR **Parallel Execution, Individual Streaming** (if you can provide a helper for that).
> 
> 
> 
> 
> Please generate the updated code for `src/ui/home.py` and `src/ui/rinha.py`.