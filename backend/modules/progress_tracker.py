"""
Module: Progress Tracker
- SQLite-backed scan history
- Stores severity, lesion count, dark spot coverage per scan
"""

import os
import json
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/dermlens.db")


def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id          TEXT PRIMARY KEY,
            timestamp   TEXT NOT NULL,
            severity    TEXT,
            lesion_total INTEGER,
            dark_spot_pct REAL,
            fitzpatrick INTEGER,
            raw_json    TEXT
        )
    """)
    conn.commit()
    return conn


def save_scan(scan_id: str, analysis: dict):
    try:
        conn = _get_conn()
        conn.execute(
            """INSERT OR REPLACE INTO scans
               (id, timestamp, severity, lesion_total, dark_spot_pct, fitzpatrick, raw_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                scan_id,
                datetime.utcnow().isoformat(),
                analysis.get("severity", {}).get("label", "Unknown"),
                analysis.get("lesions", {}).get("total", 0),
                analysis.get("dark_spots", {}).get("coverage_percent", 0.0),
                analysis.get("fitzpatrick", {}).get("type", 3),
                json.dumps(analysis, default=str),
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_history() -> list:
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT id, timestamp, severity, lesion_total, dark_spot_pct, fitzpatrick "
            "FROM scans ORDER BY timestamp DESC LIMIT 30"
        ).fetchall()
        conn.close()
        return [
            {
                "scan_id": r[0],
                "timestamp": r[1],
                "severity": r[2],
                "lesion_total": r[3],
                "dark_spot_percent": r[4],
                "fitzpatrick": r[5],
            }
            for r in rows
        ]
    except Exception:
        return []
