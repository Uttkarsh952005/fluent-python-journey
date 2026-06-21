"""
Chapter 13: Mini Project — A Protocol-Driven Plugin System
==========================================================
A practical demonstration of Static Duck Typing using `typing.Protocol`.
We build an extensible notification system where plugins do NOT need to 
inherit from a massive base class, but Mypy still provides 100% type safety.
"""

import sys
from typing import Protocol, List

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# The Protocol (Interface Definition)
# ─────────────────────────────────────────────────────────────────────────────
# We define the shape of a valid plugin. Plugins NEVER inherit from this.

class NotificationPlugin(Protocol):
    def send(self, message: str, recipient: str) -> bool:
        """Sends a message to a recipient. Returns True if successful."""
        ...

# ─────────────────────────────────────────────────────────────────────────────
# Concrete Plugins (No inheritance required!)
# ─────────────────────────────────────────────────────────────────────────────

class EmailPlugin:
    """An email sender. Matches the NotificationPlugin protocol structurally."""
    def send(self, message: str, recipient: str) -> bool:
        if "@" not in recipient:
            print(f"[Email] Failed: Invalid email address '{recipient}'")
            return False
        print(f"[Email] Sending to {recipient}: {message}")
        return True

class SMSPlugin:
    """An SMS sender. Matches the NotificationPlugin protocol structurally."""
    def send(self, message: str, recipient: str) -> bool:
        if not recipient.isdigit():
            print(f"[SMS] Failed: Invalid phone number '{recipient}'")
            return False
        print(f"[SMS] Texting {recipient}: {message}")
        return True

class BrokenPlugin:
    """FAILS the protocol because it takes the wrong arguments."""
    def send(self, message: str) -> bool:  # Missing 'recipient'
        print(f"[Broken] {message}")
        return True

# ─────────────────────────────────────────────────────────────────────────────
# The Core System
# ─────────────────────────────────────────────────────────────────────────────

class NotificationManager:
    def __init__(self):
        # Mypy will enforce that only compatible plugins enter this list
        self._plugins: List[NotificationPlugin] = []
        
    def register_plugin(self, plugin: NotificationPlugin) -> None:
        self._plugins.append(plugin)
        
    def broadcast(self, message: str, recipient: str) -> None:
        print(f"\n--- Broadcasting: '{message}' to {recipient} ---")
        for plugin in self._plugins:
            success = plugin.send(message, recipient)
            status = "OK" if success else "FAIL"
            print(f" -> Plugin {type(plugin).__name__} returned {status}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    manager = NotificationManager()
    
    # Registering valid plugins
    manager.register_plugin(EmailPlugin())
    manager.register_plugin(SMSPlugin())
    
    # If we ran Mypy, the following line would flag a static typing error!
    # manager.register_plugin(BrokenPlugin()) 
    
    manager.broadcast("System is going down for maintenance in 5 mins.", "admin@example.com")
    manager.broadcast("Your OTP is 49201", "5551234567")

if __name__ == "__main__":
    main()
