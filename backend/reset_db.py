"""Drop all user tables and data. Run from the repo root: python -m backend.reset_db"""

import db_utils as db


def reset_db():
    """Remove all user tables. Restart the API to recreate the workshop tables."""
    conn = db.get_connection()
    try:
        conn.execute("PRAGMA foreign_keys = OFF")
        with conn:
            cursor = db.get_cursor(conn)
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT GLOB 'sqlite_*'"
            )
            for row in cursor.fetchall():
                # Table names are SQL identifiers, so quote them instead of using ?.
                table_name = row["name"].replace('"', '""')
                cursor.execute(f'DROP TABLE "{table_name}"')
    finally:
        conn.close()


if __name__ == "__main__":
    reset_db()
    print("Database reset: all user tables and rows removed.")
