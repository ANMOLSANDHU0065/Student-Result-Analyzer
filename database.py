import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "scholardesk.db"

SUBJECTS = [
    "Python",
    "Java",
    "DBMS",
    "Web Development",
    "Computer Networks",
]


def get_connection():
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                dob TEXT DEFAULT '',
                gender TEXT DEFAULT '',
                address TEXT DEFAULT '',
                python REAL NOT NULL DEFAULT 0,
                java REAL NOT NULL DEFAULT 0,
                dbms REAL NOT NULL DEFAULT 0,
                web_development REAL NOT NULL DEFAULT 0,
                computer_networks REAL NOT NULL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,

                UNIQUE (user_id, roll_number)
            );

            CREATE INDEX IF NOT EXISTS idx_students_user
            ON students(user_id);
        """)


def get_user_by_email(email):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip(),)
        ).fetchone()

    return dict(row) if row else None


def get_user_by_id(user_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    return dict(row) if row else None


def create_user(name, email, password_hash):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (name.strip(), email.strip().lower(), password_hash)
        )
        user_id = cursor.lastrowid

    return get_user_by_id(user_id)


def get_all_students(user_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM students
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,)
        ).fetchall()

    return [dict(row) for row in rows]


def get_student(student_id, user_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM students
            WHERE id = ? AND user_id = ?
            """,
            (student_id, user_id)
        ).fetchone()

    return dict(row) if row else None


def save_student(user_id, data, student_id=None):
    values = (
        data["name"],
        data["roll_number"],
        data.get("email", ""),
        data.get("phone", ""),
        data.get("dob", ""),
        data.get("gender", ""),
        data.get("address", ""),
        data["marks"]["Python"],
        data["marks"]["Java"],
        data["marks"]["DBMS"],
        data["marks"]["Web Development"],
        data["marks"]["Computer Networks"],
    )

    with get_connection() as connection:
        if student_id is None:
            cursor = connection.execute(
                """
                INSERT INTO students (
                    user_id, name, roll_number, email, phone,
                    dob, gender, address, python, java, dbms,
                    web_development, computer_networks
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, *values)
            )
            saved_id = cursor.lastrowid
        else:
            cursor = connection.execute(
                """
                UPDATE students
                SET name = ?,
                    roll_number = ?,
                    email = ?,
                    phone = ?,
                    dob = ?,
                    gender = ?,
                    address = ?,
                    python = ?,
                    java = ?,
                    dbms = ?,
                    web_development = ?,
                    computer_networks = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
                """,
                (*values, student_id, user_id)
            )

            if cursor.rowcount == 0:
                return None

            saved_id = student_id

    return get_student(saved_id, user_id)


def delete_student(student_id, user_id):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM students
            WHERE id = ? AND user_id = ?
            """,
            (student_id, user_id)
        )

    return cursor.rowcount > 0