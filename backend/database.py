import sqlite3
from datetime import datetime

DB_PATH = "./failwhisperer.db"

def init_db():
    """Create database and tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT DEFAULT '',
            error_log TEXT,
            error_type TEXT,
            root_cause TEXT,
            fix TEXT,
            is_flaky INTEGER DEFAULT 0,
            confidence TEXT,
            has_screenshot INTEGER DEFAULT 0,
            screenshot_insight TEXT DEFAULT '',
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_analysis(data: dict) -> int:
    """Save one analysis to database, return the new ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analyses 
        (test_name, error_log, error_type, root_cause, fix, 
         is_flaky, confidence, has_screenshot, screenshot_insight, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('test_name', ''),
        data.get('error_log', ''),
        data.get('error_type', 'unknown'),
        data.get('root_cause', ''),
        data.get('fix', ''),
        1 if data.get('is_flaky') else 0,
        data.get('confidence', 'low'),
        1 if data.get('has_screenshot') else 0,
        data.get('screenshot_insight', ''),
        datetime.utcnow().strftime("%d %b %Y, %I:%M %p")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_history(limit: int = 20) -> list:
    """Get last N analyses from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # makes rows dict-like
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM analyses 
        ORDER BY id DESC 
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Initialize database on import
init_db()