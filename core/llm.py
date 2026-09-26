# core/llm.py
import ollama
from core.config import cfg
from utils.logger import log


def ask_llm(prompt: str, model: str = None, stream: bool = False):
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
    messages = [{"role": "user", "content": prompt}]
    
    # Speed Optimizations:
    # 1. num_ctx=2048 reduces prompt processing (eval) overhead significantly.
    # 2. keep_alive="24h" prevents Ollama from unloading the model from RAM/VRAM after idle time.
    options = {
        "num_ctx": 2048,
    }

    try:
        if stream:
            response = ollama.chat(
                model=model,
                messages=messages,
                stream=True,
                options=options,
                keep_alive="24h",
            )
            for chunk in response:
                yield chunk["message"]["content"]
        else:
            response = ollama.chat(
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
        ollama.chat(
            model=model,
            messages=[{"role": "user", "content": "hi"}],
            options={"num_ctx": 256},
            keep_alive="24h",
        )
        log.info(f"[LLM] Model '{model}' pre-warmed ✓")
    except Exception as e:
        log.warning(f"[LLM] Could not pre-warm model '{model}': {e}")


