import sqlite3
import os
import bcrypt
import secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "notes.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the notes and users tables if they don't already exist."""
    conn = get_connection()
    # Notes Table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT,
            description TEXT,
            uploader_email TEXT NOT NULL,
            uploader_name TEXT,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            upload_date TEXT NOT NULL
        )
        """
    )
    
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            password_hash BLOB NOT NULL,
            reset_key TEXT
        )
        """
    )
    conn.commit()
    conn.close()



def create_user(email, name, password):
    """Hash password with bcrypt and save user. Returns False if email exists."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
            (email.lower(), name, hashed),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already registered


def verify_user(email, password):
    """Verify password against stored hash. Returns user dict or None."""
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email.lower(),)
    ).fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
        return dict(user)
    return None


def generate_reset_key(email):
    """Generate a temporary secret key for password reset."""
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email.lower(),)
    ).fetchone()
    
    if not user:
        conn.close()
        return None

    key = secrets.token_hex(4).upper()  #temporary key generate krta h
    conn.execute(
        "UPDATE users SET reset_key = ? WHERE email = ?", (key, email.lower())
    )
    conn.commit()
    conn.close()
    return key


def reset_password(email, reset_key, new_password):
    """Reset password if the email and reset key match."""
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? AND reset_key = ?",
        (email.lower(), reset_key),
    ).fetchone()

    if user and reset_key:
        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        conn.execute(
            "UPDATE users SET password_hash = ?, reset_key = NULL WHERE email = ?",
            (hashed, email.lower()),
        )
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

#note upload krne k liye function

def add_note(title, subject, description, uploader_email, uploader_name,
             original_filename, stored_filename):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO notes (title, subject, description, uploader_email, uploader_name,
                            original_filename, stored_filename, upload_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            subject,
            description,
            uploader_email,
            uploader_name,
            original_filename,
            stored_filename,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
        ),
    )
    conn.commit()
    conn.close()


def search_notes(query):
    """Search notes by title, subject, or description (case-insensitive substring match)."""
    conn = get_connection()
    like_query = f"%{query}%"
    rows = conn.execute(
        """
        SELECT * FROM notes
        WHERE title LIKE ? OR subject LIKE ? OR description LIKE ?
        ORDER BY id DESC
        """,
        (like_query, like_query, like_query),
    ).fetchall()
    conn.close()
    return rows


def get_all_notes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def get_notes_by_user(email):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM notes WHERE uploader_email = ? ORDER BY id DESC", (email,)
    ).fetchall()
    conn.close()
    return rows


def get_note_by_id(note_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    conn.close()
    return row


def delete_note(note_id, requester_email):
    """
    Delete a note's DB record AND its file on disk.
    Only succeeds if requester_email matches the uploader (ownership check).
    """
    note = get_note_by_id(note_id)
    if note is None:
        return False
    if note["uploader_email"] != requester_email:
        return False

    file_path = os.path.join(UPLOAD_DIR, note["stored_filename"])
    if os.path.exists(file_path):
        os.remove(file_path)

    conn = get_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return True