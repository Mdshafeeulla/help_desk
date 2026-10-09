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
from core.monitoring import track_indexing
from utils.logger import log


def index_documents(
    text: str,
    department: str,
    source: str,
    progress_callback=None,
) -> int:
    """Index a source while recording per-job compute and memory usage."""
    with track_indexing(source) as record_progress:
        def combined_progress(step_name, current, total):
            if progress_callback:
                progress_callback(step_name, current, total)
            record_progress(step_name, current, total)

        return _index_documents(
            text,
            department,
            source,
            progress_callback=combined_progress,
        )


def _index_documents(
    text: str,
    department: str,
    source: str,
    progress_callback=None,
) -> int:
    """
    Full indexing pipeline: text → chunks → embeddings → LanceDB.
    Tagged with department for ABAC isolation.

    Processes embeddings in batches to prevent CPU overload on large documents.

    Args:
        text: document text to index
        department: department tag for ABAC
        source: source filename
        progress_callback: optional callable(step_name, current, total) for progress

    Returns number of chunks indexed.
    """
    t0 = time.perf_counter()

    # Step 1: Chunk text
    if progress_callback:
        progress_callback("chunking", 0, 1)

    chunks = chunk_text(text)
    if not chunks:
        log.warning(f"No chunks produced from source='{source}'")
        return 0

    log.info(f"[Pipeline] {len(chunks)} chunks from source='{source}'")

    if progress_callback:
        progress_callback("chunking", 1, 1)

    # Step 2: Embed in batches (prevents CPU overload)
    texts = [c["text"] for c in chunks]
    EMBED_BATCH = 16  # smaller batches = friendlier CPU usage

    def embed_progress(batch_num, total_batches):
        if progress_callback:
            progress_callback("embedding", batch_num, total_batches)

    embeddings = embed_texts(texts, batch_size=EMBED_BATCH, progress_callback=embed_progress)

    # Step 3: Store in batches
    if progress_callback:
        progress_callback("storing", 0, 1)

    STORE_BATCH = 100
    total_stored = 0

    for i in range(0, len(chunks), STORE_BATCH):
        batch_chunks = chunks[i : i + STORE_BATCH]
        batch_embeddings = embeddings[i : i + STORE_BATCH]
        n = store.add_documents(batch_chunks, batch_embeddings, department, source)
        total_stored += n

    if progress_callback:
        progress_callback("storing", 1, 1)

    elapsed = time.perf_counter() - t0
    log.info(f"Indexed {total_stored} chunks in {elapsed:.2f}s — dept={department}, source={source}")
    return total_stored


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


def is_followup_edit_request(question: str, history: list[dict] = None) -> bool:
    """Identify requests to transform content from the previous exchange."""
    if not history:
        return False

    text = " ".join(question.lower().split())
    edit_actions = (
        "rephrase", "rewrite", "shorten", "summarize", "expand", "translate",
        "make it", "turn it", "draft an email", "write an email", "compose an email",
        "make an email",
    )
    references = (
        "above", "previous", "earlier", "last answer", "last response", "that email",
        "this email", "the email", "that answer", "that response", "based on that",
        "who asked", "asked the query", "the customer asked",
    )
    return any(action in text for action in edit_actions) and any(
        reference in text for reference in references
    )


def query_department(
    question: str,
    department: str,
    model: str = None,
    top_k: int = None,
    stream: bool = False,
    history: list[dict] = None,
    num_ctx: int = None,
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
    num_ctx = num_ctx or cfg.ollama_num_ctx

    # ── Stage 0: Instant Response Cache (< 1ms, zero LLM calls) ─────────
    instant_answer = get_instant_response(question) if not history else None
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
        llm_res = ask_llm(
            greeting_prompt,
            model=model,
            stream=stream,
            history=history,
            num_ctx=num_ctx,
        )
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

    # Rewrite requests should use the prior answer, not unrelated retrieved chunks.
    if is_followup_edit_request(question, history):
        followup_prompt = (
            "You are an assistant helping an MSU Corp support agent. The conversation "
            "contains the customer's request and the previous support response. Follow "
            "the new request using that conversation as the source. When rewriting or "
            "drafting, preserve the established facts and steps; do not add procedures, "
            "policies, or details that are not present in the conversation. Never turn "
            "a planned, pending, or conditional action into a completed event; for "
            "example, do not say a submission was approved unless the conversation "
            "explicitly says it was approved. If a status or name is unknown, use "
            "neutral wording or a clear placeholder. Return only the requested content.\n\n"
            f"New request: {question}"
        )
        llm_res = ask_llm(
            followup_prompt,
            model=model,
            stream=stream,
            history=history,
            num_ctx=num_ctx,
        )
        latency_ms = int((time.perf_counter() - t0) * 1000)
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
    prompt = build_prompt(
        retrieved,
        question,
        department,
        max_context_tokens=num_ctx * 50 // 100,
    )

    # 5. LLM generation
    llm_res = ask_llm(
        prompt,
        model=model,
        stream=stream,
        history=history,
        num_ctx=num_ctx,
    )

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
