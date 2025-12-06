import sqlite3
from datetime import datetime

DB_PATH = "chat_logs.db"

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            response TEXT NOT NULL,
            time_taken REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_interaction(question: str, response: str, time_taken: float):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (timestamp, question, response, time_taken)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, question, response, time_taken))
    conn.commit()
    conn.close()

initialize_db()
