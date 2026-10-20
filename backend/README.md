APIs and Databases demo for ACM Workshop
Oct 20th, 2026

Install dependencies and start the API from the repository root:

```bash
python -m pip install -r backend/requirements.txt
ollama pull qwen2.5:0.5b
python -m uvicorn backend.main:app --reload
```

If your terminal is already in `backend/` with the virtual environment active,
use these commands instead:

```bash
python3 run_tests.py
python3 -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to try the routes using **Try it out**.
Tables are created automatically at startup in `data.db`.

| Method | Route | Purpose |
| --- | --- | --- |
| POST | `/messages` | Save a message; generate and save a reply for user messages |
| GET | `/conversations` | List all conversations |
| GET | `/conversations/{conversation_id}/messages` | List a conversation's messages in order |

For `POST /messages`, send this JSON to start a conversation:

```json
{"conv_id": -1, "role": "user", "content": "Hello!"}
```

The response is `{"conversation_id": 1, "reply": "Hello!"}` (values can vary). Use that ID as
`conv_id` when posting subsequent messages. `conv_id` defaults to `-1` and
`role` defaults to `user`. Allowed roles are `user`, `assistant`, and `system`;
`content` is required and must contain at least one character.

Posting to an unknown conversation returns `404`; invalid request bodies return
`422`. Reading messages for an unknown conversation returns `[]`.
Keep Ollama running (open the app or run `ollama serve`). User messages are
sent to `qwen2.5:0.5b` along with conversation history. Assistant replies are
saved automatically. Other roles are stored without generating replies.
If generation fails, the user message remains saved; error details include
the conversation ID and a message explaining the problem.
Open http://127.0.0.1:8000 for the chat interface.

Run all tests with `python -m backend.run_tests`. Tests use temporary databases and
stop at the first failure or error.

API patterns follow the [FastAPI request body documentation](https://fastapi.tiangolo.com/tutorial/body/).
