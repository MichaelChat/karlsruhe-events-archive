import locale
import logging

from scraper import fetch_new_events
from storage import load_existing_events, save_events_to_db, export_events

# Set to German locale for month parsing (Linux/Mac only; for Windows, this might vary)
try:
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
except locale.Error:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    existing_events = load_existing_events()
    events = fetch_new_events(existing_events)
    save_events_to_db(events)
    all_events = existing_events + events
    export_events(all_events)


if __name__ == "__main__":
    main()