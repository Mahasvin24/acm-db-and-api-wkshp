ACM API & Databases Workshop
Oct 20th, 2026

*** If you fall behind use the command below to catch up!
```bash
git reset --hard starter/main
```

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
ollama pull qwen2.5:0.5b
```

If Ollama is not already running, run `ollama serve` in a separate terminal.
Use the helper from Python:

```python
from backend.ollama import chat

reply = chat([{"role": "user", "content": "Explain APIs in one sentence."}])
print(reply)
```

`chat(messages, model="qwen2.5:0.5b")` returns reply text and accepts conversation
history from `backend.db_utils.get_all_messages()`. You can pass another
downloaded model using `model=`. Connection and HTTP errors propagate to the
caller. The API uses this helper automatically for messages with role `user`:
it saves the user message, loads the conversation history, generates a reply,
and saves that reply with role `assistant`. The response includes
`conversation_id` and `reply`. Other roles are saved without generating a reply.

Open http://127.0.0.1:8000 to chat. The frontend waits for the reply and loads
both messages from the database. If Ollama fails, the user message is still
saved. The error includes its conversation ID so the frontend can keep that
conversation open without resending the message.

The default [Qwen2.5 0.5B model](https://ollama.com/library/qwen2.5:0.5b) has
about 494 million parameters and a roughly 398 MB quantized download. This is
a reasonable choice for an 8 GB laptop, though runtime memory exceeds the
download size and speed depends on hardware and other running applications.
The helper sets a 2,048-token context and caps output at 256 tokens. Larger
contexts require more memory; see [Ollama context length](https://docs.ollama.com/context-length).
Older parts of long conversations may fall outside this small context window.

It calls Ollama's [chat API](https://docs.ollama.com/api/chat) with streaming
disabled, so each request returns one complete reply.

Run all tests with `python -m backend.run_tests`.
