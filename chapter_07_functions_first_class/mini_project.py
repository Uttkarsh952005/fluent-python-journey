"""
Chapter 7: Mini Project — Functional Rule Engine
=================================================
A practical application of first-class functions to build a flexible, 
pluggable rule engine for password validation.

Concepts demonstrated:
- Functions as rules (data)
- State-holding callables (__call__)
- Higher-order evaluation (all/any)
- functools.partial for rule configuration
"""

import sys
from typing import Callable
from functools import partial

sys.stdout.reconfigure(encoding="utf-8")

# A Rule is any callable that takes a string and returns a boolean
Rule = Callable[[str], bool]

# ─────────────────────────────────────────────────────────────────────────────
# Simple Functional Rules
# ─────────────────────────────────────────────────────────────────────────────

def has_upper(s: str) -> bool:
    return any(c.isupper() for c in s)

def has_lower(s: str) -> bool:
    return any(c.islower() for c in s)

def has_digit(s: str) -> bool:
    return any(c.isdigit() for c in s)

# ─────────────────────────────────────────────────────────────────────────────
# Parameterized Rules (Higher-Order & Partial)
# ─────────────────────────────────────────────────────────────────────────────

def min_length(length: int, s: str) -> bool:
    return len(s) >= length

def has_special(chars: str, s: str) -> bool:
    return any(c in chars for c in s)

# ─────────────────────────────────────────────────────────────────────────────
# Stateful Rule (__call__)
# ─────────────────────────────────────────────────────────────────────────────

class DictionaryChecker:
    """A callable class that keeps state (the loaded dictionary)."""
    def __init__(self, bad_words: list[str]):
        self.bad_words = set(w.lower() for w in bad_words)
        
    def __call__(self, s: str) -> bool:
        # Fails if the password contains any dictionary word
        s_lower = s.lower()
        return not any(bad in s_lower for bad in self.bad_words)

# ─────────────────────────────────────────────────────────────────────────────
# The Engine
# ─────────────────────────────────────────────────────────────────────────────

class PasswordValidator:
    def __init__(self):
        self.rules: list[tuple[str, Rule]] = []
        
    def add_rule(self, name: str, rule: Rule) -> None:
        """Treats the rule function as a first-class object."""
        self.rules.append((name, rule))
        
    def validate(self, password: str) -> list[str]:
        """Returns a list of failed rule names. Empty list means success."""
        # Using a functional approach: filter for rules that fail
        failures = [name for name, rule in self.rules if not rule(password)]
        return failures


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Functional Password Validator")
    print("=" * 60)

    validator = PasswordValidator()
    
    # Registering pure functions
    validator.add_rule("Must have uppercase", has_upper)
    validator.add_rule("Must have lowercase", has_lower)
    validator.add_rule("Must have digit", has_digit)
    
    # Registering parameterized functions using partial
    validator.add_rule("Min length 8", partial(min_length, 8))
    validator.add_rule("Must have special char", partial(has_special, "!@#$%^&*"))
    
    # Registering a stateful callable
    no_dict = DictionaryChecker(["password", "admin", "qwerty", "1234"])
    validator.add_rule("No dictionary words", no_dict)

    # Test cases
    passwords = [
        "short",
        "password123",
        "Admin!23",
        "S3cr3t!P@ssw0rd"
    ]
    
    for pwd in passwords:
        failures = validator.validate(pwd)
        print(f"\nPassword: '{pwd}'")
        if not failures:
            print("  ✓ VALID")
        else:
            print(f"  ✗ INVALID. Failed rules:")
            for f in failures:
                print(f"    - {f}")


if __name__ == "__main__":
    main()
