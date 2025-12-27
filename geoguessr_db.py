import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DEFAULT_DB = "geoguessr.db"

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    game_type TEXT,
    token TEXT UNIQUE,
    fetched_at TEXT,
    raw_json TEXT
);
CREATE TABLE IF NOT EXISTS rounds (
    id INTEGER PRIMARY KEY,
    game_id INTEGER,
    round_index INTEGER,
    lat REAL,
    lng REAL,
    panoId TEXT,
    startTime TEXT,
    city TEXT,
    raw_json TEXT,
    FOREIGN KEY(game_id) REFERENCES games(id) ON DELETE CASCADE
);
"""

def init_db(db_path: str = DEFAULT_DB):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()
    conn.close()

def _conn(db_path: str = DEFAULT_DB):
    return sqlite3.connect(db_path)

def save_game(game_type: str, token: str, raw: Dict[str, Any], db_path: str = DEFAULT_DB) -> int:
    conn = _conn(db_path)
    cur = conn.cursor()
    fetched_at = datetime.utcnow().isoformat()
    raw_s = json.dumps(raw)
    cur.execute(
        "INSERT OR IGNORE INTO games (game_type, token, fetched_at, raw_json) VALUES (?, ?, ?, ?)",
        (game_type, token, fetched_at, raw_s)
    )
    cur.execute("SELECT id FROM games WHERE token = ?", (token,))
    game_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return game_id

def save_rounds(game_id: int, rounds: List[Dict[str, Any]], db_path: str = DEFAULT_DB):
    conn = _conn(db_path)
    cur = conn.cursor()
    for idx, rnd in enumerate(rounds):
        # try classic then panorama nested
        lat = rnd.get("lat")
        lng = rnd.get("lng")
        pano = rnd.get("panorama") or {}
        if lat is None and pano:
            lat = pano.get("lat")
            lng = pano.get("lng")
        panoId = rnd.get("panoId") or pano.get("panoId")
        startTime = rnd.get("startTime")
        raw_s = json.dumps(rnd)
        cur.execute(
            "INSERT INTO rounds (game_id, round_index, lat, lng, panoId, startTime, city, raw_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (game_id, idx, lat, lng, panoId, startTime, None, raw_s)
        )
    conn.commit()
    conn.close()

def get_ungeocoded_rounds(db_path: str = DEFAULT_DB, limit: Optional[int] = None):
    conn = _conn(db_path)
    cur = conn.cursor()
    q = "SELECT id, lat, lng FROM rounds WHERE city IS NULL AND lat IS NOT NULL AND lng IS NOT NULL ORDER BY id"
    if limit:
        q += f" LIMIT {int(limit)}"
    cur.execute(q)
    rows = cur.fetchall()
    conn.close()
    return rows  # list of (id, lat, lng)

def update_round_city(round_id: int, city: str, db_path: str = DEFAULT_DB):
    conn = _conn(db_path)
    cur = conn.cursor()
    cur.execute("UPDATE rounds SET city = ? WHERE id = ?", (city, round_id))
    conn.commit()
    conn.close()

def export_rounds_to_csv(csv_path: str, db_path: str = DEFAULT_DB):
    import pandas as pd
    conn = _conn(db_path)
    df = pd.read_sql_query("SELECT lat, lng, city, startTime, panoId FROM rounds WHERE lat IS NOT NULL AND lng IS NOT NULL", conn)
    conn.close()
    df.to_csv(csv_path, index=False)

def get_game_id_by_token(token: str, db_path: str = DEFAULT_DB) -> Optional[int]:
    conn = _conn(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM games WHERE token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def has_rounds_for_game(game_id: int, db_path: str = DEFAULT_DB) -> bool:
    conn = _conn(db_path)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM rounds WHERE game_id = ? LIMIT 1", (game_id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists
