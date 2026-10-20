ACM API & Databases Workshop
Oct 20th, 2026

Reset the database from the repository root (removes all user tables and rows):

```bash
python -m backend.reset_db
```

Stop FastAPI before resetting, then start it again to recreate the tables:

```bash
python -m uvicorn backend.main:app --reload
```

For local AI replies, install [Ollama](https://ollama.com/download), open it,
and download the default model:

```bash
ollama pull gemma3:1b
```

If Ollama is not already running, run `ollama serve` in a separate terminal.
Use the helper from Python:

```python
from backend.ollama import chat

reply = chat([{"role": "user", "content": "Explain APIs in one sentence."}])
print(reply)
```

`chat(messages, model="gemma3:1b")` returns reply text and accepts conversation
history from `backend.db_utils.get_all_messages()`. You can pass another
downloaded model using `model=`. Connection and HTTP errors propagate to the
caller. The helper is separate from the message routes; they still only save
and retrieve messages.

It calls Ollama's [chat API](https://docs.ollama.com/api/chat) with streaming
disabled, so each request returns one complete reply.

Run all tests with `python -m backend.run_tests`.
