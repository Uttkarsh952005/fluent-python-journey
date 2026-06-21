"""
Chapter 6: Object References, Mutability, and Recycling — Examples
===================================================================
Parts:
  1. Variables are labels, not boxes (Ex 6-1, 6-2)
  2. Identity, equality, aliases (Ex 6-3, 6-4)
  3. Relative immutability of tuples (Ex 6-5)
  4. Shallow vs deep copies (Ex 6-6 through 6-10)
  5. Function parameters as references; mutable defaults (Ex 6-11 through 6-15)
  6. del, garbage collection, CPython tricks — interning (Ex 6-16 through 6-18)

Run: python examples.py
"""
import sys
import copy
import weakref

sys.stdout.reconfigure(encoding="utf-8")


# ── PART 1: Variables are labels, not boxes ───────────────────────────────────

def variables_as_labels() -> None:
    print("=== Part 1: Variables Are Labels, Not Boxes ===\n")

    # Ex 6-1: a and b are two labels on the SAME list object
    a = [1, 2, 3]
    b = a            # b is a new label on the same object — NOT a copy
    a.append(4)
    print(f"a = [1,2,3]; b = a; a.append(4)")
    print(f"b = {b}  ← b sees the change because it's the same list\n")

    # Ex 6-2: RHS is evaluated first; variable is bound AFTER object exists
    class Gizmo:
        def __init__(self):
            print(f"  Gizmo created: id={id(self)}")

    print("y = Gizmo() * 10  →  Gizmo is created, THEN multiplication fails:")
    try:
        y = Gizmo() * 10   # Gizmo prints its id, then TypeError is raised
    except TypeError as e:
        print(f"  TypeError: {e}")
    print("  'y' was never bound (exception before assignment)\n")

    print("Key rule: read the RHS first. Object is created before label is attached.")


# ── PART 2: Identity, equality, aliases ──────────────────────────────────────

def identity_and_equality() -> None:
    print("\n=== Part 2: Identity, Equality, Aliases ===\n")

    # Ex 6-3: lewis is an alias for charles — same object
    charles = {"name": "Charles L. Dodgson", "born": 1832}
    lewis   = charles           # alias — two labels, one object
    print(f"lewis is charles:  {lewis is charles}")
    print(f"id(charles):       {id(charles)}")
    print(f"id(lewis):         {id(lewis)}  (same!)\n")

    lewis["balance"] = 950      # modifying via lewis changes charles too
    print(f"lewis['balance'] = 950 → charles = {charles}\n")

    # Ex 6-4: alex is a separate object with equal value
    alex = {"name": "Charles L. Dodgson", "born": 1832, "balance": 950}
    print(f"alex == charles:     {alex == charles}  ← equal values")
    print(f"alex is charles:     {alex is charles}  ← different objects")
    print(f"alex is not charles: {alex is not charles}\n")

    # == compares VALUE; is compares IDENTITY (memory address in CPython)
    print("== checks value (calls __eq__)")
    print("is checks identity (compares id() — no __eq__ override possible)")

    # Sentinel pattern — the ONE correct use of 'is' beyond None checks
    END = object()
    def process(token):
        if token is END:
            return "done"
        return f"processing {token!r}"

    print(f"\nSentinel pattern: process(END) → {process(END)!r}")
    print(f"                  process('hi') → {process('hi')!r}")


# ── PART 3: Relative immutability of tuples ──────────────────────────────────

def tuple_immutability() -> None:
    print("\n=== Part 3: The Relative Immutability of Tuples ===\n")

    # Ex 6-5: tuple is immutable, but its CONTENTS can change if they're mutable
    t1 = (1, 2, [30, 40])
    t2 = (1, 2, [30, 40])

    print(f"t1 = {t1}")
    print(f"t2 = {t2}")
    print(f"t1 == t2:  {t1 == t2}  ← equal values")
    print(f"id(t1[-1]) before: {id(t1[-1])}")

    t1[-1].append(99)           # mutate the LIST inside the tuple

    print(f"After t1[-1].append(99):")
    print(f"t1 = {t1}")
    print(f"id(t1[-1]) after:  {id(t1[-1])}  ← same list object, different value")
    print(f"t1 == t2:  {t1 == t2}  ← now different!\n")

    print("Tuple immutability = the REFERENCES inside can't change.")
    print("But if a reference points to a mutable object, that object can still mutate.")
    print("This is why tuples containing lists are NOT hashable.\n")

    try:
        hash(t1)
    except TypeError as e:
        print(f"hash((1, 2, [30, 40, 99])): {e}")


