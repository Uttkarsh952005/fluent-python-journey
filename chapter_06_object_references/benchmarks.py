"""
Chapter 6: Benchmarks — Object References
==========================================
Measures: is vs ==, copy vs deepcopy, aliasing overhead
Run: python benchmarks.py
"""
import sys
import copy
import timeit

sys.stdout.reconfigure(encoding="utf-8")

N = 500_000


def section(title: str) -> None:
    print(f"\n{'=' * 55}\n  {title}\n{'=' * 55}")


def measure(stmt: str, setup: str, n: int = N) -> float:
    return (timeit.timeit(stmt, setup=setup, number=n) / n) * 1e9


# ── Benchmark 1: is vs == ─────────────────────────────────────────────────────

section("Benchmark 1: is vs ==")
print("  (is cannot be overloaded; == calls __eq__)\n")

setup_none = "x = None"
setup_list = "x = [1, 2, 3]; y = [1, 2, 3]"
setup_str  = "x = 'hello'; y = 'hello'"

t_is_none  = measure("x is None",  setup_none)
t_eq_none  = measure("x == None",  setup_none)
t_is_list  = measure("x is y",     setup_list)
t_eq_list  = measure("x == y",     setup_list)
t_is_str   = measure("x is y",     setup_str)
t_eq_str   = measure("x == y",     setup_str)

print(f"  {'Operation':<30} {'ns/op':>8}")
print("  " + "-" * 40)
print(f"  {'x is None':<30} {t_is_none:>8.1f}")
print(f"  {'x == None':<30} {t_eq_none:>8.1f}  ← {'%.1f'%(t_eq_none/t_is_none)}x slower")
print(f"  {'[1,2,3] is [1,2,3]':<30} {t_is_list:>8.1f}")
print(f"  {'[1,2,3] == [1,2,3]':<30} {t_eq_list:>8.1f}  ← {'%.1f'%(t_eq_list/t_is_list)}x slower (traverses items)")
print(f"  {'str is str':<30} {t_is_str:>8.1f}")
print(f"  {'str == str':<30} {t_eq_str:>8.1f}")
print("""
  is is always faster — it's a single integer comparison (id(a) == id(b)).
  == can trigger expensive __eq__ traversal for large containers.
  Use is ONLY for None/sentinel checks.
""")


# ── Benchmark 2: copy vs deepcopy ─────────────────────────────────────────────

section("Benchmark 2: copy.copy vs copy.deepcopy")
print("  (flat list, then nested list, then deeply nested)\n")

setups = {
    "flat list [1..100]":
        "import copy; x = list(range(100))",
    "nested [[1..10]] x 10":
        "import copy; x = [list(range(10)) for _ in range(10)]",
    "3-level nested":
        "import copy; x = [[[i for i in range(5)] for _ in range(5)] for _ in range(5)]",
}

print(f"  {'Structure':<30} {'copy':>10} {'deepcopy':>10} {'ratio':>8}")
print("  " + "-" * 62)

for label, setup in setups.items():
    t_copy = measure("copy.copy(x)", setup, n=100_000)
    t_deep = measure("copy.deepcopy(x)", setup, n=50_000)
    print(f"  {label:<30} {t_copy:>10.0f} {t_deep:>10.0f} {t_deep/t_copy:>8.1f}x")

print("""
  deepcopy is significantly slower — it must:
  1. Recursively traverse the entire object graph
  2. Maintain a memo dict to handle cyclic references
  3. Create new objects at every level

  Use shallow copy when inner objects are immutable (str, int, tuple).
  Use deepcopy only when you need full independence from the original.
""")


# ── Benchmark 3: Alias vs copy in tight loop ─────────────────────────────────

section("Benchmark 3: Alias vs copy — per-iteration cost")
print("  (cost of creating aliases vs copies in a loop)\n")

N2 = 100_000
t_alias    = measure("y = x",            "x = [1,2,3,4,5]", n=N2)
t_list_cp  = measure("y = list(x)",      "x = [1,2,3,4,5]", n=N2)
t_slice_cp = measure("y = x[:]",         "x = [1,2,3,4,5]", n=N2)
t_deep_cp  = measure("import copy; y = copy.deepcopy(x)", "x = [1,2,3,4,5]", n=N2)

print(f"  {'y = x (alias)':<30} {t_alias:>8.1f} ns")
print(f"  {'y = list(x)':<30} {t_list_cp:>8.1f} ns  ({t_list_cp/t_alias:.0f}x alias)")
print(f"  {'y = x[:]':<30} {t_slice_cp:>8.1f} ns  ({t_slice_cp/t_alias:.0f}x alias)")
print(f"  {'copy.deepcopy(x)':<30} {t_deep_cp:>8.1f} ns  ({t_deep_cp/t_alias:.0f}x alias)")

print("""
  Aliasing (y = x) is essentially free — just binds a name.
  list() and [:] are comparable — both create a new list from elements.
  deepcopy is orders of magnitude more expensive.

  Bottom line:
    - In hot loops processing immutable items: alias is fine
    - Building independent copies for safety: use list() / dict()
    - Full independence from nested mutable objects: deepcopy (pay the cost)
""")


# ── Summary ───────────────────────────────────────────────────────────────────

section("Summary")
print("""
  OPERATION          COST      USE WHEN
  ────────────────────────────────────────────────────────
  y = x              ~0 ns     you WANT shared state (aliasing)
  y = list(x)        low       inner items are immutable
  copy.copy(x)       low       same as list(x) for flat containers
  copy.deepcopy(x)   high      need fully independent copy
  x is None          fastest   singleton / sentinel check
  x == value         varies    value comparison (the correct default)
""")
