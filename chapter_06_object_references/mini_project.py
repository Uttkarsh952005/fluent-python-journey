"""
Chapter 6: Mini Project — Object Graph Inspector
=================================================
Visualizes Python's reference semantics in real time:
- tracks identity (id), alias relationships, ref counts
- demonstrates shallow vs deep copy differences on a document tree
- uses weakref to observe object lifetimes

Run: python mini_project.py
"""
import sys
import copy
import weakref
import ctypes

sys.stdout.reconfigure(encoding="utf-8")


def refcount(obj_id: int) -> int:
    """Get refcount for an object by its id (subtract 1 for this call's own ref)."""
    return ctypes.c_long.from_address(obj_id).value


# ─────────────────────────────────────────────────────────────────────────────
# Domain: Document tree (title, sections, tags)
# ─────────────────────────────────────────────────────────────────────────────

class Section:
    def __init__(self, heading: str, content: str) -> None:
        self.heading = heading
        self.content = content

    def __repr__(self) -> str:
        return f"Section({self.heading!r})"


class Document:
    def __init__(self, title: str, sections: list[Section], tags: list[str]) -> None:
        self.title    = title
        self.sections = list(sections)   # defensive copy of outer list
        self.tags     = list(tags)

    def __repr__(self) -> str:
        return f"Document({self.title!r}, sections={len(self.sections)}, tags={self.tags})"


# ─────────────────────────────────────────────────────────────────────────────
# Inspector utility
# ─────────────────────────────────────────────────────────────────────────────

