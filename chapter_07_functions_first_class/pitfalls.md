# Chapter 7 — Pitfalls: Functions as First-Class Objects

---

## Pitfall 1: Exhausting `map` and `filter` Generators

In Python 2, `map()` and `filter()` returned lists. In Python 3, they return **lazy iterators** (generators). A common bug is trying to consume them twice.

```python
data = [1, 2, 3, 4]
results = map(lambda x: x * 2, data)

print(list(results))  # [2, 4, 6, 8]
print(list(results))  # []  ← BUG: Iterator is exhausted!
```

**Fix:** If you need the data multiple times, use a list comprehension or explicitly cast to a list: `results = list(map(...))`.

---

## Pitfall 2: The Lambda Loop Binding Trap (Late Binding)

This is one of the most famous bugs in Python functional programming.

```python
# Goal: Create a list of 5 functions, where the i-th function returns i.
funcs = [lambda: i for i in range(5)]

print(funcs[0]())  # Expect 0, but prints 4!
print(funcs[2]())  # Expect 2, but prints 4!
```

**Why?** Python's closures use **late binding**. The `lambda` does not evaluate `i` when the function is *created*; it looks up `i` when the function is *called*. By the time you call them, the loop has finished, and `i` is `4`.

**Fix:** Bind the variable eagerly using a default argument.
```python
funcs = [lambda i=i: i for i in range(5)]
```

---

## Pitfall 3: Overusing `lambda`

Python limits lambdas to a single expression. Developers often bend over backward to cram complex logic into a lambda (using nested `and`/`or` hacks, inline comprehensions, etc.).

```python
# Unreadable production bug waiting to happen:
process = lambda d: (d.get('id'), [x for x in d.get('items', []) if x.is_valid()])

# Fix: Use a proper def. It's fully first-class anyway!
def process(d):
    items = [x for x in d.get('items', []) if x.is_valid()]
    return d.get('id'), items
```

**Rule of Thumb (Fredrik Lundh):** If you have to write a comment explaining a lambda, it should be a `def`.

---

## Pitfall 4: Confusion Between Functions and Methods

When dealing with higher-order functions, it's easy to pass an unbound method when a bound method is required.

```python
class Worker:
    def do_work(self):
        print("Working")

workers = [Worker(), Worker()]

# TypeError: do_work() missing 1 required positional argument: 'self'
map(Worker.do_work, workers)  
```

**Fix 1:** Use `operator.methodcaller`.
```python
from operator import methodcaller
list(map(methodcaller('do_work'), workers))
```

**Fix 2:** Use a list comprehension.
```python
[w.do_work() for w in workers]
```
