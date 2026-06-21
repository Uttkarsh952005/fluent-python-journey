"""
Chapter 17: Mini Project — Data Pipeline via Generator Chaining
===============================================================
A practical implementation of a lazy log-processing pipeline using 
chained generators. This mirrors a Unix `grep | awk` pipeline, 
processing data entirely lazily with O(1) memory consumption.
"""

import sys
from typing import Iterator

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Components (Generators)
# ─────────────────────────────────────────────────────────────────────────────

def read_logs_mock() -> Iterator[str]:
    """Simulates tailing a massive log file or reading from a socket."""
    logs = [
        "INFO: System booted successfully.",
        "DEBUG: Cache miss for user_id=45",
        "ERROR: Database connection timeout! (retry=1)",
        "WARN: Disk usage at 85%",
        "ERROR: Payment gateway declined (code: 402)"
    ]
    for line in logs:
        yield line

def filter_errors(lines: Iterator[str]) -> Iterator[str]:
    """Filters lines to only include ERROR logs."""
    for line in lines:
        if "ERROR:" in line:
            yield line

def extract_messages(lines: Iterator[str]) -> Iterator[str]:
    """Strips the severity prefix to get the raw message."""
    for line in lines:
        yield line.split("ERROR:", 1)[1].strip()

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Execution
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Generator Pipeline (Log Processor)")
    print("=" * 60)

    # 1. Chain the generators together.
    # Notice that NO data is processed yet. These are just suspended objects.
    log_stream = read_logs_mock()
    error_stream = filter_errors(log_stream)
    message_stream = extract_messages(error_stream)
    
    print("Generators initialized. Starting pipeline pull...\n")
    
    # 2. Pull the data through the pipeline
    # The `for` loop calls `next()` on message_stream, which pulls from 
    # error_stream, which pulls from log_stream.
    for msg in message_stream:
        print(f"Alert Triggered: {msg}")

if __name__ == "__main__":
    main()
