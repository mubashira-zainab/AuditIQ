"""
AuditIQ Database Migration Script
Run this ONCE to add the new columns (title, username, updated_at) to the existing database.
Usage:  python migrate_db.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "auditiq.db"


def migrate():
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at: {DB_PATH}")
        print("  Run the backend first to create it.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(sessions)")
    existing = {row[1] for row in cursor.fetchall()}
    print(f"[INFO] Existing columns in 'sessions': {existing}")

    migrations = [
        ("title",      "ALTER TABLE sessions ADD COLUMN title TEXT"),
        ("username",   "ALTER TABLE sessions ADD COLUMN username TEXT"),
        ("updated_at", "ALTER TABLE sessions ADD COLUMN updated_at DATETIME"),
    ]

    for col_name, sql in migrations:
        if col_name not in existing:
            cursor.execute(sql)
            print(f"[OK] Added column: {col_name}")
        else:
            print(f"[SKIP] Column already exists: {col_name}")

    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_username ON sessions(username)")
        print("[OK] Index on username ready")
    except Exception as e:
        print(f"[NOTE] Index: {e}")

    cursor.execute("PRAGMA table_info(messages)")
    msg_cols = {row[1] for row in cursor.fetchall()}
    print(f"[INFO] Existing columns in 'messages': {msg_cols}")

    conn.commit()
    conn.close()
    print("[DONE] Migration complete!")


if __name__ == "__main__":
    migrate()
