"""Translate Ollama failures into API error responses."""

from typing import NoReturn

import httpx
from fastapi import HTTPException

import backend.ollama as ollama


def raise_ollama_error(error: Exception, conversation_id: int) -> NoReturn:
    """Raise an HTTP error with the ID of the conversation already saved."""
    status_code = 502
    explanation = "Ollama could not generate a reply. Check its logs and try again."
    if isinstance(error, httpx.TimeoutException):
        status_code = 504
        explanation = "Ollama took too long to reply. Try again with a shorter message."
    elif isinstance(error, httpx.ConnectError):
        status_code = 503
        explanation = "Cannot reach Ollama. Open the Ollama app or run ollama serve."
    elif isinstance(error, httpx.HTTPStatusError) and error.response.status_code == 404:
        status_code = 503
        explanation = f"Download the model first: ollama pull {ollama.DEFAULT_MODEL}"
    raise HTTPException(
        status_code=status_code,
        detail={"message": explanation, "conversation_id": conversation_id},
    ) from error
