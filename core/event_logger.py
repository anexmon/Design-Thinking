import csv
import sqlite3
from pathlib import Path
from datetime import datetime

class EventLogger:
    def __init__(self, db_path="data/events.sqlite3"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                previous_state TEXT,
                new_state TEXT,
                details TEXT
            )""")

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def log(self, event_type, previous_state="", new_state="", details=""):
        stamp = datetime.now().astimezone().isoformat(timespec="seconds")
        with self._connect() as con:
            con.execute("INSERT INTO events(timestamp,event_type,previous_state,new_state,details) VALUES(?,?,?,?,?)",
                        (stamp, event_type, previous_state, new_state, details))

    def list_events(self, limit=500):
        with self._connect() as con:
            rows = con.execute("SELECT timestamp,event_type,previous_state,new_state,details FROM events ORDER BY id DESC LIMIT ?",
                               (limit,)).fetchall()
        return rows

    def export_csv(self, path):
        rows = self.list_events(100000)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "event_type", "previous_state", "new_state", "details"])
            writer.writerows(reversed(rows))
        return path
