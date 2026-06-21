"""
Chapter 14: Exercises — Inheritance and MRO
===========================================
Original exercises demonstrating broken super() chains and MRO conflicts.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8")

def section(title: str) -> None:
    print(f"\n{'=' * 60}\n=== {title}\n{'=' * 60}")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 1: The Broken Chain
# ─────────────────────────────────────────────────────────────────────────────
# If a class in a multiple inheritance hierarchy forgets to call super(),
# the chain is broken, and downstream classes are never initialized.

class Base:
    def __init__(self):
        self.base_init = True
        print("  Base initialized")

class MixinA(Base):
    def __init__(self):
        # BUG: Forgot to call super().__init__()!
        self.mixin_a_init = True
        print("  MixinA initialized")

class MixinB(Base):
    def __init__(self):
        super().__init__()
        self.mixin_b_init = True
        print("  MixinB initialized")

class System(MixinA, MixinB):
    def __init__(self):
        super().__init__()
        self.system_init = True
        print("  System initialized")


def test_ex1_broken_chain() -> None:
    section("Exercise 1: The Broken super() Chain")
    
    print("MRO:", [c.__name__ for c in System.__mro__])
    print("Instantiating System...")
    sys_obj = System()
    
    print("\nChecking initialization state:")
    print(f"  System initialized? {getattr(sys_obj, 'system_init', False)}")
    print(f"  MixinA initialized? {getattr(sys_obj, 'mixin_a_init', False)}")
    
    # MixinB and Base were completely skipped because MixinA broke the chain!
    print(f"  MixinB initialized? {getattr(sys_obj, 'mixin_b_init', False)}")
    print(f"  Base initialized?   {getattr(sys_obj, 'base_init', False)}")
    
    assert not getattr(sys_obj, 'base_init', False), "Base should be uninitialized"
    print("✓ Exercise 1 passed: Identified broken MRO chain.")

# ─────────────────────────────────────────────────────────────────────────────
# Exercise 2: MRO Conflict (TypeError)
# ─────────────────────────────────────────────────────────────────────────────
# Python will refuse to compile a class if the MRO is ambiguous or creates 
# an impossible linearization (e.g., A inherits from B, but Leaf inherits 
# from B then A).

def test_ex2_mro_conflict() -> None:
    section("Exercise 2: MRO Linearization Failure")
    
    class X: pass
    class Y(X): pass
    
    try:
        # Invalid: Y already specifies that X must come AFTER it.
        # But this signature puts X BEFORE Y.
        class Z(X, Y): 
            pass
        assert False, "Should have raised TypeError"
    except TypeError as e:
        print(f"Caught MRO conflict: {e}")
        print("✓ Exercise 2 passed")


if __name__ == "__main__":
    test_ex1_broken_chain()
    test_ex2_mro_conflict()
