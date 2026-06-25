import sqlite3
import json
import os
from typing import List, Dict, Any

DB_PATH = os.getenv("DB_PATH", "agents.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_history_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_history_db()

def add_message(session_id: str, role: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (session_id, role, content)
        VALUES (?, ?, ?)
    ''', (session_id, role, content))
    conn.commit()
    conn.close()

def get_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content, timestamp FROM chat_history 
        WHERE session_id = ? 
        ORDER BY timestamp ASC LIMIT ?
    ''', (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_history(session_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()
