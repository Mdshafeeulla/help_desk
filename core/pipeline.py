# core/pipeline.py
import time

from core.config import cfg
from core.embedder import embed_texts, embed_query
from core.chunker import chunk_text
from core.store import store
from core.retriever import hybrid_search
from core.prompt_builder import build_prompt
from core.llm import ask_llm
from core.instant_responses import get_instant_response
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


GREETINGS = {
    "hi", "hello", "hey", "hey there", "hi there", "greetings",
    "good morning", "good afternoon", "good evening", "howdy",
    "sup", "what's up", "yo", "thanks", "thank you", "bye", "goodbye",
    "who are you", "help", "hi!", "hello!", "hey!", "test"
}


def is_greeting(text: str) -> bool:
    """Check if the question is a simple greeting or small talk."""
    cleaned = text.strip().lower().strip("!.,?\"' ")
    if cleaned in GREETINGS:
        return True
    words = cleaned.split()
    if len(words) <= 2 and any(w in GREETINGS for w in words):
        return True
    return False


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
      0. Check instant response cache → return in <1ms (no LLM, no embedding)
      1. Check if greeting → send short prompt to LLM (skips vector search)
      2. Embed the question
      3. Hybrid search (ANN + BM25) with ABAC filter
      4. Build grounded prompt
      5. Send to LLM (streaming)

    Returns dict with keys: answer/stream, chunks, latency_ms, model, is_instant
    """
    t0 = time.perf_counter()

    # ── Stage 0: Instant Response Cache (< 1ms, zero LLM calls) ─────────
    instant_answer = get_instant_response(question)
    if instant_answer is not None:
        latency_ms = int((time.perf_counter() - t0) * 1000)
        log.info(f"[Instant] Returned cache hit in {latency_ms}ms — query='{question[:40]}'")
        return {
            "answer": instant_answer,
            "stream": None,
            "chunks": [],
            "latency_ms": latency_ms,
            "model": "instant-cache",
            "department": department,
            "is_instant": True,
        }

    # ── Stage 1: Greeting through LLM (short prompt, no vector search) ───
    if is_greeting(question):
        greeting_prompt = (
            "You are the MSU Corp Support Assistant — an AI-powered L1 customer support agent. "
            f"The customer said: '{question}'. "
            "Respond warmly and professionally in one short sentence, welcoming them to MSU Corp Support "
            "and asking what platform issue you can help them resolve today."
        )
        llm_res = ask_llm(greeting_prompt, model=model, stream=stream)
        latency_ms = int((time.perf_counter() - t0) * 1000)
        log.info(f"Greeting (LLM) handled — latency={latency_ms}ms")
        return {
            "stream": llm_res if stream else None,
            "answer": llm_res if not stream else None,
            "chunks": [],
            "latency_ms": latency_ms,
            "model": model or cfg.ollama_model,
            "department": department,
            "is_instant": False,
        }

    # ── Stage 2+: Full RAG Pipeline ──────────────────────────────────────
    if store.is_empty(department):
        raise ValueError(
            f"No documents indexed for IT Support. "
            f"Ask an Admin to upload documents first."
        )

    # 2. Embed query
    q_vec = embed_query(question)

    # 3. Retrieve (ABAC-filtered + BM25 re-ranked)
    retrieved = hybrid_search(store, q_vec, question, department, top_k)

    if not retrieved:
        raise ValueError(
            "No relevant documents found in IT Support for your question."
        )

    # 4. Build prompt
    prompt = build_prompt(retrieved, question, department)

    # 5. LLM generation
    llm_res = ask_llm(prompt, model=model, stream=stream)

    latency_ms = int((time.perf_counter() - t0) * 1000)
    log.info(
        f"RAG query complete — model={model or cfg.ollama_model}, "
        f"chunks={len(retrieved)}, latency={latency_ms}ms"
    )

    if stream:
        return {
            "stream": llm_res,
            "answer": None,
            "chunks": retrieved,
            "latency_ms": latency_ms,
            "model": model or cfg.ollama_model,
            "department": department,
            "is_instant": False,
        }
    else:
        return {
            "answer": llm_res,
            "stream": None,
            "chunks": retrieved,
            "latency_ms": latency_ms,
            "model": model or cfg.ollama_model,
            "department": department,
            "is_instant": False,
        }
