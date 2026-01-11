### 🧠 Phase 3: Local RAG (Knowledge Base) - Execution Plan

**Before you begin:**

1. Run `pip install qdrant-client sentence-transformers pypdf langchain-text-splitters`.
2. (Optional) Add these to your `pyproject.toml` or `requirements.txt`.

---

#### 🔹 Prompt 1: The Vector Brain (Infrastructure)

*First, we set up the storage and embedding logic. We will use `sentence-transformers` for local, cost-free embeddings and Qdrant in local mode.*

> **Context:**
> I am adding Local RAG capabilities to my application. I need a service to handle vector storage and retrieval.
> **Goal:**
> Create `src/calango/services/vector_service.py`.
> **Requirements:**
> 1. **Class `VectorService**`:
> * **Init**: Initialize `QdrantClient` in local mode (path="./calango_data/qdrant") and `SentenceTransformer("all-MiniLM-L6-v2")`.
> * **Collection**: On init, check if a collection named "knowledge_base" exists. If not, create it with vector size 384 (standard for MiniLM).
> * **Method `upsert_text(text: str, metadata: dict)**`:
> * Generate embedding for the text.
> * Generate a UUID for the point.
> * Upsert into Qdrant.
> 
> 
> * **Method `search(query: str, limit=5)**`:
> * Embed the query.
> * Search Qdrant.
> * Return a list of results (text payload + score).
> 
> 
> 
> 
> 
> 
> Please generate the code for `src/calango/services/vector_service.py`.

---

#### 🔹 Prompt 2: The Ingestion UI (Knowledge Page)

*Now we build the interface to feed the brain.*

> **Context:**
> I have a `VectorService` ready. Now I need a UI page to upload documents (PDF/Text) and ingest them into the vector database.
> **Goal:**
> Create `src/ui/knowledge.py`.
> **Requirements:**
> 1. **Imports**: Use `pypdf` for PDF reading and `langchain_text_splitters.RecursiveCharacterTextSplitter` for chunking.
> 2. **UI Layout**:
> * Title: "📚 Biblioteca (Knowledge Base)".
> * File Uploader: Accept `.pdf`, `.txt`, `.md`.
> * "Ingest" Button.
> 
> 
> 3. **Logic**:
> * When a file is uploaded and "Ingest" is clicked:
> * Extract text (handle PDF vs Text).
> * Split text into chunks (approx 500 characters, overlap 50).
> * Call `vector_service.upsert_text` for each chunk (store filename in metadata).
> * Show a progress bar.
> * Show success message with the number of chunks added.
> 
> 
> 
> 
> 4. **Integration**: Initialize `VectorService` at the top of the file (or import from a singleton if we established one, but direct instantiation is fine for now).
> 
> 
> Please generate the code for `src/ui/knowledge.py`.

---

#### 🔹 Prompt 3: Connecting the Synapses (RAG Integration)

*Finally, we make the Chat Service use this new knowledge.*

> **Context:**
> I have the `VectorService` populated with data. Now I want the `ChatService` to retrieve relevant context before sending the user's message to the LLM.
> **Goal:**
> Modify `src/calango/core.py` and `src/calango/services/chat_service.py`.
> **Requirements:**
> 1. **Update `CalangoEngine` (`core.py`)**:
> * Update `run_chat` method signature to accept an optional `context` string.
> * If `context` is provided, append it to the System Prompt (e.g., "Use the following context to answer: {context}").
> * Log the `context` usage in the `usage` dictionary yielded/returned, so we can see it in the UI/Logs later.
> 
> 
> 2. **Update `ChatService` (`chat_service.py`)**:
> * Inject `VectorService` into `__init__`.
> * In `send_message`:
> * Call `vector_service.search(user_message)`.
> * Concatenate the top 3 results into a `context_str`.
> * Pass this `context_str` to the `engine.run_chat` call.
> 
> 
> 
> 
> 3. **Update `src/app.py**`:
> * Add the new page to navigation: `knowledge_page = st.Page("ui/knowledge.py", title="Knowledge", icon="📚")`.
> 
> 
> 
> 
> Please generate the updated code for `src/calango/core.py` and `src/calango/services/chat_service.py` with RAG logic.

---

### 🎥 Relevant Resources

To better understand how Qdrant and Sentence Transformers work together for this local setup, I selected this video for you:

[Qdrant Full Tutorial: Vector DB Setup, SentenceTransformers Embeddings](https://www.youtube.com/watch?v=SkpAIafmjHM)

This video is relevant because it walks through the exact stack you are implementing: Qdrant for storage and SentenceTransformers for local embeddings.