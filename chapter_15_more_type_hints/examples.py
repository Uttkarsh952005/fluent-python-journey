"""
Chapter 15: More About Type Hints
=================================
Original implementations exploring advanced static typing concepts.

Key concepts covered:
- @overload for complex return signatures
- TypedDict for enforcing dictionary schemas at static time
- typing.cast for overriding the type checker
"""

import sys
from typing import overload, TypedDict, cast, Any

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Overloaded Signatures (@overload)
# ─────────────────────────────────────────────────────────────────────────────
# Sometimes a function returns different types depending on the input type.
# We use @overload to tell Mypy exactly what happens for each input.

@overload
def double(value: int) -> int: ...

@overload
def double(value: str) -> str: ...

# The actual runtime implementation MUST be dynamically typed 
# (or broadly typed) to handle both. Mypy ignores this signature!
def double(value: Any) -> Any:
    return value * 2


def demo_overload() -> None:
    section("Part 1: @overload")
    # Mypy knows `res1` is exactly an int.
    res1 = double(10)
    # Mypy knows `res2` is exactly a str.
    res2 = double("Echo")
    print(f"double(10) -> {res1} ({type(res1).__name__})")
    print(f"double('Echo') -> {res2} ({type(res2).__name__})")


# ─────────────────────────────────────────────────────────────────────────────
# 2. TypedDict
# ─────────────────────────────────────────────────────────────────────────────
# A standard Python dictionary has no schema. TypedDict allows us to 
# specify the exact keys and value types a dict should contain for Mypy.

class UserRecord(TypedDict):
    id: int
    username: str
    is_active: bool

def process_user(record: UserRecord) -> None:
    # Mypy statically guarantees 'record' has these exact keys.
    # At runtime, `record` is just a completely normal dict.
    print(f"Processing User #{record['id']}: {record['username']} (Active: {record['is_active']})")


def demo_typed_dict() -> None:
    section("Part 2: TypedDict")
    # This is a valid UserRecord.
    valid_data: UserRecord = {'id': 404, 'username': 'admin', 'is_active': True}
    process_user(valid_data)
    
    # If we ran Mypy, this would fail because 'is_active' is an int!
    # But at runtime, Python doesn't care. TypedDict disappears.
    bad_data: UserRecord = {'id': 505, 'username': 'guest', 'is_active': 1} # type: ignore
    process_user(bad_data)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Type Casting (typing.cast)
# ─────────────────────────────────────────────────────────────────────────────
# Sometimes, Mypy cannot infer the type of dynamically loaded data (like JSON).
# `cast` forces Mypy to assume a type. It does NOTHING at runtime.

def fetch_data_from_db() -> Any:
    """Simulates a database fetch returning completely untyped data."""
    return {'id': 999, 'username': 'sysadmin', 'is_active': False}

def demo_cast() -> None:
    section("Part 3: typing.cast")
    
    raw_data = fetch_data_from_db()
    # At this point, Mypy thinks raw_data is `Any`.
    
    # We FORCE Mypy to treat it as a UserRecord.
    # At runtime, `cast(type, obj)` literally just returns `obj`.
    safe_data = cast(UserRecord, raw_data)
    process_user(safe_data)
    print("Successfully cast untyped data to TypedDict for downstream Mypy checking.")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_overload()
    demo_typed_dict()
    demo_cast()
