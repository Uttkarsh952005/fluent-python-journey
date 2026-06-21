"""
Chapter 20: Mini Project — Server Health Dashboard
==================================================
A responsive health checker that pings multiple servers concurrently.
By using `as_completed()`, we can update the dashboard the exact 
millisecond a server responds, rather than waiting for the slowest
server to finish before displaying any results.
"""

import sys
import time
import random
from concurrent import futures

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Mock Server Ping
# ─────────────────────────────────────────────────────────────────────────────

def ping_server(server_name: str) -> dict:
    """Simulates a network ping with highly variable latency."""
    if "Database" in server_name:
        # Simulate a slow database server
        time.sleep(2.0)
        status = "DEGRADED"
    else:
        # Simulate fast web servers
        time.sleep(random.uniform(0.1, 0.4))
        status = "ONLINE"
        
    return {"server": server_name, "status": status}

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Execution
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Live Server Health Dashboard")
    print("=" * 60)

    servers = [
        "Web_US_East", "Web_US_West", "Database_Primary", 
        "Cache_Redis", "Auth_Service"
    ]
    
    print("Pinging servers...")
    start_time = time.perf_counter()
    
    # We use max_workers=5 to ping all 5 servers simultaneously
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        
        # 1. Map futures to server names so we know which future is which
        future_to_server = {
            executor.submit(ping_server, server): server 
            for server in servers
        }
        
        # 2. Iterate over them as they complete out-of-order
        for future in futures.as_completed(future_to_server):
            server_name = future_to_server[future]
            try:
                data = future.result()
                elapsed = time.perf_counter() - start_time
                print(f"  [{elapsed:0.2f}s] {server_name:<18}: {data['status']}")
            except Exception as exc:
                print(f"  [ERROR] {server_name} generated an exception: {exc}")
                
    print(f"\nDashboard refresh complete in {time.perf_counter() - start_time:.2f}s.")

if __name__ == "__main__":
    main()
