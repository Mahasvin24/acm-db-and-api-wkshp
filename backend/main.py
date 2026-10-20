"""Run with: python -m uvicorn main:app --reload"""

import sqlite3
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import backend.db_utils as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_tables()
    yield


app = FastAPI(title="ACM Chat API", lifespan=lifespan)


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
    return {"conversation_id": conv_id}