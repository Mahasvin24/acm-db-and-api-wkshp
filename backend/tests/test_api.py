import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
        self.client = self.enterContext(TestClient(app))

    def test_empty_database(self):
        response = self.client.get("/conversations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        response = self.client.get("/conversations/123/messages")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_post_messages_and_read_conversation(self):
        response = self.client.post("/messages", json={"conv_id": -1, "content": "Hello!"})
        self.assertEqual(response.status_code, 201)
        conv_id = response.json()["conversation_id"]

        response = self.client.post(
            "/messages",
            json={"conv_id": conv_id, "role": "assistant", "content": "Hi!"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["conversation_id"], conv_id)

        conversations = self.client.get("/conversations").json()
        self.assertEqual([c["id"] for c in conversations], [conv_id])
        response = self.client.get(f"/conversations/{conv_id}/messages")
        self.assertEqual(response.status_code, 200)
        messages = response.json()
        self.assertEqual([m["content"] for m in messages], ["Hello!", "Hi!"])
        self.assertEqual([m["role"] for m in messages], ["user", "assistant"])

    def test_post_to_unknown_conversation(self):
        response = self.client.post("/messages", json={"conv_id": 123, "content": "Hello"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Conversation not found"})
        self.assertEqual(self.client.get("/conversations").json(), [])

    def test_invalid_message_does_not_create_conversation(self):
        for body in ({}, {"content": ""}, {"content": "Hi", "role": "invalid"}):
            with self.subTest(body=body):
                response = self.client.post("/messages", json=body)
                self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.get("/conversations").json(), [])


if __name__ == "__main__":
    unittest.main()