# ── PART 4: Shallow vs deep copies ───────────────────────────────────────────

def copies_demo() -> None:
    print("\n=== Part 4: Shallow vs Deep Copies ===\n")

    # Ex 6-6/6-7: shallow copy — outer container duplicated, inner refs shared
    l1 = [3, [66, 55, 44], (7, 8, 9)]
    l2 = list(l1)       # shallow copy — same as l1[:]

    print(f"l1 = {l1}")
    print(f"l2 = list(l1) — shallow copy")
    print(f"l2 is l1: {l2 is l1}  ← different lists")
    print(f"l2[1] is l1[1]: {l2[1] is l1[1]}  ← but SAME inner list!\n")

    l1.append(100)          # only affects l1 (outer list is different)
    l1[1].remove(55)        # affects BOTH — shared inner list

    print(f"After l1.append(100) and l1[1].remove(55):")
    print(f"l1: {l1}")
    print(f"l2: {l2}  ← l2[1] changed because l2[1] IS l1[1]\n")

    l2[1] += [33, 22]       # mutates the shared list — visible in l1 too
    l2[2] += (10, 11)       # creates a NEW tuple — l2[2] is now different

    print(f"After l2[1] += [33,22] and l2[2] += (10,11):")
    print(f"l1: {l1}")
    print(f"l2: {l2}")
    print(f"l1[1] is l2[1]: {l1[1] is l2[1]}  ← still shared!")
    print(f"l1[2] is l2[2]: {l1[2] is l2[2]}  ← tuples diverged\n")

    # Ex 6-8/6-9: Bus class — shallow vs deep copy
    class Bus:
        def __init__(self, passengers=None):
            self.passengers = list(passengers) if passengers else []
        def pick(self, name):  self.passengers.append(name)
        def drop(self, name):  self.passengers.remove(name)
        def __repr__(self):    return f"Bus({self.passengers})"

    bus1 = Bus(["Alice", "Bill", "Claire", "David"])
    bus2 = copy.copy(bus1)      # shallow: different Bus, SAME passengers list
    bus3 = copy.deepcopy(bus1)  # deep: different Bus AND different passengers list

    print(f"bus1, bus2, bus3 ids: {id(bus1)}, {id(bus2)}, {id(bus3)}")
    print(f"bus1.passengers is bus2.passengers: {bus1.passengers is bus2.passengers}")
    print(f"bus1.passengers is bus3.passengers: {bus1.passengers is bus3.passengers}\n")

    bus1.drop("Bill")
    print(f"After bus1.drop('Bill'):")
    print(f"bus2.passengers: {bus2.passengers}  ← Bill gone (shared list!)")
    print(f"bus3.passengers: {bus3.passengers}  ← Bill still here (deep copy)\n")

    # Ex 6-10: deepcopy handles cyclic references
    a = [10, 20]
    b = [a, 30]
    a.append(b)             # cyclic: a → b → a → ...
    c = copy.deepcopy(a)    # deepcopy tracks visited objects — no infinite loop
    print(f"Cyclic deepcopy: a = [10, 20, [[...], 30]]")
    print(f"deepcopy(a) succeeded — cyclic refs handled gracefully")


# ── PART 5: Function parameters as references; mutable defaults ───────────────

