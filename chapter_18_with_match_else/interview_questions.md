# Chapter 18 — Interview Questions: Control Flow

---

## 🟢 L3

### Q1: What is the purpose of the `with` statement?
The `with` statement is used to wrap the execution of a block of code with methods defined by a context manager (`__enter__` and `__exit__`). It guarantees that teardown operations (like closing a file or releasing a lock) are executed even if an exception is raised inside the block. It is essentially syntactic sugar for a `try/finally` block.

---

## 🟡 L4

### Q2: What does the `else` clause do when attached to a `for` loop?
The `else` block executes if and only if the `for` loop ran to completion naturally without hitting a `break` statement. If the loop was interrupted by `break`, the `else` block is completely skipped. 

### Q3: When writing a context manager, how do you handle an exception inside `__exit__`?
The `__exit__` method receives three arguments: `exc_type`, `exc_val`, and `traceback`. If you want to swallow the exception (so the caller doesn't see it), you must explicitly `return True`. If you return `False` or `None` (the default behavior of missing returns), the exception will automatically propagate up to the caller after `__exit__` finishes.

---

## 🔴 L5

### Q4: Why is it an anti-pattern to put too much code inside a `try` block?
If you put non-risky code inside a `try` block, you risk accidentally catching exceptions that indicate genuine logic bugs. For example, if you catch `KeyError` for a dictionary lookup, but you also wrap a function call inside that same `try` block, a completely unrelated `KeyError` deep inside that function call might get caught and masked by your error handler. You should use a `try/except/else` structure to isolate the risky call and place the safe downstream logic in the `else` block.

---

## 🟣 L6

### Q5: How does `@contextmanager` inject exceptions into the generator?
When you use `@contextmanager`, CPython wraps your generator object. When entering the `with` block, it calls `next(gen)` to advance it to the `yield`. If an exception occurs inside the `with` block, the contextlib wrapper catches it and calls `gen.throw(exc_type, exc_val, traceback)`. This causes the exception to be raised exactly at the `yield` expression inside your generator function, which is why a `try/finally` block inside the generator is strictly required to handle the crash and execute teardown.
