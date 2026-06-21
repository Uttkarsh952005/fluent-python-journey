"""
Chapter 19: Mini Project — Concurrent Web Scraper
=================================================
A practical demonstration of ThreadPoolExecutor for I/O-bound tasks.
Because `time.sleep` (and socket requests) release the GIL, threads 
provide massive speedups for network operations without the overhead 
of full multiprocessing.
"""

import sys
import time
from concurrent import futures

sys.stdout.reconfigure(encoding="utf-8")

# ─────────────────────────────────────────────────────────────────────────────
# Mock I/O Operations
# ─────────────────────────────────────────────────────────────────────────────

def download_image(image_id: int) -> str:
    """Simulates a slow network request (I/O bound)."""
    # time.sleep explicitly releases the GIL, allowing other threads to run
    time.sleep(0.5)
    return f"Image_{image_id}.jpg"

# ─────────────────────────────────────────────────────────────────────────────
# Sequential vs Concurrent Execution
# ─────────────────────────────────────────────────────────────────────────────

def download_sequential(image_ids: list[int]) -> list[str]:
    """Downloads one by one, blocking the main thread."""
    results = []
    for i in image_ids:
        results.append(download_image(i))
    return results

def download_concurrent(image_ids: list[int]) -> list[str]:
    """Uses a ThreadPool to download multiple images simultaneously."""
    results = []
    # ThreadPoolExecutor manages the threads for us securely
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        # map() assigns tasks to the pool and yields results in original order
        for result in executor.map(download_image, image_ids):
            results.append(result)
    return results

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Execution
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  ThreadPool I/O Pipeline")
    print("=" * 60)

    images = list(range(1, 11)) # 10 images to download
    
    print("\n1. Running Sequential Download (Should take ~5.0 seconds)")
    t0 = time.perf_counter()
    download_sequential(images)
    t1 = time.perf_counter()
    print(f"  Sequential time: {t1 - t0:.2f}s")
    
    print("\n2. Running Concurrent Download (Should take ~0.5 seconds)")
    t0 = time.perf_counter()
    download_concurrent(images)
    t1 = time.perf_counter()
    print(f"  Concurrent time: {t1 - t0:.2f}s")
    
    print("\nConclusion:")
    print("Because network requests release the GIL, threads are perfect")
    print("for parallelizing I/O. Multiprocessing is NOT required here!")

if __name__ == "__main__":
    main()
