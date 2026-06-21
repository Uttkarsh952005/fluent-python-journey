"""
Chapter 14: Mini Project — A Modular Web Request System (Mixins)
================================================================
A practical demonstration of Cooperative Multiple Inheritance and Mixins.
Instead of a deep, rigid inheritance tree (BaseRequest -> LoggedRequest -> 
JSONLoggedRequest), we use Mixins to *compose* behavior cleanly.
"""

import sys
import json
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Core Classes
# ─────────────────────────────────────────────────────────────────────────────

class BaseRequestHandler:
    """The root of the handler hierarchy."""
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.status = "initialized"

    def handle(self, payload: dict):
        self.status = "handled"
        return f"Processed {len(payload)} bytes at {self.endpoint}"


# ─────────────────────────────────────────────────────────────────────────────
# Mixins (Composition over Inheritance)
# ─────────────────────────────────────────────────────────────────────────────

class LoggingMixin:
    """A mixin that intercepts the handle() call to add logging."""
    
    def handle(self, payload: dict):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] LoggingMixin: Request received for {getattr(self, 'endpoint', 'Unknown')}")
        
        # COOPERATIVE DELEGATION: Call the next class in the MRO!
        result = super().handle(payload)
        
        print(f"[{timestamp}] LoggingMixin: Request completed with status '{self.status}'")
        return result


class JSONValidationMixin:
    """A mixin that ensures the payload has a specific schema before processing."""
    
    def handle(self, payload: dict):
        print("  -> JSONValidationMixin: Validating schema...")
        if "user_id" not in payload:
            raise ValueError("Payload missing required 'user_id' field")
            
        # COOPERATIVE DELEGATION
        return super().handle(payload)


# ─────────────────────────────────────────────────────────────────────────────
# Concrete Implementation
# ─────────────────────────────────────────────────────────────────────────────

class SecureAPIHandler(LoggingMixin, JSONValidationMixin, BaseRequestHandler):
    """
    A concrete class composed of Mixins.
    Notice the MRO: SecureAPIHandler -> LoggingMixin -> JSONValidationMixin -> BaseRequestHandler -> object
    """
    pass


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Mixin-based Request Pipeline")
    print("=" * 60)

    handler = SecureAPIHandler(endpoint="/api/v1/users")
    
    # 1. Inspect the MRO
    print("MRO Linearization:")
    for i, cls in enumerate(type(handler).__mro__):
        print(f"  {i}. {cls.__name__}")
    
    print("\nExecuting Pipeline:")
    try:
        # 2. Process a valid payload
        response = handler.handle({"user_id": 402, "action": "update"})
        print(f"\nResponse: {response}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
