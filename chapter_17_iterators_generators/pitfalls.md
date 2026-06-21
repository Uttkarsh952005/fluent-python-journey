# Chapter 17 — Pitfalls: Generators & Iterators

---

## Pitfall 1: Generator Exhaustion

Unlike lists or strings, generators are engines that produce values once and then die. They do not store their values.

```python
def process_data(data_generator):
    # Pass 1: We check if there are errors
    if any("ERROR" in row for row in data_generator):
        print("Errors found! Starting detailed analysis...")
        
    # BUG: Pass 2: The generator is now completely empty!
    for row in data_generator:
        print(f"Analyzing: {row}") # This loop will NEVER execute!

gen = (row for row in ["INFO", "ERROR", "DEBUG"])
process_data(gen)
```

**Why it fails:** The `any()` call advanced the generator via `next()`. By the time we hit the `for` loop, the generator has already raised `StopIteration`. It is exhausted forever.
**Fix:** If you must iterate multiple times, either materialize the generator into a list (`data = list(gen)`) or pass a function that returns a *new* generator each time.

---

## Pitfall 2: Memory Explosions from Eager Returns

A common mistake when trying to write "clean" helper functions is eagerly returning all results at once instead of yielding them.

```python
# BAD: Will instantly crash the server if the log file is 10GB
def find_errors_bad(filename):
    results = []
    with open(filename) as f:
        for line in f:
            if "ERROR" in line:
                results.append(line)
    return results

# GOOD: Server memory stays near 0MB, no matter the file size
def find_errors_good(filename):
    with open(filename) as f:
        for line in f:
            if "ERROR" in line:
                yield line
```

**Fix:** If a function processes an unbounded stream of data (logs, database rows, sockets), it must **never** return a list. It must always `yield`.

---

## Pitfall 3: The `yield from` Misunderstanding

Developers often think `yield from gen()` is just syntactic sugar for `for x in gen(): yield x`. 
It is not. `yield from` opens a direct, two-way channel between the sub-generator and the outermost caller. If the caller uses `.send()` or `.throw()`, a simple `for x in gen(): yield x` loop will crash because it intercepts the `.send()` but doesn't pass it down. `yield from` safely routes those advanced signals to the sub-generator.
