import csv
import json
import logging
import os
import shutil
import sqlite3
from datetime import date

from config import EXPORT_DIR, JSON_FILE


def load_existing_events():
    path = os.path.join(EXPORT_DIR, JSON_FILE)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_events_to_db(events):
    # Prepare export directory
    os.makedirs("docs", exist_ok=True)
    today_str = date.today().isoformat()
    base_path = f"docs/events-{today_str}"
    db_path = f"{base_path}.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            event_datetime TEXT,
            location TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL,
            description TEXT,
            source_link TEXT UNIQUE
        )
        """
    )
    inserted_count = 0
    for event in events:
        try:
            cursor.execute(
                """
                INSERT OR IGNORE INTO events (
                    title, event_datetime, location, address, latitude, longitude, description, source_link
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["title"],
                    event["datetime"],
                    event["location"],
                    event["address"],
                    event["latitude"],
                    event["longitude"],
                    event["description"],
                    event["link"],
                ),
            )
            if cursor.rowcount > 0:
                inserted_count += 1
        except sqlite3.Error as e:
            logging.error(f"SQLite error inserting event {event['link']}: {e}")
    conn.commit()
    conn.close()
    logging.log(level=logging.INFO, msg=f"Inserted {inserted_count} new events into database.")


def export_events(events, export_dir=EXPORT_DIR):
    today = date.today().isoformat()
    base = os.path.join(export_dir, f"events-{today}")

    # Write CSV
    with open(f"{base}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=events[0].keys())
        writer.writeheader()
        writer.writerows(events)

    # Write JSON
    with open(f"{base}.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

    # Copy SQLite
    shutil.copy(f"{base}.json", os.path.join(export_dir, "events-latest.json"))
    shutil.copy(f"{base}.csv", os.path.join(export_dir, "events-latest.csv"))
    shutil.copy(f"{base}.db", os.path.join(export_dir, "events-latest.db"))
    logging.log(level=logging.INFO, msg="Exported JSON, CSV, and DB to docs/ folder.")
