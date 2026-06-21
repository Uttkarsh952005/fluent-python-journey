# Chapter 17 — Interview Questions: Generators and Coroutines

---

## 🟢 L3

### Q1: What is the difference between an Iterable and an Iterator?
An **Iterable** is any object that holds data and can be iterated over (like a list or string). It implements `__iter__` which returns an Iterator.
An **Iterator** is the stateful engine that actually fetches the data. It implements `__next__` to return the next value (or raise `StopIteration`) and `__iter__` which returns itself.

### Q2: What happens when you call a function containing the `yield` keyword?
It does **not** execute the function body. Instead, it immediately returns a Generator Object. The function's code only begins executing when you pass that generator object into `next()` or a `for` loop.

---

## 🟡 L4

### Q3: Why is `yield from` useful? Why not just use a `for` loop to yield items from a sub-generator?
While a `for` loop (`for x in subgen(): yield x`) works for pulling data *out* of a generator, it breaks if you are treating the generator as a coroutine and pushing data *in* (via `.send()` or `.throw()`). `yield from` creates a transparent, two-way pipe that correctly forwards `.send()` and `.throw()` from the caller directly into the inner sub-generator.

---

## 🔴 L5

### Q4: Why must you "prime" a coroutine before sending data into it?
When you instantiate a coroutine generator, the instruction pointer is paused at the very top of the function. It has not yet reached the `val = yield` statement, which is the point where it suspends and waits for data. By calling `next(coro)` (or `coro.send(None)`), you advance the execution so it suspends at the `yield`, making it ready to catch the first incoming value.

---

## 🟣 L6

### Q5: How does CPython handle the local state of a generator when it suspends?
When a normal function executes, its local variables live on the C stack and are destroyed when the function returns. 
When a generator is created, CPython allocates a `PyFrameObject` on the **heap**, not the stack. This frame contains all local variables and the instruction pointer (`f_lasti`). When `YIELD_VALUE` is executed, CPython simply pauses the evaluation loop and returns the value, leaving the heap-allocated frame perfectly intact. When `next()` is called again, CPython loads that exact frame back into the evaluation loop and resumes from `f_lasti`.
