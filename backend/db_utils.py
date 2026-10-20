# db_utils.py

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("data.db")


"""
Task #1: Conversations Table
"""
def create_conversations_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)


"""
Task #2: Messages Table 
"""
def create_messages_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

"""
Task #3: Get Messages
"""
def get_all_messages(conversation_id):
    """Return a conversation's messages in insertion order, or an empty list."""
    conn = get_connection()
    try:
        cursor = get_cursor(conn)
        cursor.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


"""
Other useful functions implemented for you:
"""


def create_tables():
    """Create both tables without removing existing conversations."""
    conn = get_connection()
    try:
        with conn:
            cursor = get_cursor(conn)
            create_conversations_table(cursor)
            create_messages_table(cursor)
    finally:
        conn.close()


def get_connection():
    """Open the database. The caller is responsible for closing the connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_cursor(conn):
    """Get a cursor from an existing connection."""
    return conn.cursor()


def get_all_conversations():
    """Return all conversations, oldest first."""
    conn = get_connection()
    try:
        cursor = get_cursor(conn)
        cursor.execute("SELECT * FROM conversations ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def insert_message(conv_id, role, content):
    """Save a message and return its conversation ID.

    Pass -1 to start a conversation. Any other ID must already exist;
    otherwise SQLite raises sqlite3.IntegrityError. Both inserts commit
    together, so a failed message cannot leave an empty new conversation.
    """
    conn = get_connection()
    try:
        with conn:
            cursor = get_cursor(conn)
            if conv_id == -1:
                cursor.execute("INSERT INTO conversations DEFAULT VALUES")
                conv_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                (conv_id, role, content),
            )
        return conv_id
    finally:
        conn.close()