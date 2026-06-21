"""
Chapter 22: Dynamic Attributes and Properties
=============================================
Original implementations exploring attribute interception using 
__getattr__ to build dynamic JSON wrappers, and demonstrating the 
Uniform Access Principle using @property.
"""

import sys
from collections import abc
import keyword

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Dynamic JSON Wrapper (__getattr__)
# ─────────────────────────────────────────────────────────────────────────────

class FrozenJSON:
    """A read-only façade for navigating a JSON-like object using attribute notation."""

    def __init__(self, mapping):
        # Store the dictionary internally
        self.__data = dict(mapping)

    def __getattr__(self, name):
        """Called ONLY when an attribute is NOT found via normal lookups."""
        if hasattr(self.__data, name):
            # If they asked for a dict method like .keys(), return it
            return getattr(self.__data, name)
        
        try:
            # Try to fetch the key from the dictionary
            value = self.__data[name]
            
            # The Magic: If the value is another dict, wrap it dynamically!
            if isinstance(value, abc.Mapping):
                return FrozenJSON(value)
            # If it's a list, wrap each item
            elif isinstance(value, abc.MutableSequence):
                return [FrozenJSON(item) if isinstance(item, abc.Mapping) else item 
                        for item in value]
            return value
            
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

def demo_frozen_json() -> None:
    section("Part 1: Dynamic Attributes (__getattr__)")
    
    raw_data = {
        "user": {
            "id": 101,
            "profile": {
                "name": "Alice",
                "role": "Admin"
            }
        }
    }
    
    # Instead of raw_data["user"]["profile"]["name"]
    obj = FrozenJSON(raw_data)
    
    print(f"  Dynamic Access: obj.user.profile.name -> {obj.user.profile.name}")
    print(f"  Dynamic Access: obj.user.id -> {obj.user.id}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Properties (@property)
# ─────────────────────────────────────────────────────────────────────────────

class BankAccount:
    """Demonstrates data validation using properties."""
    def __init__(self, balance=0.0):
        # We store the actual value in a private attribute
        self._balance = balance

    @property
    def balance(self):
        """The Getter."""
        return self._balance

    @balance.setter
    def balance(self, value):
        """The Setter. Intercepts assignments to validate them."""
        if value < 0:
            raise ValueError("Balance cannot be negative!")
        self._balance = value

def demo_properties() -> None:
    section("Part 2: Data Validation with @property")
    
    account = BankAccount(100.0)
    print(f"  Initial balance: {account.balance}")
    
    account.balance = 150.0 # Triggers the setter cleanly
    print(f"  Updated balance: {account.balance}")
    
    try:
        account.balance = -50.0
    except ValueError as e:
        print(f"  Caught expected error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_frozen_json()
    demo_properties()
