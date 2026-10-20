"""Call Ollama's local chat API without an SDK."""

import httpx


OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen2.5:0.5b"


def chat(messages, model=DEFAULT_MODEL):
    """Return an assistant reply for a list of messages with role and content.

    Accepts the dictionaries returned by db.get_all_messages() as well.
    Ollama must be running and the model must already be downloaded.
    HTTP and connection errors are raised to the caller.
    """
    history = [
        {"role": message["role"], "content": message["content"]}
        for message in messages
    ]
    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": model,
            "messages": history,
            "stream": False,
            "options": {"num_ctx": 2048, "num_predict": 256},
        },
        timeout=120.0,
    )
    response.raise_for_status()
    reply = response.json()["message"]["content"]
    if not isinstance(reply, str) or not reply.strip():
        raise ValueError("Ollama returned an empty or invalid reply.")
    return reply
