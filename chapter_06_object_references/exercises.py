"""
Chapter 6: Exercises — Object References, Mutability, and Recycling
====================================================================
Run: python exercises.py
"""
import sys
import copy
import weakref

sys.stdout.reconfigure(encoding="utf-8")


# ── Exercise 1: Aliasing Detective ───────────────────────────────────────────
# Predict the output BEFORE running. Then verify.

def exercise_1_aliasing() -> None:
    print("=== Exercise 1: Aliasing Detective ===\n")

    x = [1, 2, 3]
    y = x
    z = x[:]        # shallow copy

    x.append(4)
    y[0] = 99

    print(f"x = {x}")
    print(f"y = {y}  ← alias of x — sees all changes")
    print(f"z = {z}  ← shallow copy — outer list independent\n")

    # Nested aliasing trap
    a = [[1, 2], [3, 4]]
    b = a[:]        # shallow copy

    a[0].append(99)     # modifies inner list — b[0] sees it (shared ref)
    a.append([5, 6])    # modifies outer a only — b unchanged here

    print(f"After nested shallow copy:")
    print(f"a = {a}")
    print(f"b = {b}  ← b[0] changed (shared inner list), b[1] unchanged")
    print(f"a[0] is b[0]: {a[0] is b[0]}\n")


# ── Exercise 2: is vs == Audit ────────────────────────────────────────────────
# Find every place 'is' is being misused and explain why.

def exercise_2_is_vs_eq() -> None:
    print("=== Exercise 2: is vs == Audit ===\n")

    cases = [
        (1000, 1000),
        ("hello world", "hello world"),
        (None, None),
        ([], []),
        (True, 1),
    ]

    print(f"  {'a':<20} {'b':<20} {'a==b':>6} {'a is b':>8} {'note'}")
    print("  " + "-" * 70)
    for a, b in cases:
        eq = a == b
        ident = a is b
        note = ""
        if ident and type(a) not in (bool, type(None)):
            note = "interning/cache — don't rely on this!"
        elif not ident and eq:
            note = "equal values, different objects — use =="
        elif type(a) is type(None):
            note = "None check — 'is None' is correct here"
        print(f"  {repr(a):<20} {repr(b):<20} {str(eq):>6} {str(ident):>8}   {note}")

    print("""
Rules:
  - Use 'is' ONLY to check singletons: None, True, False, sentinel objects
  - Use 'is' for sentinel patterns: `if token is END_OF_STREAM`
  - Use '==' for all value comparisons — always
  - NEVER write: if x is "some string"  or  if count is 0
""")


# ── Exercise 3: Copy Depth Tester ────────────────────────────────────────────
# Given a nested structure, determine which parts are shared after copy/deepcopy.

def exercise_3_copy_depth() -> None:
    print("=== Exercise 3: Copy Depth Tester ===\n")

    original = {
        "name": "Alice",
        "scores": [95, 87, 92],
        "address": {"city": "Mumbai", "zip": "400001"},
        "tags": ("python", "data"),
    }

    shallow = copy.copy(original)
    deep    = copy.deepcopy(original)

    # Mutate each level
    original["name"] = "Bob"                    # str (immutable) — rebinding only
    original["scores"].append(100)              # mutate inner list
    original["address"]["city"] = "Delhi"       # mutate inner dict

    print(f"{'Key':<12} {'original':>20} {'shallow':>20} {'deep':>20}")
    print("-" * 76)
    for key in original:
        print(f"  {key:<10} {str(original[key]):>20} {str(shallow[key]):>20} {str(deep[key]):>20}")

    print(f"""
Observations:
  name:    shallow['name'] = {shallow['name']!r}  — str is immutable; rebinding doesn't affect copies
  scores:  shallow['scores'] = {shallow['scores']}  — shallow shares the list; deep doesn't
  address: shallow['address']['city'] = {shallow['address']['city']!r}  — shallow shares inner dict
  tags:    tuple — immutable, shared safely in all cases
""")


# ── Exercise 4: Defensive Copy Policy ────────────────────────────────────────
# Implement a class that follows correct defensive copying of received arguments.

def exercise_4_defensive_copy() -> None:
    print("=== Exercise 4: Defensive Copy Policy ===\n")

    class Playlist:
        """
        A music playlist that owns its track list.
        Demonstrates the correct pattern: copy received mutable args.
        """
        def __init__(self, name: str, tracks: list[str]) -> None:
            self.name   = name
            self.tracks = list(tracks)    # ← defensive copy — we own this list

        def add(self, track: str) -> None:
            self.tracks.append(track)

        def __repr__(self) -> str:
            return f"Playlist({self.name!r}, {self.tracks})"

    user_tracks = ["Track A", "Track B", "Track C"]
    pl = Playlist("My Mix", user_tracks)

    # Caller modifies their list — playlist unaffected
    user_tracks.append("Track D")
    print(f"user_tracks after append: {user_tracks}")
    print(f"playlist.tracks:          {pl.tracks}  ← unaffected (defensive copy)\n")

    # Playlist adds its own tracks — caller unaffected
    pl.add("Track E")
    print(f"After pl.add('Track E'):")
    print(f"user_tracks:      {user_tracks}  ← unaffected")
    print(f"playlist.tracks:  {pl.tracks}")


# ── Exercise 5: Reference Counting Observer ──────────────────────────────────
# Use weakref to observe when objects are destroyed.

def exercise_5_weakref_observer() -> None:
    print("\n=== Exercise 5: Weakref Lifecycle Observer ===\n")

    log: list[str] = []

    class Tracked:
        def __init__(self, name: str) -> None:
            self.name = name

    def make_finalizer(name: str):
        def callback():
            log.append(f"{name} destroyed")
        return callback

    # Create objects and register finalizers
    obj_a = Tracked("Alpha")
    obj_b = Tracked("Beta")

    weakref.finalize(obj_a, make_finalizer("Alpha"))
    weakref.finalize(obj_b, make_finalizer("Beta"))

    print(f"Before deletion: log = {log}")

    # Create an alias — deleting original won't destroy
    alias_a = obj_a
    del obj_a
    print(f"After del obj_a (alias exists): log = {log}  ← Alpha still alive")

    # Now remove the alias too
    del alias_a
    print(f"After del alias_a: log = {log}  ← Alpha now destroyed")

    del obj_b
    print(f"After del obj_b:   log = {log}  ← Beta destroyed\n")

    print("Key insight: del removes a NAME, not the object.")
    print("Object is destroyed only when ALL references are gone.")


if __name__ == "__main__":
    exercise_1_aliasing()
    exercise_2_is_vs_eq()
    exercise_3_copy_depth()
    exercise_4_defensive_copy()
    exercise_5_weakref_observer()
