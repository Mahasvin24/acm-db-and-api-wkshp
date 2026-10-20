"""Run with: python -m uvicorn main:app --reload"""

import sqlite3
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import backend.db_utils as db
import backend.ollama as ollama


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_tables()
    yield


app = FastAPI(title="ACM Chat API", lifespan=lifespan)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


class MessageCreate(BaseModel):
    conv_id: int = -1
    role: Literal["user", "assistant", "system"] = "user"
    content: str = Field(min_length=1)

"""
Task #4
GET /conversations
Should return a list of all the different conversations.
Note that this is different from the actual sent messages.
"""
@app.get("/conversations")
def get_conversations():
    """List all conversations."""
    return db.get_all_conversations()

"""
Task #5
GET /conversations/conversation_id/messages
This should return an array of all the messages
for the conversation with id "conversation_id"
"""
@app.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int):
    """List messages in order. Returns [] if the conversation does not exist."""
    return db.get_all_messages(conversation_id)

"""
Task #6
POST /messages
This should return an array of all the messages
for the conversation with id "conversation_id".
"""
@app.post("/messages", status_code=201)
def post_message(message: MessageCreate):
    """Save a message. Use conv_id=-1 to start a new conversation."""
    try:
        conv_id = db.insert_message(
            message.conv_id, message.role, message.content
        )
    except sqlite3.IntegrityError as exc:
        if exc.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_FOREIGNKEY:
            raise HTTPException(status_code=404, detail="Conversation not found") from exc
        raise
    reply = None
    if message.role == "user":
        history = db.get_all_messages(conv_id)
        try:
            reply = ollama.chat(history)
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            status_code = 502
            explanation = "Ollama could not generate a reply. Check its logs and try again."
            if isinstance(exc, httpx.TimeoutException):
                status_code = 504
                explanation = "Ollama took too long to reply. Try again with a shorter message."
            elif isinstance(exc, httpx.ConnectError):
                status_code = 503
                explanation = "Cannot reach Ollama. Open the Ollama app or run ollama serve."
            elif isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 404:
                status_code = 503
                explanation = f"Download the model first: ollama pull {ollama.DEFAULT_MODEL}"
            raise HTTPException(
                status_code=status_code,
                detail={"message": explanation, "conversation_id": conv_id},
            ) from exc
        db.insert_message(conv_id, "assistant", reply)

    return {"conversation_id": conv_id, "reply": reply}
