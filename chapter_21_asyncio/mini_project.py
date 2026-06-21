"""
Chapter 21: Mini Project — Throttled Async Web Scraper
======================================================
A simulated high-performance web scraper.
Unlike ThreadPoolExecutor (which limits concurrency via max_workers),
asyncio will happily launch 10,000 concurrent requests if you let it,
which will instantly crash your OS with 'Too Many Open Files'.

This project demonstrates the mandatory architectural pattern for
bulk async processing: The Semaphore.
"""

import sys
import time
import asyncio
import random

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Mock Async Client
# ─────────────────────────────────────────────────────────────────────────────

async def fetch_url(url: str, semaphore: asyncio.Semaphore) -> str:
    """Fetches a URL, strictly limited by the Semaphore."""
    # The semaphore acts as a bouncer. If 5 coroutines are inside,
    # the 6th coroutine MUST wait here until one leaves.
    async with semaphore:
        # Simulate network latency
        await asyncio.sleep(random.uniform(0.05, 0.2))
        return f"200 OK: {url}"

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Execution
# ─────────────────────────────────────────────────────────────────────────────

async def main():
    print("=" * 60)
    print("  Throttled Async Web Scraper")
    print("=" * 60)

    # We have 20 URLs to scrape
    urls = [f"http://api.example.com/data/{i}" for i in range(20)]
    
    # CRITICAL: We only allow 5 concurrent connections to the target server
    # to avoid triggering their DDoS protection or crashing our OS sockets.
    concurrency_limit = 5
    semaphore = asyncio.Semaphore(concurrency_limit)
    print(f"Queueing 20 requests (Max Concurrency: {concurrency_limit})...")
    
    start_t = time.perf_counter()
    
    # 1. Create all 20 coroutines instantly (they don't run yet)
    tasks = [fetch_url(url, semaphore) for url in urls]
    
    # 2. Schedule them all concurrently
    # The Semaphore guarantees only 5 will actually execute the network call at once
    results = await asyncio.gather(*tasks)
    
    elapsed = time.perf_counter() - start_t
    print(f"Successfully scraped {len(results)} URLs in {elapsed:.2f}s!")
    print("\nSample Results:")
    for res in results[:3]:
        print(f"  {res}")

if __name__ == "__main__":
    asyncio.run(main())
