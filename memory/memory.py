import sqlite3
import os

DB_PATH = "runtime/chat.db"

def init_db():
    """Initialize the SQLite database with a messages table."""
    os.makedirs("runtime", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,        -- e.g. 'discord' or 'slack'
            channel_id TEXT,      -- channel or conversation ID
            role TEXT,            -- 'system', 'user', 'assistant'
            user TEXT,            -- username or user ID
            content TEXT,         -- message text
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_message(platform: str, channel_id: str, role: str, user: str, content: str):
    """Insert a message into the database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO messages (platform, channel_id, role, user, content)
        VALUES (?, ?, ?, ?, ?)
    """, (platform, channel_id, role, user, content))
    conn.commit()
    conn.close()

def get_history(platform: str, channel_id: str, limit: int = 6):
    """Retrieve the last N messages for a given platform + channel."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT role, content FROM messages
        WHERE platform = ? AND channel_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (platform, channel_id, limit))
    rows = cur.fetchall()
    conn.close()

    # Reverse so oldest is first
    history = [{"role": role, "content": content} for role, content in reversed(rows)]
    return history