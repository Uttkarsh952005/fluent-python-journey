# Chapter 21 — Pitfalls: Asynchronous Programming

---

## Pitfall 1: Forgetting to `await`

Because `async def` functions return Coroutine objects rather than executing immediately, forgetting the `await` keyword results in completely silent failures.

```python
async def fetch_database():
    print("Fetching data...")
    return {"status": "ok"}

async def main():
    # BUG: We forgot 'await'!
    # This evaluates to a Coroutine object, not the dictionary.
    data = fetch_database()
    
    # BUG: This will crash because 'data' is a coroutine object, not a dict.
    if data["status"] == "ok":
        print("Success")
```

**Fix:** You must always `await fetch_database()`. If you don't, Python will eventually print a warning: `RuntimeWarning: coroutine 'fetch_database' was never awaited`, but your code will still have failed.

---

## Pitfall 2: The Unbounded Concurrency Trap (DDoS'ing yourself)

If you use `concurrent.futures.ThreadPoolExecutor(max_workers=10)`, your concurrency is strictly capped at 10. `asyncio.gather` has no such cap.

```python
async def scrape(url):
    # Simulated network request
    pass

async def massive_scrape(urls):
    # BUG: If `urls` has 50,000 items, asyncio will instantly attempt
    # to open 50,000 TCP sockets. Your OS will crash with "Too Many Open Files"
    # or the target server will ban your IP address for a DDoS attack.
    tasks = [scrape(url) for url in urls]
    await asyncio.gather(*tasks)
```

**Fix:** You must introduce an `asyncio.Semaphore` to throttle your concurrency. See `mini_project.py` for the correct implementation.

---

## Pitfall 3: Using `requests` instead of `httpx`

Many developers start writing async APIs (like FastAPI) and continue using the legendary `requests` library.

**Why it fails:** `requests.get()` is a synchronous, blocking function. Because `asyncio` operates on a single thread, calling `requests.get()` will literally freeze every single other concurrent user on your server until that HTTP request finishes.
**Fix:** You must use an asynchronous HTTP client like `httpx.AsyncClient()` or `aiohttp.ClientSession()`.
