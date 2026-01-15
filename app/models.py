import sqlite3
from datetime import datetime
from app.config import settings


def get_connection():
    return sqlite3.connect(
        settings.database_url.replace("sqlite:///", ""),
        check_same_thread=False,
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            from_msisdn TEXT NOT NULL,
            to_msisdn TEXT NOT NULL,
            ts TEXT NOT NULL,
            text TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()