def inspect_refs(*named_objs: tuple[str, object]) -> None:
    """Print id, type, and whether any two names are aliases."""
    print(f"  {'Name':<12} {'id':>16} {'type':<16}")
    print("  " + "-" * 48)
    for name, obj in named_objs:
        print(f"  {name:<12} {id(obj):>16} {type(obj).__name__:<16}")

    # Alias detection
    ids = [(name, id(obj)) for name, obj in named_objs]
    aliases = []
    seen: dict[int, str] = {}
    for name, oid in ids:
        if oid in seen:
            aliases.append(f"{name} is {seen[oid]}")
        else:
            seen[oid] = name
    if aliases:
        print(f"  Aliases found: {', '.join(aliases)}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Demo 1: Aliasing vs copying
# ─────────────────────────────────────────────────────────────────────────────

def demo_aliasing() -> None:
    print("=" * 60)
    print("  Demo 1: Aliasing vs Copying")
    print("=" * 60)

    s1 = Section("Introduction", "Python is awesome.")
    s2 = Section("Conclusion", "Keep learning.")
    tags = ["python", "learning"]

    doc1 = Document("Python Guide", [s1, s2], tags)

    # Alias — same object
    doc_alias = doc1
    # Shallow copy — new Document shell, same Section objects
    doc_shallow = copy.copy(doc1)
    # Deep copy — everything duplicated
    doc_deep = copy.deepcopy(doc1)

    print("\nObject identities:\n")
    inspect_refs(
        ("doc1", doc1),
        ("doc_alias", doc_alias),
        ("doc_shallow", doc_shallow),
        ("doc_deep", doc_deep),
    )

    print("Section[0] identities (inner objects):\n")
    inspect_refs(
        ("doc1.s[0]",    doc1.sections[0]),
        ("alias.s[0]",   doc_alias.sections[0]),
        ("shallow.s[0]", doc_shallow.sections[0]),
        ("deep.s[0]",    doc_deep.sections[0]),
    )

    print("  shallow.sections[0] IS doc1.sections[0]:", doc_shallow.sections[0] is doc1.sections[0])
    print("  deep.sections[0]    IS doc1.sections[0]:", doc_deep.sections[0] is doc1.sections[0])


# ─────────────────────────────────────────────────────────────────────────────
# Demo 2: Mutation propagation through shallow copy
# ─────────────────────────────────────────────────────────────────────────────

def demo_mutation_propagation() -> None:
    print("\n" + "=" * 60)
    print("  Demo 2: Mutation Propagation")
    print("=" * 60)

    s1 = Section("Intro", "Hello.")
    s2 = Section("Body", "Content.")
    original = Document("Original", [s1, s2], ["v1"])
    shallow  = copy.copy(original)
    deep     = copy.deepcopy(original)

    # Mutate the inner Section object
    original.sections[0].heading = "MODIFIED INTRO"
    # Mutate the outer list (add a section)
    original.sections.append(Section("Appendix", "Extra."))
    # Mutate tags
    original.tags.append("v2")

    print(f"\nAfter mutating original:")
    print(f"  original.sections[0].heading = {original.sections[0].heading!r}")
    print(f"  shallow.sections[0].heading  = {shallow.sections[0].heading!r}  ← SAME (shared Section object)")
    print(f"  deep.sections[0].heading     = {deep.sections[0].heading!r}  ← independent")
    print()
    print(f"  len(original.sections) = {len(original.sections)}")
    print(f"  len(shallow.sections)  = {len(shallow.sections)}  ← outer list is different (new via list())")
    print(f"  len(deep.sections)     = {len(deep.sections)}")
    print()
    print(f"  original.tags = {original.tags}")
    print(f"  shallow.tags  = {shallow.tags}  ← different (new list() in __init__)")
    print(f"  deep.tags     = {deep.tags}")


# ─────────────────────────────────────────────────────────────────────────────
# Demo 3: Weakref lifecycle tracking
# ─────────────────────────────────────────────────────────────────────────────

def demo_weakref_lifecycle() -> None:
    print("\n" + "=" * 60)
    print("  Demo 3: Weakref Lifecycle Tracking")
    print("=" * 60)

    events: list[str] = []

    class TrackedSection(Section):
        pass

    def on_destroy(name: str):
        def _cb():
            events.append(f"DESTROYED: {name}")
        return _cb

    print()
    sec_a = TrackedSection("Alpha", "...")
    sec_b = TrackedSection("Beta", "...")

    weakref.finalize(sec_a, on_destroy("Alpha"))
    weakref.finalize(sec_b, on_destroy("Beta"))

    # Put into a document (document holds strong refs via its list)
    doc = Document("Lifecycle Test", [sec_a, sec_b], [])

    # Delete our local references — but Document still holds them
    del sec_a, sec_b
    print(f"After del sec_a, sec_b — events: {events}  ← still alive in doc")

    # Now remove from document
    doc.sections.clear()
    print(f"After doc.sections.clear() — events: {events}  ← now destroyed")


# ─────────────────────────────────────────────────────────────────────────────
# Demo 4: Mutable default trap — exposed at runtime
# ─────────────────────────────────────────────────────────────────────────────

def demo_mutable_default_trap() -> None:
    print("\n" + "=" * 60)
    print("  Demo 4: Mutable Default Trap — Runtime Exposure")
    print("=" * 60)

    class HauntedDocument:
        def __init__(self, title: str, tags: list[str] = []) -> None:
            self.title = title
            self.tags  = tags   # aliasing the default!

        def add_tag(self, tag: str) -> None:
            self.tags.append(tag)

    d1 = HauntedDocument("First Doc")
    d1.add_tag("python")

    d2 = HauntedDocument("Second Doc")  # gets same default list!

    print(f"\n  d1.tags = {d1.tags}")
    print(f"  d2.tags = {d2.tags}  ← 'python' tag appeared without adding it!")
    print(f"  d1.tags is d2.tags: {d1.tags is d2.tags}")
    print(f"  The ghost lives in: HauntedDocument.__init__.__defaults__ = "
          f"{HauntedDocument.__init__.__defaults__}")

    print("""
  Fix: use None as default, create fresh list in __init__:
    def __init__(self, title, tags=None):
        self.tags = list(tags) if tags else []
""")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo_aliasing()
    demo_mutation_propagation()
    demo_weakref_lifecycle()
    demo_mutable_default_trap()

    print("\n" + "=" * 60)
    print("  Key Takeaways")
    print("=" * 60)
    print("""
  1. Assignment binds a name to an object — NOT a copy
  2. Shallow copy: new outer container, shared inner objects
  3. Deep copy: full independent duplicate (handles cycles)
  4. del removes a name — object lives until refcount hits 0
  5. Mutable defaults are evaluated once — shared across calls
  6. Defensive copy received args: self.x = list(x) not self.x = x
""")
