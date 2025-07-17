import re
import time
from datetime import datetime

from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

MONTHS = {
    "Januar": "01", "Februar": "02", "März": "03", "April": "04",
    "Mai": "05", "Juni": "06", "Juli": "07", "August": "08",
    "September": "09", "Oktober": "10", "November": "11", "Dezember": "12"
}

geolocator = Nominatim(user_agent="karlsruhe_event_app")

def normalize_street_name(text):
    return text.replace("Str.", "Straße").replace("str.", "straße")

def geocode_address(address, location, retries=3):
    def _geocode_address(query):
        for attempt in range(retries):
            try:
                loc = geolocator.geocode(f"{query}, Karlsruhe, Germany", timeout=10)
                if loc:
                    return loc.latitude, loc.longitude
            except GeocoderTimedOut:
                time.sleep(1)
        return None, None
    if address:
        return _geocode_address(address)
    if location:
        return _geocode_address(location)
    return None, None

def parse_event_datetime(text):
    pattern = r"(\d{1,2})\. (\w+) (\d{4}), (\d{1,2})(?:\.(\d{2}))?(?:  bis  \d{1,2}(?:\.\d{2})?)? Uhr"
    match = re.search(pattern, text)
    if not match:
        return None
    day, month_str, year, hour, minute = match.groups()
    minute = minute or "00"
    month_num = MONTHS.get(month_str)
    if not month_num:
        print(f"Unknown month: {month_str}")
        return None
    datetime_str = f"{year}-{month_num}-{int(day):02d} {int(hour):02d}:{minute}"
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M").isoformat()
    except ValueError as e:
        print(f"Failed to parse datetime: {datetime_str} -> {e}")