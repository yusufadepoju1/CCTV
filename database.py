import sqlite3
import os
from datetime import datetime

DB_PATH = 'db/intrusions.db'

def init_db():
    if not os.path.exists('db'):
        os.makedirs('db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intrusions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            screenshot_path TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            video_source TEXT NOT NULL,
            polygon_points TEXT NOT NULL
        )
    ''')
    # Ensure default config exists
    cursor.execute('SELECT COUNT(*) FROM config')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO config (id, video_source, polygon_points) VALUES (1, 'sample.mp4', '[[100, 480], [540, 480], [440, 250], [200, 250]]')")
    
    conn.commit()
    conn.close()

def add_intrusion(screenshot_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO intrusions (timestamp, screenshot_path)
        VALUES (?, ?)
    ''', (timestamp, screenshot_path))
    conn.commit()
    conn.close()

def get_recent_intrusions(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, timestamp, screenshot_path 
        FROM intrusions 
        ORDER BY id DESC 
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {"id": row[0], "timestamp": row[1], "screenshot_path": row[2]} 
        for row in rows
    ]

def get_config():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT video_source, polygon_points FROM config WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        import json
        try:
            points = json.loads(row[1])
        except json.JSONDecodeError:
            points = [[100, 480], [540, 480], [440, 250], [200, 250]]
        return {"video_source": row[0], "polygon_points": points}
    return {"video_source": "sample.mp4", "polygon_points": [[100, 480], [540, 480], [440, 250], [200, 250]]}

def update_config(video_source=None, polygon_points=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if video_source is not None and polygon_points is not None:
        import json
        points_str = json.dumps(polygon_points)
        cursor.execute("UPDATE config SET video_source = ?, polygon_points = ? WHERE id = 1", (video_source, points_str))
    elif video_source is not None:
        cursor.execute("UPDATE config SET video_source = ? WHERE id = 1", (video_source,))
    elif polygon_points is not None:
        import json
        points_str = json.dumps(polygon_points)
        cursor.execute("UPDATE config SET polygon_points = ? WHERE id = 1", (points_str,))
        
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print("Database initialized.")
