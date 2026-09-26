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

    try:
        if stream:
            return ollama.chat(model=model, messages=messages, stream=True)
        else:
            response = ollama.chat(model=model, messages=messages)
            return response["message"]["content"]
    except Exception as e:
        log.error(f"LLM call failed (model={model}): {e}")
        raise RuntimeError(
            f"Could not reach Ollama model '{model}'. "
            f"Is Ollama running? Have you pulled the model?\n"
            f"Try: ollama pull {model}"
        ) from e
