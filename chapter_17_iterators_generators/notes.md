# Chapter 17: Iterators, Generators, and Classic Coroutines — Notes

## 1. Iterable vs. Iterator
These two terms are constantly confused, but the distinction is mathematically strict in Python.
*   **Iterable**: Any object that has an `__iter__` method returning an *Iterator*. Lists, tuples, and strings are Iterables. They hold data.
*   **Iterator**: Any object that implements `__next__` (to return the next item or raise `StopIteration`) AND `__iter__` (which just returns `self`). Iterators are the engine that powers the `for` loop.

## 2. The `yield` Keyword
The moment you write the word `yield` anywhere inside a function, Python completely changes the nature of that function.
*   It is no longer a normal function. It is a **Generator Function**.
*   When called, it does NOT execute its body. It immediately returns a **Generator Object**.
*   Execution only starts when you call `next()` on that generator object.
*   `yield` literally suspends the execution state (local variables, instruction pointers) in CPython and returns control to the caller.

## 3. The `yield from` Keyword
Introduced in Python 3.3, `yield from subgen()` does more than just `for x in subgen(): yield x`. 
It opens a completely transparent, two-way communication channel between the outermost caller and the innermost sub-generator. If the caller calls `.send()`, `.throw()`, or `.close()`, those calls bypass the delegating generator entirely and are passed directly to the sub-generator.

## 4. Classic Coroutines
A generator naturally *produces* data. A coroutine is a generator used to *consume* data.
By writing `val = yield`, you tell the generator to pause and wait. The caller can then push data into the suspended generator using `coroutine.send(data)`.
**Crucial Rule:** You must always "prime" a coroutine by calling `next(coro)` or `coro.send(None)` before you can send actual data into it. You have to advance the generator to the first `yield` so it is ready to receive.
