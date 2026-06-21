"""
Chapter 22: Exercises — The Recursion Trap and Keywords
=======================================================
Original exercises demonstrating the two most common ways dynamic
attribute logic crashes in production.
"""

import sys
import keyword

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Infinite Recursion Trap
# ─────────────────────────────────────────────────────────────────────────────

class BadWrapper:
    def __init__(self, data):
        self.data = data
        
    def __getattr__(self, name):
        # BUG: Typo! We typed 'self.dta' instead of 'self.data'.
        # Because 'dta' doesn't exist, Python calls __getattr__("dta").
        # Inside that call, it hits 'self.dta' again, calling __getattr__("dta").
        # Result: Infinite Recursion!
        return self.dta[name]

def test_ex1_recursion() -> None:
    section("Exercise 1: The Recursion Trap")
    
    obj = BadWrapper({"key": "value"})
    try:
        print(obj.key)
        assert False, "Should have crashed!"
    except RecursionError:
        print("  [Caught] RecursionError: maximum recursion depth exceeded!")
        print("✓ Exercise 1 passed: Proved that missing attributes inside __getattr__ cause infinite loops.")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Keyword Collisions
# ─────────────────────────────────────────────────────────────────────────────

class SafeJSON:
    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            # If the JSON key is a Python keyword (like 'class'), 
            # we must sanitize it so it can be accessed via dot notation.
            if keyword.iskeyword(key):
                key += '_'
            self.__data[key] = value

    def __getattr__(self, name):
        try:
            return self.__data[name]
        except KeyError:
            raise AttributeError(name)

def test_ex2_keywords() -> None:
    section("Exercise 2: Keyword Collisions")
    
    raw_api_response = {
        "id": 404,
        "class": "ErrorResponse", # 'class' is a reserved keyword!
        "def": "Not Found"        # 'def' is a reserved keyword!
    }
    
    obj = SafeJSON(raw_api_response)
    
    # We cannot type obj.class (SyntaxError). 
    # But because we sanitized it, we can type obj.class_
    print(f"  obj.class_ -> {obj.class_}")
    print(f"  obj.def_   -> {obj.def_}")
    
    assert obj.class_ == "ErrorResponse"
    print("✓ Exercise 2 passed: Proved keyword sanitization is mandatory for API wrappers.")


if __name__ == "__main__":
    test_ex1_recursion()
    test_ex2_keywords()
