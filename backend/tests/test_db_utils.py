import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import backend.db_utils as db_utils


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        database = patch.object(db_utils, "DB_PATH", Path(directory.name) / "test.db")
        database.start()
        self.addCleanup(database.stop)
        db_utils.create_tables()

    def test_new_conversation_and_ordered_messages(self):
        conv_id = db_utils.insert_message(-1, "user", "Hello!")
        returned_id = db_utils.insert_message(conv_id, "assistant", "Hi!")

        self.assertEqual(returned_id, conv_id)
        self.assertEqual(len(db_utils.get_all_conversations()), 1)
        messages = db_utils.get_all_messages(conv_id)
        self.assertEqual([m["content"] for m in messages], ["Hello!", "Hi!"])
        self.assertEqual([m["role"] for m in messages], ["user", "assistant"])
        self.assertTrue(all(m["conversation_id"] == conv_id for m in messages))

    def test_conversations_are_separate(self):
        first = db_utils.insert_message(-1, "user", "First")
        second = db_utils.insert_message(-1, "user", "Second")

        self.assertNotEqual(first, second)
        self.assertEqual([c["id"] for c in db_utils.get_all_conversations()], [first, second])
        self.assertEqual([m["content"] for m in db_utils.get_all_messages(first)], ["First"])
        self.assertEqual([m["content"] for m in db_utils.get_all_messages(second)], ["Second"])

    def test_empty_database_and_missing_conversation(self):
        self.assertEqual(db_utils.get_all_conversations(), [])
        self.assertEqual(db_utils.get_all_messages(123), [])

    def test_invalid_conversation_is_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            db_utils.insert_message(123, "user", "Hello")
        self.assertEqual(db_utils.get_all_conversations(), [])

    def test_failed_message_rolls_back_new_conversation(self):
        with self.assertRaises(sqlite3.IntegrityError):
            db_utils.insert_message(-1, "user", None)
        self.assertEqual(db_utils.get_all_conversations(), [])

    def test_table_creation_preserves_data_and_content_is_not_sql(self):
        content = "It's a message'); DROP TABLE messages; -- 🐍"
        conv_id = db_utils.insert_message(-1, "user", content)
        db_utils.create_tables()
        self.assertEqual(db_utils.get_all_messages(conv_id)[0]["content"], content)


if __name__ == "__main__":
    unittest.main()
