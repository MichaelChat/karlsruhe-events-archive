import locale
import logging

from scraper import fetch_new_events
from storage import load_existing_events, save_events_to_db, export_events


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def main():
    existing_events = load_existing_events()
    events = fetch_new_events(existing_events)
    save_events_to_db(events)
    all_events = existing_events + events
    export_events(all_events)


if __name__ == "__main__":
    main()