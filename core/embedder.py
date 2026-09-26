# core/embedder.py
import numpy as np
from sentence_transformers import SentenceTransformer
from core.config import cfg
from utils.logger import log

_model = None

def _get_model():
    global _model
    if _model is None:
        log.info(f"[Embedder] Loading '{cfg.embed_model}' on device='{cfg.embed_device}'...")
        _model = SentenceTransformer(
            cfg.embed_model,
            device=cfg.embed_device,
            trust_remote_code=True,  # required for nomic-embed-text-v1.5
        )
        log.info("[Embedder] Model ready ✓")
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Embed a batch of document texts.
    Uses nomic 'search_document' prompt for better retrieval accuracy.
    Returns float32 array of shape (N, cfg.embed_dimensions).
    """
    if isinstance(texts, str):
        texts = [texts]
    vecs = _get_model().encode(
        texts,
        prompt_name="document",
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=32,
    )
    # MRL truncation: use only first `embed_dimensions` dims
    return vecs[:, : cfg.embed_dimensions].astype("float32")


def embed_query(text: str) -> np.ndarray:
    """
    Embed a single user query.
    Uses nomic 'search_query' prompt (asymmetric encoding = better recall).
    Returns 1D float32 array of shape (cfg.embed_dimensions,).
    """
    vec = _get_model().encode(
        [text],
        prompt_name="query",
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return vec[0, : cfg.embed_dimensions].astype("float32")
