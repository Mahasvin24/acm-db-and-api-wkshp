APIs and Databases demo for ACM Workshop
Oct 20th, 2026

Install dependencies and start the API from this directory:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to try the routes using **Try it out**.
Tables are created automatically at startup in `data.db`.

| Method | Route | Purpose |
| --- | --- | --- |
| POST | `/messages` | Save a message; return its conversation ID |
| GET | `/conversations` | List all conversations |
| GET | `/conversations/{conversation_id}/messages` | List a conversation's messages in order |

For `POST /messages`, send this JSON to start a conversation:

```json
{"conv_id": -1, "role": "user", "content": "Hello!"}
```

The response is `{"conversation_id": 1}` (the ID can vary). Use that ID as
`conv_id` when posting subsequent messages. `conv_id` defaults to `-1` and
`role` defaults to `user`. Allowed roles are `user`, `assistant`, and `system`;
`content` is required and must contain at least one character.

Posting to an unknown conversation returns `404`; invalid request bodies return
`422`. Reading messages for an unknown conversation returns `[]`.
These routes store and retrieve messages; Ollama integration is a later step.

Run all tests with `python run_tests.py`. Tests use temporary databases and
stop at the first failure or error.

API patterns follow the [FastAPI request body documentation](https://fastapi.tiangolo.com/tutorial/body/).
