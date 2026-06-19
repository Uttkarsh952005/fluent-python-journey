# Chapter 2 — Pitfalls: Sequences

## Pitfall 1: List Multiplication Creates Shared References

### The Mistake
```python
# Create a 3x3 grid
grid = [[0] * 3] * 3  # ❌ WRONG — shares inner lists!
grid[0][0] = 1

print(grid)
# [[1, 0, 0], [1, 0, 0], [1, 0, 0]]  ← All rows changed!
```

### Why It Happens
`[inner_list] * 3` creates a list of THREE REFERENCES to the SAME inner list object. Modifying one "row" modifies all rows.

### The Fix
```python
# ✅ CORRECT: each row is a distinct object
grid = [[0] * 3 for _ in range(3)]
grid[0][0] = 1
print(grid)
# [[1, 0, 0], [0, 0, 0], [0, 0, 0]]  ← Only first row changed
```

**Rule**: `obj * n` for immutable objects (int, str) is safe. For mutable objects in a list, always use a comprehension.

---

## Pitfall 2: Iterating While Modifying

### The Mistake
```python
numbers = [1, 2, 3, 4, 5, 6]

# Remove even numbers
for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)  # ❌ Modifying while iterating!

print(numbers)  # [1, 3, 5] — WRONG! Missing some evens
```

### Why It Happens
When you `remove(2)`, element 3 slides left to index 1. The for loop then moves to index 2 (which is now 4), skipping 3. Python's list iterator advances by index, not by element identity.

### The Fix
```python
# ✅ Option 1: filter (creates new list)
numbers = [n for n in numbers if n % 2 != 0]

# ✅ Option 2: iterate over a copy
for num in list(numbers):  # list() makes a copy
    if num % 2 == 0:
        numbers.remove(num)
```

---

## Pitfall 3: Relying on `+=` Returning the Same Object for Immutables

### The Mistake
```python
def add_item(container, item):
    container += [item]  # Returns new tuple if immutable!

my_tuple = (1, 2, 3)
add_item(my_tuple, 4)
print(my_tuple)  # (1, 2, 3) ← Unchanged! Function saw a new binding
```

### Why It Happens
`container += [item]` for a tuple creates a new object and rebinds the LOCAL variable `container`. The caller's `my_tuple` still points to the original. For mutable types (list), `__iadd__` modifies in place — the original object changes.

### The Fix
```python
# ✅ For mutable: explicit method or return the new value
def add_item(container: list, item: int) -> None:
    container.append(item)  # Modifies in place — no rebinding

# ✅ For immutable: return the new value
def add_to_tuple(t: tuple, item: int) -> tuple:
    return t + (item,)  # Caller updates their variable
```

---

## Pitfall 4: `list.pop(0)` in a Loop

### The Mistake
```python
queue = list(range(1000))

# Process items FIFO:
while queue:
    item = queue.pop(0)  # ❌ O(n) — shifts all elements left each time!
    process(item)
# Total cost: O(n²) — catastrophic for large queues
```

### The Fix
```python
from collections import deque

queue = deque(range(1000))

while queue:
    item = queue.popleft()  # ✅ O(1) — no shifting
    process(item)
# Total cost: O(n)
```

---

## Pitfall 5: Slicing a List Creates a Shallow Copy

### The Mistake
```python
original = [[1, 2], [3, 4], [5, 6]]
sliced = original[0:2]  # ← Looks like a safe copy

sliced[0].append(99)  # Modifying inner list

print(original)  # [[1, 2, 99], [3, 4], [5, 6]] ← original changed!
```

### Why It Happens
List slicing creates a **shallow copy**: a new list object containing the same references as the original. The inner lists are not copied — both `original[0]` and `sliced[0]` point to the same list object.

### The Fix
```python
import copy

# ✅ Shallow copy — new outer list, same inner objects
shallow = original[:]
# ✅ Deep copy — completely independent
deep = copy.deepcopy(original)
```

**When shallow copy is OK**: If inner objects are immutable (integers, strings, tuples). Only matters for nested mutable structures.

---

## Pitfall 6: Generator Exhaustion

### The Mistake
```python
gen = (x**2 for x in range(10))
total = sum(gen)         # Consumes the generator
max_val = max(gen)       # ← Returns max of nothing! Empty generator!
```

### Why It Happens
Generators are **stateful, one-pass iterators**. Once exhausted, they return nothing — they don't reset.

### The Fix
```python
# ✅ Option 1: materialize to list if you need multiple passes
squares = [x**2 for x in range(10)]
total = sum(squares)
max_val = max(squares)

# ✅ Option 2: use itertools.tee() to duplicate the generator
from itertools import tee
gen1, gen2 = tee(x**2 for x in range(10))  # Creates two parallel iterators
```

---

## Interview Relevance

These pitfalls map directly to common interview questions:
- "Why is `pop(0)` on a list slow?" → Pitfall 4 (O(n) shift)
- "What's wrong with `[[]] * n`?" → Pitfall 1 (shared references)  
- "Is slicing a list safe from mutation?" → Pitfall 5 (shallow copy)
- "What happens when you exhaust a generator twice?" → Pitfall 6