def parameters_and_defaults() -> None:
    print("\n=== Part 5: Function Parameters as References ===\n")

    # Ex 6-11: call-by-sharing — parameter is an alias of the argument
    def f(a, b):
        a += b
        return a

    x, y = 1, 2
    f(x, y)
    print(f"Integers: f(1,2) → x={x}  (unchanged — int is immutable, += rebinds local a)")

    lst_a, lst_b = [1, 2], [3, 4]
    f(lst_a, lst_b)
    print(f"Lists:    f([1,2],[3,4]) → lst_a={lst_a}  (changed! += on list is in-place)")

    t, u = (10, 20), (30, 40)
    f(t, u)
    print(f"Tuples:   f((10,20),(30,40)) → t={t}  (unchanged — += creates new tuple)\n")

    # Ex 6-12/6-13: HauntedBus — mutable default shared across all instances
    class HauntedBus:
        """Mutable default `[]` is one object, shared by ALL calls."""
        def __init__(self, passengers=[]):   # ← THE BUG
            self.passengers = passengers
        def pick(self, name): self.passengers.append(name)
        def drop(self, name): self.passengers.remove(name)

    bus2 = HauntedBus()
    bus2.pick("Carrie")
    bus3 = HauntedBus()         # gets SAME default list as bus2
    print(f"HauntedBus: bus3 starts empty?  {bus3.passengers}")
    print(f"            bus2 is bus3 passengers: {bus2.passengers is bus3.passengers}")
    print(f"            The ghost: {HauntedBus.__init__.__defaults__}\n")

    # Ex 6-14/6-15: TwilightBus — aliasing received argument
    class TwilightBus:
        """Aliases the passed-in list directly — mutates caller's data."""
        def __init__(self, passengers=None):
            self.passengers = passengers if passengers is not None else []  # BUG: no copy
        def drop(self, name): self.passengers.remove(name)

    team = ["Sue", "Tina", "Maya", "Diana"]
    bus  = TwilightBus(team)
    bus.drop("Tina")
    print(f"TwilightBus bug: after bus.drop('Tina'), team = {team}")
    print("The bus aliased the team list directly — caller's data was mutated!\n")

    # THE FIX: always copy mutable arguments
    class SafeBus:
        def __init__(self, passengers=None):
            self.passengers = list(passengers) if passengers else []
        def drop(self, name): self.passengers.remove(name)

    team2 = ["Sue", "Tina", "Maya", "Diana"]
    safe  = SafeBus(team2)
    safe.drop("Tina")
    print(f"SafeBus fix: after safe.drop('Tina'), team2 = {team2}  ← unchanged")


# ── PART 6: del, GC, interning ───────────────────────────────────────────────

def del_and_gc_demo() -> None:
    print("\n=== Part 6: del, Garbage Collection, Interning ===\n")

    # del removes a reference — object destroyed only when refcount hits 0
    a = [1, 2]
    b = a
    del a               # removes label 'a'; object still has label 'b'
    print(f"del a; b = {b}  ← object still alive via 'b'")
    # b = [3]           # now object [1,2] would be destroyed

    # Ex 6-16: weakref.finalize — observe object destruction
    s1 = {1, 2, 3}
    s2 = s1
    destroyed = []

    def on_destroy():
        destroyed.append(True)
        print("  {1,2,3} destroyed!")

    ender = weakref.finalize(s1, on_destroy)
    print(f"\nender.alive after del s1: ", end="")
    del s1
    print(ender.alive)      # True — s2 still holds a reference

    print(f"ender.alive after s2 rebind: ", end="")
    s2 = "spam"             # last reference gone → object destroyed → callback fires
    print(ender.alive)

    # Ex 6-17/6-18: CPython tricks with immutables — interning
    print("\nInterning (CPython implementation detail):")

    t1 = (1, 2, 3)
    t2 = tuple(t1)          # NOT a new tuple — returns the same object
    print(f"  tuple(t1) is t1: {tuple(t1) is t1}  ← no copy made for tuples")

    t3 = (1, 2, 3)          # CPython may or may not intern — don't rely on either result
    print(f"  (1,2,3) is t1:   {t3 is t1}  ← CPython may intern small tuple literals (impl detail)")

    s1 = "ABC"
    s2 = "ABC"
    print(f"  'ABC' is 'ABC':  {s1 is s2}  ← string interning (CPython optimisation)")
    print("  NEVER rely on this. Always use == for string/int comparison.")


# ── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    variables_as_labels()
    identity_and_equality()
    tuple_immutability()
    copies_demo()
    parameters_and_defaults()
    del_and_gc_demo()
