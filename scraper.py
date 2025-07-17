import logging

import feedparser
import requests
from bs4 import BeautifulSoup

from config import FEED_URL
from utils import parse_event_datetime, geocode_address, normalize_street_name


def fetch_new_events(existing_events):
    logging.log(level=logging.INFO, msg="Fetching feed...")
    existing_links = {e["link"] for e in existing_events}
    feed = feedparser.parse(FEED_URL)
    new_events = []

    for entry in feed.entries:
        link = entry.link
        if link in existing_links:
            continue
        event = parse_event_page(link, entry.title)
        if event:
            new_events.append(event)
    logging.log(level=logging.INFO, msg=f"Found {len(new_events)} upcoming events.")
    return new_events

def parse_event_page(url, title):
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    details = soup.select_one("#details")
    if not details:
        return None

    try:
        dt_text = details.find("b").get_text(strip=True)
        event_datetime = parse_event_datetime(dt_text)
    except Exception:
        event_datetime = None

    location = details.find("span", class_="location")
    location_text = location.get_text(strip=True) if location else ""

    address_block = soup.select_one("#box_ort .adr")
    if address_block:
        street = address_block.find("span", class_="street-address")
        postal = address_block.find("span", class_="postal-code")
        city = address_block.find("span", class_="locality")

        street_address = street.get_text(strip=True) if street else ""
        postal_code = postal.get_text(strip=True) if postal else ""
        city_name = city.get_text(strip=True) if city else ""

        full_address = f"{street_address} {postal_code} {city_name}".strip(", ")
        full_address = normalize_street_name(full_address)
    else:
        full_address = ""

    lat, lon = geocode_address(full_address, location_text)

    desc_block = soup.find("div", id="description")
    description = desc_block.get_text(strip=True) if desc_block else ""

    return {
        "title": title,
        "datetime": event_datetime,
        "location": location_text,
        "address": full_address,
        "latitude": lat,
        "longitude": lon,
        "description": description,
        "link": url
    }
