# Chapter 17 — Architecture Notes: Generator Suspension

---

## 1. Stack vs. Heap Allocation for Frames

In almost all C programs (and by extension, standard CPython functions), execution frames are pushed onto the C-level call stack. When the function returns, the stack pointer decrements, immediately discarding the local variables.

Generators cannot work this way because their state must survive across multiple `next()` calls.
To solve this, CPython implements generator frames (`PyFrameObject`) as **heap-allocated objects**.
When a generator function is compiled, it is flagged with `CO_GENERATOR`. When called, instead of executing the bytecode, CPython creates a `PyFrameObject` on the heap, binds the local variables to it, and wraps it in a `PyGenObject`.

---

## 2. The `YIELD_VALUE` Opcode

When you run `next(gen)`, CPython pushes the `PyFrameObject` onto its evaluation loop (`_PyEval_EvalFrameDefault` in `Python/ceval.c`).

When the bytecode interpreter hits `YIELD_VALUE`:
1. It pops the top value off the generator's evaluation stack (this is the value you are yielding).
2. It saves the current instruction offset into `frame->f_lasti` (so it knows exactly where it paused).
3. It `return`s from the evaluation loop immediately.

Because the frame is on the heap, its reference count does not drop to 0. It sits in memory, safely preserved.

---

## 3. Resuming the Generator

When you call `next(gen)` again, the CPython loop looks at `frame->f_lasti`, jumps directly to that instruction offset, and continues executing as if nothing happened.
If you call `gen.send(value)`, CPython pushes `value` onto the top of the generator's evaluation stack *before* jumping to `f_lasti`. The generator wakes up, pops that value off the stack, and assigns it to whatever variable was waiting (e.g., `x = yield`).
