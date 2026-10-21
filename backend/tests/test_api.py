import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

import backend.db_utils as db_utils
from backend.main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        database = patch.object(db_utils, "DB_PATH", Path(directory.name) / "test.db")
        database.start()
        self.addCleanup(database.stop)
        model = patch("backend.main.ollama.chat", return_value="Hi!")
        self.chat = model.start()
        self.addCleanup(model.stop)
        self.client = self.enterContext(TestClient(app))

    def test_empty_database(self):
        response = self.client.get("/conversations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        response = self.client.get("/conversations/123/messages")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_post_messages_and_read_conversation(self):
        self.chat.side_effect = ["Hi!", "You said hello."]
        response = self.client.post("/messages", json={"conv_id": -1, "content": "Hello!"})
        self.assertEqual(response.status_code, 201)
        conv_id = response.json()["conversation_id"]
        self.assertEqual(response.json()["reply"], "Hi!")
        self.assertEqual(self.chat.call_args.args[0][0]["content"], "Hello!")

        response = self.client.post(
            "/messages",
            json={"conv_id": conv_id, "content": "What did I say?"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["conversation_id"], conv_id)
        self.assertEqual(response.json()["reply"], "You said hello.")
        self.assertEqual(
            [m["content"] for m in self.chat.call_args.args[0]],
            ["Hello!", "Hi!", "What did I say?"],
        )

        conversations = self.client.get("/conversations").json()
        self.assertEqual([c["id"] for c in conversations], [conv_id])
        response = self.client.get(f"/conversations/{conv_id}/messages")
        self.assertEqual(response.status_code, 200)
        messages = response.json()
        self.assertEqual(
            [m["content"] for m in messages],
            ["Hello!", "Hi!", "What did I say?", "You said hello."],
        )
        self.assertEqual([m["role"] for m in messages], ["user", "assistant", "user", "assistant"])

    def test_post_to_unknown_conversation(self):
        response = self.client.post("/messages", json={"conv_id": 123, "content": "Hello"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Conversation not found"})
        self.assertEqual(self.client.get("/conversations").json(), [])
        self.chat.assert_not_called()

    def test_invalid_message_does_not_create_conversation(self):
        for body in ({}, {"content": ""}, {"content": "Hi", "role": "invalid"}):
            with self.subTest(body=body):
                response = self.client.post("/messages", json=body)
                self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.get("/conversations").json(), [])
        self.chat.assert_not_called()

    def test_other_roles_are_saved_without_generating_a_reply(self):
        response = self.client.post("/messages", json={"role": "system", "content": "Be brief."})
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()["reply"])
        self.chat.assert_not_called()

    def test_ollama_errors_keep_the_user_message_and_return_conversation_id(self):
        request = httpx.Request("POST", "http://localhost:11434/api/chat")
        missing_model = httpx.HTTPStatusError(
            "model not found", request=request, response=httpx.Response(404, request=request)
        )
        server_error = httpx.HTTPStatusError(
            "server error", request=request, response=httpx.Response(500, request=request)
        )
        generic_message = "Ollama could not generate a reply. Check its logs and try again."
        for error, status, explanation in (
            (
                httpx.ConnectError("offline"), 503,
                "Cannot reach Ollama. Open the Ollama app or run ollama serve.",
            ),
            (
                httpx.ReadTimeout("slow"), 504,
                "Ollama took too long to reply. Try again with a shorter message.",
            ),
            (missing_model, 503, "Download the model first: ollama pull qwen2.5:0.5b"),
            (server_error, 502, generic_message),
            (httpx.ReadError("connection lost"), 502, generic_message),
            (ValueError("invalid JSON"), 502, generic_message),
            (KeyError("message"), 502, generic_message),
            (TypeError("invalid response"), 502, generic_message),
        ):
            with self.subTest(error=type(error).__name__):
                self.chat.side_effect = error
                response = self.client.post("/messages", json={"content": "Hello"})
                self.assertEqual(response.status_code, status)
                detail = response.json()["detail"]
                self.assertEqual(detail["message"], explanation)
                history = self.client.get(f'/conversations/{detail["conversation_id"]}/messages').json()
                self.assertEqual([m["content"] for m in history], ["Hello"])
                self.assertEqual(history[0]["role"], "user")


if __name__ == "__main__":
    unittest.main()
