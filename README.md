APIs and Databases demo for ACM Workshop
Oct 20th, 2026

Stack: Ollama + FastAPI + SQLite.

`db_utils.py` uses Python's built-in `sqlite3` module and saves to `data.db`
beside the module. No database installation is needed.

```python
from db_utils import (
    create_tables,
    get_all_conversations,
    get_all_messages,
    insert_message,
)

create_tables()  # Run once at app startup; safe to call again.
conv_id = insert_message(-1, "user", "Hello!")
insert_message(conv_id, "assistant", "Hi! What would you like to learn?")
print(get_all_conversations())
print(get_all_messages(conv_id))
```

`insert_message(conv_id, role, content)` returns the conversation ID. Passing
`-1` creates a new conversation; other IDs must already exist. Read helpers
return lists of dictionaries, including IDs and timestamps, ready for FastAPI
JSON responses. Messages are ordered by insertion; missing conversations return
an empty message list.

For SQL practice, use `get_connection()` and `get_cursor(conn)` directly:

```python
from db_utils import get_connection, get_cursor

conn = get_connection()
try:
    cursor = get_cursor(conn)
    cursor.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id",
        (conv_id,),
    )
    for row in cursor.fetchall():
        print(dict(row))
finally:
    conn.close()
```

Use `?` placeholders for values. For statements that change data, call
`conn.commit()` before closing (or use `with conn:` to commit on success and
roll back on failure). `create_conversations_table(cursor)` and
`create_messages_table(cursor)` are also available individually; `create_tables()`
calls both and manages the connection.

SQL exercises:

- Select only user messages in one conversation.
- Count messages in each conversation using `GROUP BY`.
- Join `conversations` and `messages` to include conversations with zero messages.

Run the database checks with `python -m unittest discover -s tests -v`.
