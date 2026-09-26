# core/config.py
from dataclasses import dataclass, field


@dataclass
class Config:
    # ── Paths ────────────────────────────────────────────────────────
    db_path: str = "data/lancedb"
    table_name: str = "enterprise_docs"

    # ── Embedder ─────────────────────────────────────────────────────
    embed_model: str = "nomic-ai/nomic-embed-text-v1.5"
    embed_device: str = "cuda"          # change to "cpu" if no GPU
    embed_dimensions: int = 256         # MRL: 256 of 768 dims

    # ── Chunking ─────────────────────────────────────────────────────
    chunk_size: int = 300               # words per chunk
    chunk_overlap: int = 50             # words overlap between chunks

    # ── Retrieval ────────────────────────────────────────────────────
    top_k: int = 6
    semantic_weight: float = 0.65       # 0.65 ANN + 0.35 BM25

    # ── LLM ──────────────────────────────────────────────────────────
    ollama_model: str = "phi4-mini"

    # ── Departments ───────────────────────────────────────────────────
    # Edit this list to match your company's departments
    departments: list = field(default_factory=lambda: [
        "hr",
        "finance",
        "it",
        "sales",
        "marketing",
        "operations",
        "legal",
        "management",
    ])

    # ── Available LLMs (must be pulled via `ollama pull`) ────────────
    available_models: list = field(default_factory=lambda: [
        "phi4-mini",
        "mistral",
        "qwen2.5:7b-instruct-q4_K_M",
        "gemma3:4b",
    ])


cfg = Config()  # singleton — import this everywhere
