"""Call Ollama's local chat API without an SDK."""

import httpx


OLLAMA_URL = "http://localhost:11434/api/chat"


def chat(messages, model="gemma3:1b"):
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
        json={"model": model, "messages": history, "stream": False},
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]
