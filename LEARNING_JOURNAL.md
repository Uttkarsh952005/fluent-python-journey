# 📓 Learning Journal — Fluent Python Journey

> A rolling log of insights, reflections, and engineering lessons discovered chapter by chapter.
> Updated with every significant learning milestone.

---

## Week 1 — June 2026

### Chapter 1: The Python Data Model

**Date**: 2026-06-19  
**Status**: ✅ Complete

#### What I Actually Learned (Beyond the Book)

The most important insight from Chapter 1 isn't the `FrenchDeck` example itself — it's the **principle behind it**. Python's data model is essentially a framework of hooks. When you implement `__len__` and `__getitem__`, you're not just enabling `len()` and indexing — you're buying into an entire ecosystem:

- `random.choice()` works because it calls `len()` and `__getitem__`
- `reversed()` works on any sequence that has both
- `in` operator falls back to sequential `__getitem__` if `__contains__` is missing

This is **duck typing in its purest form** — Python doesn't check *what you are*, it checks *what you can do*.

#### The CPython Detail That Surprised Me

`len()` doesn't actually call `obj.__len__()` in most cases. For built-in types (list, dict, str, etc.), CPython invokes `sq_length` or `mp_length` directly at the C level, bypassing the Python method lookup entirely. This is why `len([1,2,3])` is dramatically faster than `[1,2,3].__len__()` on built-ins — the latter triggers Python's attribute lookup machinery.

For user-defined classes, `len()` *does* dispatch to `__len__()`, but via `type.__call__` — still faster than manual attribute access.

#### Benchmark Insight
- `len(lst)` on a built-in list: ~50ns
- `lst.__len__()` on a built-in list: ~80ns (attribute lookup overhead)
- `len(custom_obj)` on a user class: ~90ns (Python dispatch)

#### Architectural Decision: Why Protocols > Inheritance

Python chose **structural subtyping (protocols)** over **nominal subtyping (inheritance)** for the standard library. A class doesn't need to inherit from `Sequence` to work as one — it just needs `__len__` and `__getitem__`. This keeps the standard library open to extension without tight coupling.

Java would require `implements Sequence`. Python just asks: *can you do what a sequence does?*

#### What I'll Explore Next
- How `__repr__` vs `__str__` differs in exception contexts
- The `__format__` protocol and its relationship with f-strings
- How `__bool__` interacts with `__len__` (truthiness fallback chain)

---

### Looking Ahead: Chapter 2 — An Array of Sequences

**Key questions I want to answer:**
1. When should I use `array.array` over `list`? (Memory, type safety, performance)
2. How does Python's slicing actually work at the C level?
3. Is `memoryview` ever practical in real applications, or is it just a benchmark curiosity?
4. What's the actual performance difference between list comprehensions and generator expressions in different scenarios?

---

## Template for Future Entries

```markdown
### Chapter X: [Title]

**Date**: YYYY-MM-DD
**Status**: ✅ Complete / 🔄 In Progress

#### What I Actually Learned (Beyond the Book)
[Insight that surprised you or challenged assumptions]

#### The CPython Detail That Surprised Me
[One low-level implementation detail worth remembering]

#### Benchmark Insight
[One concrete performance number with context]

#### Architectural Decision
[One design decision Python made and WHY it made it]

#### What I'll Explore Next
[Open questions to carry into the next chapter]
```

---

*This journal is evidence that learning happened — not just that code was written.*
