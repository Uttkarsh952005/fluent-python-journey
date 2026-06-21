"""
Chapter 15: Mini Project — Strictly Typed JSON Processor
========================================================
A practical implementation showing how to safely map dynamic JSON
payloads into static typing boundaries using TypedDict and cast().
"""

import sys
import json
from typing import TypedDict, List, cast, Any

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Static Schemas
# ─────────────────────────────────────────────────────────────────────────────

class LocationInfo(TypedDict):
    lat: float
    lng: float

class WeatherRecord(TypedDict):
    city: str
    temperature: float
    location: LocationInfo
    tags: List[str]

# ─────────────────────────────────────────────────────────────────────────────
# The Processor Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def fetch_json_payload() -> str:
    """Simulates receiving raw data from an external REST API."""
    raw_data = [
        {
            "city": "Tokyo", 
            "temperature": 22.5, 
            "location": {"lat": 35.6, "lng": 139.6},
            "tags": ["sunny", "humid"]
        },
        {
            "city": "London", 
            "temperature": 15.2, 
            "location": {"lat": 51.5, "lng": -0.1},
            "tags": ["rainy", "breezy"]
        }
    ]
    return json.dumps(raw_data)


def process_records(records: List[WeatherRecord]) -> None:
    """
    A strictly typed downstream function. 
    Mypy guarantees `records` matches the WeatherRecord schema exactly.
    """
    print(f"Processing {len(records)} records safely...")
    for rec in records:
        city = rec['city']
        temp = rec['temperature']
        lat = rec['location']['lat']
        print(f"  - {city} is {temp}°C (Coordinates: {lat} N)")


def main():
    print("=" * 60)
    print("  TypedDict JSON Pipeline")
    print("=" * 60)

    raw_json = fetch_json_payload()
    
    # 1. Parsing returns `Any`
    parsed_data: Any = json.loads(raw_json)
    
    # 2. Bridge the dynamic/static boundary using `cast`
    # Warning: This is a promise to Mypy. It does NOT validate at runtime.
    typed_records = cast(List[WeatherRecord], parsed_data)
    
    # 3. Safely pass to the downstream processor
    process_records(typed_records)
    
    print("\nNote: At runtime, typed_records is just a plain `list` of `dict`.")
    print(f"type(typed_records) == {type(typed_records)}")
    print(f"type(typed_records[0]) == {type(typed_records[0])}")

if __name__ == "__main__":
    main()
