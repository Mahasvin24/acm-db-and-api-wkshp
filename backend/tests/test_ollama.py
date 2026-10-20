import unittest
from unittest.mock import patch

import httpx

from backend.ollama import OLLAMA_URL, chat


class OllamaTests(unittest.TestCase):
    @patch("backend.ollama.httpx.post")
    def test_chat_sends_history_and_returns_reply(self, post):
        history = [
            {"id": 1, "conversation_id": 2, "role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "What did I say?"},
        ]
        post.return_value = httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": "You said hello."}},
            request=httpx.Request("POST", OLLAMA_URL),
        )

        self.assertEqual(chat(history), "You said hello.")
        post.assert_called_once_with(
            OLLAMA_URL,
            json={
                "model": "gemma3:1b",
                "messages": [{"role": m["role"], "content": m["content"]} for m in history],
                "stream": False,
            },
            timeout=120.0,
        )

    @patch("backend.ollama.httpx.post")
    def test_model_can_be_changed_and_http_errors_propagate(self, post):
        post.return_value = httpx.Response(
            404,
            json={"error": "model not found"},
            request=httpx.Request("POST", OLLAMA_URL),
        )
        with self.assertRaises(httpx.HTTPStatusError):
            chat([{"role": "user", "content": "Hello"}], model="another-model")
        self.assertEqual(post.call_args.kwargs["json"]["model"], "another-model")

    @patch("backend.ollama.httpx.post", side_effect=httpx.ConnectError("Ollama is not running"))
    def test_connection_errors_propagate(self, post):
        with self.assertRaises(httpx.ConnectError):
            chat([{"role": "user", "content": "Hello"}])


if __name__ == "__main__":
    unittest.main()
