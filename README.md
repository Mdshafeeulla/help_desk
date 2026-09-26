# 🏢 Enterprise RAG — Multi-Department Knowledge Assistant

A **local-first**, **privacy-preserving** RAG (Retrieval-Augmented Generation) system that lets different company departments query their own documents via an LLM — with **strict department-level data isolation (ABAC)**.

> **No data leaves your machine.** Everything runs locally on your GPU.

---

## ✨ Features

- 🔒 **ABAC Data Isolation** — HR can't see Finance docs. Enforced at the DB layer.
- 🧠 **Hybrid Retrieval** — ANN vector search + BM25 keyword re-ranking
- ⚡ **Sub-2s Latency** — GPU-accelerated embeddings + quantized LLM
- 💾 **Persistent Storage** — LanceDB survives restarts (no re-indexing!)
- 🎯 **MRL Embeddings** — 256-dim Matryoshka embeddings for fast ANN search
- 📄 **PDF + TXT Upload** — PyMuPDF for fast, accurate text extraction
- 💬 **Chat Interface** — Multi-turn Q&A with source attribution
- 🔑 **Admin Panel** — Upload docs, manage departments, view stats

---

## 🖥️ Hardware Requirements

| Component | Minimum |
|---|---|
| GPU | NVIDIA GPU with 4+ GB VRAM (RTX 3050 or better) |
| RAM | 16 GB |
| CUDA | 11.8+ (we use 12.8) |
| Disk | ~10 GB (models + DB) |

---

## 🚀 Quick Start

### 1. Clone & Enter Project

```bash
cd e:\project\enterprise-rag
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install PyTorch with CUDA (if not already installed)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

> Skip this if you already have `torch` with CUDA. Check with:
> ```bash
> python -c "import torch; print(torch.cuda.is_available())"
> ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Pull an LLM via Ollama

Make sure [Ollama](https://ollama.com) is installed and running, then:

```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
```

Other options:
```bash
ollama pull mistral           # You already have this
ollama pull phi4-mini          # Fastest, lowest VRAM
ollama pull gemma3:4b          # Google, balanced
```

### 6. Run the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## 📖 How to Use

### As Admin

1. Open the app → click **"Open Admin →"**
2. Select a **department** from the dropdown (e.g., HR, Finance, IT)
3. Upload **PDF or TXT** files containing department documents
4. Click **"Index Documents"** — chunks are embedded and stored in LanceDB
5. View stats and manage documents in the other tabs

### As Employee

1. Open the app → click **"Open Chat →"**
2. Select **your department** from the sidebar
3. Ask questions in natural language
4. The system retrieves relevant chunks **only from your department's documents**
5. The LLM generates a grounded answer with source citations

---

## 🔒 Security Model (ABAC)

Every document chunk in LanceDB carries a `department` metadata tag:

```
┌────────────────────────────────────────────────┐
│  User selects: department = "finance"          │
│                                                │
│  → LanceDB query:                              │
│     WHERE department = 'finance'   ← ENFORCED  │
│                                                │
│  → Only finance chunks reach the LLM           │
│  → HR, IT, Legal = physically unreachable      │
└────────────────────────────────────────────────┘
```

This filter is applied **server-side** in `core/store.py`. No user input can bypass it.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Streamlit UI                      │
│  ┌─────────────┐    ┌────────────────────────────┐  │
│  │ Admin Panel  │    │ Chat (dept-scoped)         │  │
│  └──────┬───────┘    └──────────┬─────────────────┘  │
│         │                       │                    │
│  ┌──────▼───────────────────────▼─────────────────┐  │
│  │             core/pipeline.py                    │  │
│  │  index_documents()    query_department()        │  │
│  └──┬──────┬──────┬──────┬──────┬─────────────────┘  │
│     │      │      │      │      │                    │
│  chunker embedder store retriever llm                │
│     │      │      │      │      │                    │
│     │   nomic   LanceDB  BM25  Ollama                │
│     │   (CUDA)  (ABAC)  re-rank (local)              │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
enterprise-rag/
├── app.py                  # Home page (role selector)
├── pages/
│   ├── 1_Admin_Panel.py    # Upload & manage documents
│   └── 2_Chat.py           # Employee Q&A chat
├── core/
│   ├── config.py           # Central configuration
│   ├── embedder.py         # nomic-embed-text-v1.5 + CUDA + MRL
│   ├── chunker.py          # Word-based overlapping chunks
│   ├── store.py            # LanceDB + ABAC filtering
│   ├── retriever.py        # Hybrid ANN + BM25 re-ranking
│   ├── llm.py              # Ollama wrapper
│   ├── pipeline.py         # Orchestrator
│   └── prompt_builder.py   # Department-aware prompts
├── utils/
│   ├── pdf_parser.py       # PyMuPDF text extraction
│   └── logger.py           # Structured logging
├── data/
│   └── lancedb/            # Persistent vector store (auto-created)
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Configuration

Edit `core/config.py` to customize:

| Setting | Default | Description |
|---|---|---|
| `departments` | hr, finance, it, sales, ... | Company departments |
| `embed_dimensions` | 256 | MRL truncation (256 of 768) |
| `chunk_size` | 300 words | Words per chunk |
| `top_k` | 6 | Chunks retrieved per query |
| `semantic_weight` | 0.65 | ANN vs BM25 balance |
| `ollama_model` | qwen2.5:7b-instruct-q4_K_M | Default LLM |

---

## 🔧 Tech Stack

| Component | Technology |
|---|---|
| LLM | Ollama (Qwen2.5 7B Q4) |
| Embedder | nomic-embed-text-v1.5 (CUDA) |
| Vector DB | LanceDB (embedded, Rust) |
| Search | Hybrid ANN + BM25 |
| Filtering | ABAC via LanceDB metadata |
| PDF Parser | PyMuPDF |
| UI | Streamlit |

---

## 📝 License

MIT
