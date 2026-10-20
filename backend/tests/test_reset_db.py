import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import backend.db_utils as db
from backend.reset_db import reset_db


class ResetDatabaseTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        database = patch.object(db, "DB_PATH", Path(directory.name) / "test.db")
        database.start()
        self.addCleanup(database.stop)

    def test_reset_removes_all_user_tables_and_allows_a_fresh_start(self):
        db.create_tables()
        db.insert_message(-1, "user", "Old message")
        conn = db.get_connection()
        try:
            with conn:
                conn.execute('CREATE TABLE "extra ""table" (value TEXT)')
                conn.execute('INSERT INTO "extra ""table" VALUES (?)', ("Extra data",))
        finally:
            conn.close()

        reset_db()

        conn = db.get_connection()
        try:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT GLOB 'sqlite_*'"
            ).fetchall()
            self.assertEqual(tables, [])
        finally:
            conn.close()

        db.create_tables()
        self.assertEqual(db.get_all_conversations(), [])
        conv_id = db.insert_message(-1, "user", "Fresh message")
        self.assertEqual(conv_id, 1)
        self.assertEqual(db.get_all_messages(conv_id)[0]["content"], "Fresh message")

    def test_reset_handles_an_empty_database_and_repeated_resets(self):
        reset_db()
        reset_db()
        db.create_tables()
        self.assertEqual(db.get_all_conversations(), [])


if __name__ == "__main__":
    unittest.main()
