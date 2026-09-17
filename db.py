import sqlite3

DB_PATH = "passwords.db"


def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def add_entry(website: str, username: str, encrypted_password: str, db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
            (website, username, encrypted_password),
        )
        conn.commit()
    finally:
        conn.close()


def get_entry(website: str, db_path: str = DB_PATH):
    """Case-insensitive lookup. Returns (website, username, encrypted_password) or None."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT website, username, password FROM passwords WHERE LOWER(website) = LOWER(?)",
            (website,),
        )
        return cursor.fetchone()
    finally:
        conn.close()
