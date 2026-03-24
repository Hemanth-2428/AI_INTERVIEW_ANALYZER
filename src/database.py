import sqlite3
from datetime import datetime

DB_NAME = "interview_history.db"


def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            question TEXT,
            answer TEXT,
            confidence_score INTEGER,
            communication_score INTEGER,
            overall_score INTEGER,
            feedback TEXT,
            explanation TEXT,
            created_at TEXT
        )
        """
    )

    cursor.execute("PRAGMA table_info(interviews)")
    columns = [row[1] for row in cursor.fetchall()]

    if "role" not in columns:
        cursor.execute("ALTER TABLE interviews ADD COLUMN role TEXT")

    conn.commit()
    conn.close()


def save_interview(role, question, answer, result):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO interviews (
            role,
            question,
            answer,
            confidence_score,
            communication_score,
            overall_score,
            feedback,
            explanation,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            role,
            question,
            answer,
            result["confidence_score"],
            result["communication_score"],
            result["overall_score"],
            result["feedback"],
            result["explanation"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    conn.commit()
    conn.close()


def get_all_interviews(role):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, role, question, answer, confidence_score, communication_score,
               overall_score, feedback, explanation, created_at
        FROM interviews
        WHERE role = ?
        ORDER BY id DESC
        """,
        (role,),
    )
    rows = cursor.fetchall()

    conn.close()
    return rows


def delete_interview(interview_id, role):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM interviews WHERE id = ? AND role = ?",
        (interview_id, role),
    )
    conn.commit()
    conn.close()


def delete_all_interviews(role):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM interviews WHERE role = ?", (role,))
    conn.commit()
    conn.close()
