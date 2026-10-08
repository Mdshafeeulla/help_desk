# core/llm.py
import os
import ollama
from core.config import cfg
from utils.logger import log

_client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))


def ask_llm(
    prompt: str,
    model: str = None,
    stream: bool = False,
    history: list[dict] = None,
):
    """
    Send a prompt to an Ollama model.

    Args:
        prompt : the full prompt string
        model  : Ollama model name (defaults to cfg.ollama_model)
        stream : if True, returns a generator yielding token chunks

    Returns:
        str (if stream=False) or generator (if stream=True)
    """
    model = model or cfg.ollama_model
    messages = [
        {"role": message["role"], "content": message["content"]}
        for message in (history or [])[-2:]
        if message.get("role") in {"user", "assistant"}
        and isinstance(message.get("content"), str)
    ]
    messages.append({"role": "user", "content": prompt})
    
    # A smaller context window lowers Ollama's memory use; increase it if prompts
    # are too long. keep_alive avoids reloading the model between requests.
    options = {
        "num_ctx": cfg.ollama_num_ctx,
    }

    try:
        if stream:
            response = _client.chat(
                model=model,
                messages=messages,
                stream=True,
                options=options,
                keep_alive="24h",
            )
            for chunk in response:
                yield chunk["message"]["content"]
        else:
            response = _client.chat(
                model=model,
                messages=messages,
                options=options,
                keep_alive="24h",
            )
            return response["message"]["content"]
    except Exception as e:
        log.error(f"LLM call failed (model={model}): {e}")
        raise RuntimeError(
            f"Could not reach Ollama model '{model}'. "
            f"Is Ollama running? Have you pulled the model?\n"
            f"Try: ollama pull {model}"
        ) from e


def prewarm_model(model: str = None):
    """
    Pre-load model weights into VRAM/RAM so the user doesn't wait on cold-start.
    """
    model = model or cfg.ollama_model
    try:
        log.info(f"[LLM] Pre-warming model '{model}' in VRAM/RAM...")
        _client.chat(
            model=model,
            messages=[{"role": "user", "content": "hi"}],
            options={"num_ctx": cfg.ollama_num_ctx},
            keep_alive="24h",
        )
        log.info(f"[LLM] Model '{model}' pre-warmed ✓")
    except Exception as e:
        log.warning(f"[LLM] Could not pre-warm model '{model}': {e}")


