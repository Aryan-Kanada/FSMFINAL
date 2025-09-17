# utils.py
import re

def parse_retrieval_location(loc_str):
    m = re.match(r"([A-E])([1-7])", loc_str)
    return m.group(1) + m.group(2) if m else None

def parse_storage_update(location_str, status):
    m = re.match(r"([A-E])([1-7])", location_str)
    if m:
        loc = m.group(1) + m.group(2)
        if status.lower() == 'occupied':
            loc += 's'
        return loc
    return None
