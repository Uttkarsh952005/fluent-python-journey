"""
Chapter 11: Exercises — A Pythonic Object
=========================================
Original exercises exploring custom formatting, private attributes, and slots.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: Custom Format Mini-Language
# ─────────────────────────────────────────────────────────────────────────────
# Implement `__format__` for a `Temperature` class.
# By default it should print in Celsius.
# If the format spec ends with 'F', convert to Fahrenheit.
# If it ends with 'K', convert to Kelvin.

class Temperature:
    def __init__(self, celsius: float):
        self.c = float(celsius)
        
    def __format__(self, fmt_spec: str) -> str:
        # TODO: Implement custom formatting
        if fmt_spec.endswith('F'):
            val = (self.c * 9/5) + 32
            spec = fmt_spec[:-1]
            return f"{format(val, spec)}°F"
        elif fmt_spec.endswith('K'):
            val = self.c + 273.15
            spec = fmt_spec[:-1]
            return f"{format(val, spec)}K"
        else:
            return f"{format(self.c, fmt_spec)}°C"

def test_ex1_formatting() -> None:
    section("Exercise 1: Custom Formatting")
    t = Temperature(25.0)
    
    res_c = f"{t:.1f}"
    res_f = f"{t:.1fF}"
    res_k = f"{t:.2fK}"
    
    print(f"Celsius:    {res_c}")
    print(f"Fahrenheit: {res_f}")
    print(f"Kelvin:     {res_k}")
    
    assert res_c == "25.0°C"
    assert res_f == "77.0°F"
    assert res_k == "298.15K"
    print("✓ Exercise 1 passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: Emulating Privacy with Name Mangling
# ─────────────────────────────────────────────────────────────────────────────
# Python doesn't have true private variables. Attributes starting with `__` 
# (and not ending with `__`) are "name mangled" to prevent accidental overriding.
# Create a class `Vault` with a mangled `__password`. Try to access it from 
# outside using the mangled name.

class Vault:
    def __init__(self, password: str):
        # TODO: Store the password using a double underscore
        self.__password = password

def test_ex2_name_mangling() -> None:
    section("Exercise 2: Name Mangling")
    v = Vault("super_secret")
    
    try:
        print(v.__password)
        assert False, "Should have raised AttributeError"
    except AttributeError:
        print("Blocked direct access to __password")
        
    # TODO: Access the mangled attribute. The format is _ClassName__attribute
    hacked_password = getattr(v, "_Vault__password")
    print(f"Hacked password: {hacked_password}")
    
    assert hacked_password == "super_secret"
    print("✓ Exercise 2 passed")


if __name__ == "__main__":
    test_ex1_formatting()
    test_ex2_name_mangling()
