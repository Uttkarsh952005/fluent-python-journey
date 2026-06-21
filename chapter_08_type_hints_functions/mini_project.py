"""
Chapter 8: Mini Project — Typed Command Dispatcher
==================================================
A mini command dispatcher that registers and executes commands.
It heavily relies on the `Callable` type hint to enforce that registered
commands conform to expected signatures.

Concepts demonstrated:
- Callable[[ArgType], ReturnType]
- dict[str, Callable]
- Type aliasing
"""

import sys
from typing import Callable, Any

sys.stdout.reconfigure(encoding="utf-8")

# Define a type alias for our command signature
# A command must take a string and return a string
CommandFunc = Callable[[str], str]

class Dispatcher:
    """A registry for string manipulation commands."""
    
    def __init__(self):
        # Enforce that keys are strings and values are our CommandFunc alias
        self._commands: dict[str, CommandFunc] = {}
        
    def register(self, name: str, func: CommandFunc) -> None:
        """Registers a new command."""
        self._commands[name] = func
        
    def execute(self, name: str, payload: str) -> str:
        """Executes a command by name."""
        if name not in self._commands:
            raise ValueError(f"Unknown command: {name}")
        
        # Mypy knows `func` is a CommandFunc, so it expects a str and returns a str.
        func = self._commands[name]
        return func(payload)


# ─────────────────────────────────────────────────────────────────────────────
# Sample Commands
# ─────────────────────────────────────────────────────────────────────────────

def cmd_uppercase(payload: str) -> str:
    return payload.upper()

def cmd_reverse(payload: str) -> str:
    return payload[::-1]

def cmd_wrap(payload: str) -> str:
    return f"[{payload}]"

# Note: If we tried to register a function with a bad signature:
# def bad_cmd(x: int) -> int: return x * 2
# dispatcher.register("bad", bad_cmd)  # Mypy would flag this!


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Typed Command Dispatcher")
    print("=" * 60)

    disp = Dispatcher()
    
    # Registering commands
    disp.register("upper", cmd_uppercase)
    disp.register("reverse", cmd_reverse)
    disp.register("wrap", cmd_wrap)
    
    # Executing commands
    text = "Hello Typed World"
    print(f"Original: {text}")
    print(f"upper:    {disp.execute('upper', text)}")
    print(f"reverse:  {disp.execute('reverse', text)}")
    print(f"wrap:     {disp.execute('wrap', text)}")
    
    try:
        disp.execute("unknown", text)
    except ValueError as e:
        print(f"\nExpected error: {e}")

if __name__ == "__main__":
    main()
