import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            google_id     TEXT UNIQUE,
            avatar        TEXT DEFAULT '',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def create_user(name, email, password=None, google_id=None, avatar=''):
    """Create a new user and return the user dict."""
    conn = get_db()
    try:
        password_hash = generate_password_hash(password) if password else None
        cursor = conn.execute(
            'INSERT INTO users (name, email, password_hash, google_id, avatar) VALUES (?, ?, ?, ?, ?)',
            (name, email.lower(), password_hash, google_id, avatar)
        )
        conn.commit()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return dict(user)
    finally:
        conn.close()


def find_user_by_email(email):
    """Return user dict by email or None."""
    conn = get_db()
    try:
        user = conn.execute(
            'SELECT * FROM users WHERE email = ?', (email.lower(),)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def find_user_by_google_id(google_id):
    """Return user dict by Google sub-ID or None."""
    conn = get_db()
    try:
        user = conn.execute(
            'SELECT * FROM users WHERE google_id = ?', (google_id,)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Return user dict by primary key or None."""
    conn = get_db()
    try:
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def verify_password(user_data, password):
    """Return True if password matches the stored hash."""
    if not user_data or not user_data.get('password_hash'):
        return False
    return check_password_hash(user_data['password_hash'], password)


def update_user_google(user_id, google_id, avatar):
    """Link an existing account to a Google ID (and set avatar if blank)."""
    conn = get_db()
    try:
        conn.execute(
            '''UPDATE users
               SET google_id = ?,
                   avatar = CASE WHEN avatar = '' OR avatar IS NULL THEN ? ELSE avatar END
               WHERE id = ?''',
            (google_id, avatar, user_id)
        )
        conn.commit()
    finally:
        conn.close()
