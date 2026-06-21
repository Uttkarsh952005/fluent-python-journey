# Chapter 10 — Pitfalls: Design Patterns with First-Class Functions

---

## Pitfall 1: The "Java-in-Python" Anti-Pattern (Single Method Classes)

Developers coming from Java or C++ often bring their OOP baggage to Python, resulting in massive class hierarchies just to pass a single behavior.

```python
# DANGER: Massive boilerplate for a single behavior
class StringFormatter(ABC):
    @abstractmethod
    def format(self, text: str) -> str: pass

class UpperFormatter(StringFormatter):
    def format(self, text: str) -> str: return text.upper()

class LowerFormatter(StringFormatter):
    def format(self, text: str) -> str: return text.lower()
```

**Fix:** If a class only has an `__init__` and one other method, it should almost certainly be a function or a closure.
```python
def format_upper(text: str) -> str: return text.upper()
def format_lower(text: str) -> str: return text.lower()
```

---

## Pitfall 2: Forcing Functions When State is Complex

The reverse of Pitfall 1 is taking functional programming too far. If a function requires complex, mutable state that evolves over time, using a closure or `nonlocal` can quickly become unreadable.

```python
# DANGER: Unreadable state management in a closure
def create_complex_processor():
    cache = {}
    history = []
    
    def process(data):
        nonlocal cache, history
        # ... 50 lines of complex state mutations ...
        pass
        
    return process
```

**Fix:** If you need to manage multiple pieces of mutable state or expose multiple behaviors (methods) interacting with that state, **use a class**. Python is a multi-paradigm language; classes are excellent for stateful objects.

---

## Pitfall 3: Global State in Strategy Functions

Because functional strategies are often implemented as module-level functions, it is easy to accidentally rely on global variables.

```python
# DANGER: Global state breaks the Strategy pattern
ACTIVE_DISCOUNT = 0.2

def global_promo(order):
    return order.total * ACTIVE_DISCOUNT
```

**Fix:** Strategies must be pure functions relying only on their inputs, or closures that tightly encapsulate their specific state.

---

## Pitfall 4: Missing Type Hints on Callables

When replacing Abstract Base Classes with functions, you lose the IDE's ability to enforce the interface via inheritance.

```python
# DANGER: No signature enforcement
class Order:
    def __init__(self, strategy):
        self.strategy = strategy
```

**Fix:** You MUST use `typing.Callable` to restore the signature contract.
```python
from typing import Callable

class Order:
    def __init__(self, strategy: Callable[['Order'], float]):
        self.strategy = strategy
```
