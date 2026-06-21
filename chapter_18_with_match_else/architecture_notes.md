# Chapter 18 — Architecture Notes: `sys.exc_info()` and the `with` Block

---

## 1. The Dunder Exit Arguments

Why does the `__exit__` method take exactly three arguments (`exc_type`, `exc_val`, `traceback`) instead of just one exception object?

Before Python 3, exceptions were not objects in the way they are today. String exceptions were valid in very early versions of Python. To handle the metadata of an exception safely, CPython tracked exceptions globally per-thread.

The three arguments passed to `__exit__` map exactly to the tuple returned by `sys.exc_info()`.
When an exception occurs inside a `with` block, the interpreter suspends the exception propagation, grabs the current `exc_info()` tuple from the thread state, unpacks it, and passes it directly to `__exit__`.

---

## 2. The `SETUP_WITH` Opcode

In CPython, the `with` statement has a dedicated bytecode instruction called `SETUP_WITH`.
When the interpreter hits `SETUP_WITH`, it:
1. Calls `__enter__` on the context manager.
2. Pushes a "finally" block onto the block stack.
3. Takes the return value of `__enter__` and pushes it to the evaluation stack so it can be bound to the `as` variable via a `STORE_FAST` opcode.

If the block completes, it calls `__exit__(None, None, None)`.
If an exception is raised, the interpreter unwinds the block stack, finds the `with` finally block, and pushes the exception tuple onto the stack, calling `__exit__` with those arguments.

---

## 3. Contextlib and `gen.throw`

The `@contextmanager` decorator converts a simple generator into a context manager using the `_GeneratorContextManager` wrapper class.
Its `__exit__` method looks roughly like this (simplified from `contextlib.py`):

```python
def __exit__(self, type, value, traceback):
    if type is None:
        try:
            next(self.gen)
        except StopIteration:
            return False
        else:
            raise RuntimeError("generator didn't stop")
    else:
        try:
            # Here is the magic injection
            self.gen.throw(type, value, traceback)
            raise RuntimeError("generator didn't stop after throw()")
        except StopIteration as exc:
            return exc is not value
```

This source code proves why the `try/finally` inside the generator is mandatory. If an exception occurs, the wrapper literally `.throw()`s it directly into the `yield` statement. If there is no `finally` block to catch it, the generator aborts, and teardown is skipped.
