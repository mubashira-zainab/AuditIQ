import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "app", "auditiq.db")

def upgrade_db():
    # If the DB is in backend folder instead of backend/app
    db_path_alt = os.path.join(os.path.dirname(__file__), "auditiq.db")
    if os.path.exists(db_path_alt):
        actual_db_path = db_path_alt
    else:
        actual_db_path = DB_PATH

    if not os.path.exists(actual_db_path):
        print("Database not found. SQLAlchemy will create it on first run.")
        return

    print(f"Upgrading database at {actual_db_path}...")
    conn = sqlite3.connect(actual_db_path)
    cursor = conn.cursor()

    # Check sessions table
    cursor.execute("PRAGMA table_info(sessions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if columns:
        if "is_pinned" not in columns:
            print("Adding 'is_pinned' column to 'sessions' table...")
            cursor.execute("ALTER TABLE sessions ADD COLUMN is_pinned BOOLEAN DEFAULT 0")
        
        if "upload_data" not in columns:
            print("Adding 'upload_data' column to 'sessions' table...")
            cursor.execute("ALTER TABLE sessions ADD COLUMN upload_data JSON")

    # Ensure memory table has user_id
    cursor.execute("PRAGMA table_info(memory)")
    mem_columns = [col[1] for col in cursor.fetchall()]
    if mem_columns and "user_id" not in mem_columns:
        print("Adding 'user_id' column to 'memory' table...")
        cursor.execute("ALTER TABLE memory ADD COLUMN user_id INTEGER REFERENCES users(id)")

    conn.commit()
    conn.close()
    print("Database upgrade complete.")

if __name__ == "__main__":
    upgrade_db()
