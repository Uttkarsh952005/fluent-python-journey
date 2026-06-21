"""
Chapter 24: Mini Project — Dependency Injection Framework
=========================================================
A simulated Dependency Injection framework using Metaclasses.
Instead of forcing developers to manually instantiate database
connections or loggers in every service, the Metaclass intercepts
the class creation and automatically injects them.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Mocks
# ─────────────────────────────────────────────────────────────────────────────

class MockDatabase:
    def execute(self, query):
        return f"[DB] Executed: {query}"

class MockLogger:
    def log(self, message):
        print(f"  [LOG] {message}")

# ─────────────────────────────────────────────────────────────────────────────
# The Metaclass Framework
# ─────────────────────────────────────────────────────────────────────────────

class DependencyInjectorMeta(type):
    """
    A Metaclass that automatically injects a `db` and `logger` attribute
    into any class that uses it.
    """
    def __new__(meta_cls, cls_name, bases, cls_dict):
        # Inject dependencies directly into the class dictionary
        cls_dict['db'] = MockDatabase()
        cls_dict['logger'] = MockLogger()
        
        # We can also dynamically wrap methods!
        # Let's wrap the __init__ method to log when the service starts.
        original_init = cls_dict.get('__init__')
        
        def new_init(self, *args, **kwargs):
            self.logger.log(f"Initializing {cls_name} Service...")
            if original_init:
                original_init(self, *args, **kwargs)
                
        cls_dict['__init__'] = new_init
        
        return super().__new__(meta_cls, cls_name, bases, cls_dict)


class BaseService(metaclass=DependencyInjectorMeta):
    """All business logic services will inherit from this."""
    pass

# ─────────────────────────────────────────────────────────────────────────────
# The Consumer (Business Logic)
# ─────────────────────────────────────────────────────────────────────────────

class UserService(BaseService):
    """
    Notice how clean this is! The developer doesn't have to define a 
    database or logger. The Metaclass already put them there.
    """
    def fetch_user(self, user_id):
        self.logger.log(f"Fetching user {user_id}...")
        result = self.db.execute(f"SELECT * FROM users WHERE id={user_id}")
        print(f"  {result}")


def main():
    print("=" * 60)
    print("  Metaclass Dependency Injection")
    print("=" * 60)

    # 1. Instantiation triggers the dynamically wrapped __init__
    service = UserService()
    
    # 2. Execution utilizes the dynamically injected `db` and `logger`
    service.fetch_user(101)


if __name__ == "__main__":
    main()
