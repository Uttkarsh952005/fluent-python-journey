"""
Chapter 9: Mini Project — Decorator-Based Rate Limiter
======================================================
A practical implementation of a rate-limiting decorator.
It uses closures to store state (request history) for each decorated
function independently.

Concepts demonstrated:
- Parameterized decorators
- Closures holding mutable state
- `functools.wraps`
"""

import sys
import time
import functools

sys.stdout.reconfigure(encoding="utf-8")

def rate_limit(max_calls: int, period_seconds: float):
    """
    A decorator factory that limits how often a function can be called.
    Allows `max_calls` within a sliding window of `period_seconds`.
    """
    def decorator(func):
        # State stored in the closure: a list of timestamps
        call_history: list[float] = []
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove timestamps older than our sliding window
            # We must use `call_history[:]` to modify the list in-place,
            # or `nonlocal` if we were reassigning `call_history`.
            call_history[:] = [t for t in call_history if now - t <= period_seconds]
            
            if len(call_history) >= max_calls:
                raise RuntimeError(
                    f"Rate limit exceeded for {func.__name__}. "
                    f"Max {max_calls} calls per {period_seconds}s."
                )
            
            # Record this call
            call_history.append(now)
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


# ─────────────────────────────────────────────────────────────────────────────
# Usage
# ─────────────────────────────────────────────────────────────────────────────

# Limit the API to 3 calls per 2.0 seconds
@rate_limit(max_calls=3, period_seconds=2.0)
def fetch_data(user_id: int) -> str:
    return f"Data payload for user {user_id}"

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Rate Limiting Decorator")
    print("=" * 60)

    print("Attempting 5 rapid requests...")
    
    for i in range(1, 6):
        try:
            res = fetch_data(i)
            print(f"Request {i}: SUCCESS -> {res}")
        except RuntimeError as e:
            print(f"Request {i}: BLOCKED -> {e}")
            
    print("\nSleeping for 2.1 seconds to reset the window...")
    time.sleep(2.1)
    
    try:
        res = fetch_data(6)
        print(f"Request 6: SUCCESS -> {res}")
    except RuntimeError as e:
        print(f"Request 6: BLOCKED -> {e}")

if __name__ == "__main__":
    main()
