"""
Utility helpers for translating frontend / backend text into AS RS tag names.
"""
import re

# e.g.  "A3"  →  "A3"
def parse_retrieval_location(loc_str: str) -> str | None:
    """
    Extract a valid box tag (A1-E7) for retrieval commands.
    """
    m = re.fullmatch(r"([A-E])([1-7])", loc_str.strip().upper())
    return "".join(m.groups()) if m else None

# e.g.  ("B2", "Occupied")  →  "B2S"
def parse_storage_update(location_str: str, status: str) -> str | None:
    """
    Convert a location + status into a storage (…S) tag when status is 'occupied'.
    """
    m = re.fullmatch(r"([A-E])([1-7])", location_str.strip().upper())
    if not m:
        return None
    tag = "".join(m.groups())
    return tag + "S" if status.lower() == "occupied" else tag
