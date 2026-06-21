"""
Chapter 18: Mini Project — Database Transaction Manager
=======================================================
A professional-grade implementation of a context manager that handles
database transactions. It automatically commits if the block succeeds,
and automatically rolls back if an exception is raised.
"""

import sys
from contextlib import contextmanager

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Mock Database Connection
# ─────────────────────────────────────────────────────────────────────────────

class MockDatabaseConnection:
    def __init__(self):
        self.state = "connected"
        self.transactions_committed = 0
        self.transactions_rolled_back = 0
        
    def execute(self, query):
        if "DROP" in query.upper():
            raise ValueError(f"Dangerous query detected: {query}")
        print(f"  [DB] Executing: {query}")

    def commit(self):
        self.transactions_committed += 1
        print("  [DB] COMMIT successful.")
        
    def rollback(self):
        self.transactions_rolled_back += 1
        print("  [DB] ROLLBACK successful. Data preserved.")
        
    def close(self):
        self.state = "closed"
        print("  [DB] Connection securely closed.")

# ─────────────────────────────────────────────────────────────────────────────
# The Context Manager
# ─────────────────────────────────────────────────────────────────────────────

@contextmanager
def transaction():
    """
    A transactional context manager.
    Yields a live database connection.
    Commits on success, rolls back on exception, and closes safely.
    """
    conn = MockDatabaseConnection()
    try:
        # Pass the connection to the user's `with` block
        yield conn
        # If the block finishes without errors, we arrive here
        conn.commit()
    except Exception as e:
        # If ANY error happens in the `with` block, we catch it here
        print(f"  [CM] Caught exception: {e}")
        conn.rollback()
        # We must re-raise the exception so the caller knows it failed
        raise
    finally:
        # This will ALWAYS run, whether we hit the commit or the rollback
        conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Execution
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Transaction Manager Pipeline")
    print("=" * 60)

    print("\n--- Scenario 1: The Happy Path ---")
    with transaction() as db:
        db.execute("INSERT INTO users (name) VALUES ('Alice')")
        db.execute("UPDATE stats SET count = count + 1")
        
    print("\n--- Scenario 2: The Exception Path ---")
    try:
        with transaction() as db:
            db.execute("INSERT INTO users (name) VALUES ('Bob')")
            # This will trigger our ValueError inside the DB mock
            db.execute("DROP TABLE users")
    except ValueError:
        print("  [Main] Application handled the dropped exception.")

if __name__ == "__main__":
    main()
