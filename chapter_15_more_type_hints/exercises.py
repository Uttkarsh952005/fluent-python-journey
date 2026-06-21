"""
Chapter 15: Exercises — The @overload Trap and Annotations
==========================================================
Original exercises demonstrating broken overload chains and runtime 
reflection on TypedDict.
"""

import sys
import typing

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Broken Overload
# ─────────────────────────────────────────────────────────────────────────────
# A common mistake is putting actual logic inside an @overload signature.
# Python throws that logic away when the concrete implementation is parsed!

@typing.overload
def multiply(val: int) -> int:
    # BUG: This logic is thrown away and never executed!
    print("Executing integer logic!")
    return val * val

@typing.overload
def multiply(val: str) -> str:
    # BUG: This logic is also thrown away!
    print("Executing string logic!")
    return val * 2

# This concrete function overwrites the previous two definitions in the module namespace.
def multiply(val: typing.Any) -> typing.Any:
    # ONLY this logic executes.
    return val * 2

def test_ex1_overload() -> None:
    section("Exercise 1: Overload Execution")
    
    # We expect the integer logic (val * val) to run if the overload was real.
    # But because it's overwritten, we get (val * 2) -> 5 * 2 = 10.
    res = multiply(5)
    print(f"multiply(5) returned: {res}")
    
    assert res == 10, "The overload logic incorrectly executed!"
    print("✓ Exercise 1 passed: Proved that @overload bodies are ignored at runtime.")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: TypedDict at Runtime
# ─────────────────────────────────────────────────────────────────────────────
# TypedDict does not inherit from dict. It is a class that creates a dict.
# We can use typing.get_type_hints() to read its schema at runtime.

class ServerConfig(typing.TypedDict):
    host: str
    port: int
    ssl: bool

def test_ex2_typeddict_reflection() -> None:
    section("Exercise 2: TypedDict Runtime Reflection")
    
    # 1. Instantiate it
    config = ServerConfig(host="localhost", port=443, ssl=True)
    
    # 2. Prove it is just a plain dict
    print(f"Type of config: {type(config).__name__}")
    assert type(config) is dict
    
    # 3. Read the static schema annotations at runtime
    hints = typing.get_type_hints(ServerConfig)
    print("\nSchema extracted from TypedDict at runtime:")
    for key, val_type in hints.items():
        print(f"  {key}: {val_type}")
        
    assert hints['port'] is int
    print("\n✓ Exercise 2 passed: TypedDict is a plain dict with attached __annotations__.")


if __name__ == "__main__":
    test_ex1_overload()
    test_ex2_typeddict_reflection()
