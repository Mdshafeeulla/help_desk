# core/pipeline.py
import time

from core.config import cfg
from core.embedder import embed_texts, embed_query
from core.chunker import chunk_text
from core.store import store
from core.retriever import hybrid_search
from core.prompt_builder import build_prompt
from core.llm import ask_llm
from utils.logger import log


def index_documents(text: str, department: str, source: str) -> int:
    """
    Full indexing pipeline: text → chunks → embeddings → LanceDB.
    Tagged with department for ABAC isolation.

    Returns number of chunks indexed.
    """
    t0 = time.perf_counter()

    chunks = chunk_text(text)
    if not chunks:
        log.warning(f"No chunks produced from source='{source}'")
        return 0

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    n = store.add_documents(chunks, embeddings, department, source)
    elapsed = time.perf_counter() - t0
    log.info(f"Indexed {n} chunks in {elapsed:.2f}s — dept={department}, source={source}")
    return n


def query_department(
    question: str,
    department: str,
    model: str = None,
    top_k: int = None,
    stream: bool = False,
) -> dict:
    """
    Full RAG query pipeline, scoped to a single department.

    Steps:
      1. Embed the question
      2. Hybrid search (ANN + BM25) with ABAC department filter
      3. Build grounded prompt
      4. Send to LLM

    Returns dict: {answer, chunks, latency_ms, model, department}
    """
    t0 = time.perf_counter()

    if store.is_empty(department):
        raise ValueError(
            f"No documents indexed for department '{department}'. "
            f"Ask an Admin to upload documents first."
        )

    # 1. Embed query
    q_vec = embed_query(question)

    # 2. Retrieve (ABAC-filtered + BM25 re-ranked)
    retrieved = hybrid_search(store, q_vec, question, department, top_k)

    if not retrieved:
        raise ValueError(
            f"No relevant documents found in '{department}' for your question."
        )

    # 3. Build prompt
    prompt = build_prompt(retrieved, question, department)

    # 4. LLM generation
    answer = ask_llm(prompt, model=model, stream=stream)

    latency_ms = int((time.perf_counter() - t0) * 1000)
    log.info(
        f"Query complete — dept={department}, model={model or cfg.ollama_model}, "
        f"chunks={len(retrieved)}, latency={latency_ms}ms"
    )

    return {
        "answer": answer,
        "chunks": retrieved,
        "latency_ms": latency_ms,
        "model": model or cfg.ollama_model,
        "department": department,
    }
