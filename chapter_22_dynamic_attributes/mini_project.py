"""
Chapter 22: Mini Project — Dynamic API Client Wrapper
=====================================================
A robust JSON API wrapper demonstrating the __new__ constructor method.
Depending on the JSON structure received (list vs dict vs int), __new__
dynamically decides which object type to instantiate and return.
"""

import sys
import keyword
from collections import abc
from functools import cached_property

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Dynamic Constructor (__new__)
# ─────────────────────────────────────────────────────────────────────────────

class APIResponse:
    """Dynamically parses and wraps JSON responses."""
    
    def __new__(cls, data):
        """
        __new__ is the TRUE constructor. It decides what object to create.
        If data is a mapping (dict), we create an APIResponse instance.
        If data is a sequence (list), we return a list of APIResponse instances!
        """
        if isinstance(data, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(data, abc.MutableSequence):
            return [cls(item) for item in data]
        else:
            return data

    def __init__(self, mapping):
        # By the time __init__ runs, we are guaranteed `mapping` is a dict
        self.__data = {}
        for key, value in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
            self.__data[key] = value

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            try:
                # Recursively call APIResponse, hitting __new__ again!
                return APIResponse(self.__data[name])
            except KeyError:
                raise AttributeError(f"'APIResponse' has no attribute '{name}'")

    @cached_property
    def data_size(self):
        """
        A simulated expensive calculation.
        Because of @cached_property, it only runs once!
        """
        print("    [System] Calculating payload size... (Expensive!)")
        return sum(len(str(v)) for v in self.__data.values())

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Execution
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Dynamic API Wrapper Pipeline")
    print("=" * 60)

    # Simulated API Response (A list of nested dictionaries)
    raw_json = [
        {"id": 1, "class": "Server", "metrics": {"cpu": 85, "ram": 1024}},
        {"id": 2, "class": "Database", "metrics": {"cpu": 15, "ram": 8192}}
    ]
    
    # 1. We pass a LIST to the class. __new__ intercepts this and 
    # automatically returns a list of APIResponse instances!
    print("Parsing JSON...")
    api_objects = APIResponse(raw_json)
    
    print(f"\nCreated {len(api_objects)} API Objects.")
    
    # 2. Dynamic Traversal
    print("\nDemonstrating Dynamic Traversal:")
    server_1 = api_objects[0]
    print(f"  server_1.id -> {server_1.id}")
    print(f"  server_1.class_ (sanitized) -> {server_1.class_}")
    print(f"  server_1.metrics.cpu -> {server_1.metrics.cpu}")
    
    # 3. Cached Properties
    print("\nDemonstrating @cached_property:")
    print(f"  Access 1 (computes): {server_1.data_size} bytes")
    print(f"  Access 2 (cached):   {server_1.data_size} bytes")

if __name__ == "__main__":
    main()
