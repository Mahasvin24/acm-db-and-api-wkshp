# ACM API & Databases Workshop

Oct 20th, 2026

Run the setup commands below from the repository root unless noted otherwise.
Set up Ollama first, then start the backend and open the frontend.

## Ollama

Ollama runs the AI model locally and provides replies to the backend.

### Install

- **macOS:** Download Ollama from [the macOS download page](https://ollama.com/download/mac),
  install it, and open the app. Complete any first-launch setup prompts.
- **Windows:** Download and run the installer from [the Windows download page](https://ollama.com/download/windows),
  then open Ollama. Open a new PowerShell or Command Prompt window after installation.
- **Linux:** Run the command from [Ollama's Linux installation guide](https://docs.ollama.com/linux):

  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

Check that the command is available:

```bash
ollama --version
```

If your terminal cannot find `ollama`, restart the terminal and try again.

### Start Ollama and download the model

Keep the Ollama app running. If the server is not already running, start it in
a separate terminal and leave that terminal open:

```bash
ollama serve
```

If `ollama serve` reports that port `11434` is already in use, Ollama may already
be running through the app or a background service.

In another terminal, download the workshop's default model and try a prompt:

```bash
ollama pull qwen2.5:0.5b
ollama run qwen2.5:0.5b "Explain APIs in one sentence."
```

The backend connects to Ollama at `http://localhost:11434`. Local models do not
require an API key; see [Ollama's quickstart](https://docs.ollama.com/quickstart).

### Model and memory

The default [Qwen2.5 0.5B model](https://ollama.com/library/qwen2.5:0.5b) has
about 494 million parameters and a roughly 398 MB quantized download. This is
a reasonable choice for an 8 GB laptop, though runtime memory exceeds the
download size and speed depends on hardware and other running applications.
The helper sets a 2,048-token context and caps output at 256 tokens. Larger
contexts require more memory; see [Ollama context length](https://docs.ollama.com/context-length).
Older parts of long conversations may fall outside this small context window.

## Backend

### Install dependencies

With Python installed, create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Or in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If your system uses `python3` instead of `python`, use `python3` to create the
environment. Once activated, install the backend dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

### Start the API

With Ollama running and the model downloaded, start FastAPI:

```bash
python -m uvicorn backend.main:app --reload
```

Keep this terminal open. Visit http://127.0.0.1:8000/docs to try the API routes.
See the [backend README](backend/README.md) for request examples and route details.

For messages with role `user`, the API saves the user message, loads the
conversation history, generates a reply, and saves that reply with role
`assistant`. The response includes `conversation_id` and `reply`. Other roles
are saved without generating a reply.

### Use the Ollama helper from Python

```python
from backend.ollama import chat

reply = chat([{"role": "user", "content": "Explain APIs in one sentence."}])
print(reply)
```

`chat(messages, model="qwen2.5:0.5b")` returns reply text and accepts conversation
history from `backend.db_utils.get_all_messages()`. You can pass another
downloaded model using `model=`. Connection and HTTP errors propagate to the
caller.

It calls Ollama's [chat API](https://docs.ollama.com/api/chat) with streaming
disabled, so each request returns one complete reply.

## Frontend

With the backend running, open http://127.0.0.1:8000 to chat. FastAPI serves the
files in `frontend/`, so no separate frontend install or server is needed.

The frontend waits for the reply and loads both messages from the database.
If Ollama fails, the user message is still saved. The error includes its
conversation ID so the frontend can keep that conversation open without
resending the message.

## Database

The backend uses SQLite and creates the tables automatically at startup in
`backend/data.db`. No separate database server is required.

To reset the database, stop FastAPI first, then run the following from the
repository root. **This removes all user tables and rows.**

```bash
python -m backend.reset_db
```

Restart FastAPI to recreate the tables:

```bash
python -m uvicorn backend.main:app --reload
```

## Tests

With the virtual environment active, run all tests from the repository root:

```bash
python -m backend.run_tests
```

## Catch up during the workshop

If you fall behind, use the command below to catch up. **This discards local
changes to tracked files.**

```bash
git reset --hard starter/main
```
