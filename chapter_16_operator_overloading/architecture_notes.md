# Chapter 16 — Architecture Notes: Operator Dispatch in CPython

---

## 1. The `PyNumberMethods` Struct

At the CPython source code level, dunder methods like `__add__` and `__iadd__` are not actually dictionary lookups at runtime. When a class is created, CPython populates a C struct called `PyNumberMethods`.

```c
typedef struct {
    binaryfunc nb_add;
    binaryfunc nb_subtract;
    binaryfunc nb_multiply;
    // ...
    binaryfunc nb_inplace_add;
    binaryfunc nb_inplace_subtract;
} PyNumberMethods;
```

When you type `a + b`, the interpreter executes the `BINARY_ADD` opcode. This opcode directly checks the `nb_add` function pointer on the type object. This C-level slot dispatch is significantly faster than doing a `getattr(a, "__add__")` string lookup.

---

## 2. The Implementation of the Reverse Fallback

The logic that handles the reverse fallback (the `__radd__` behavior) is baked deep into `Objects/abstract.c` in the CPython source tree, specifically in the `PyNumber_Add` function.

Here is the exact algorithmic path CPython takes for `a + b`:
1. Check if `a->ob_type->tp_as_number->nb_add` exists.
2. If it does, call it. 
3. If it returns the C constant `Py_NotImplemented`, proceed to step 4.
4. Check if `b->ob_type->tp_as_number->nb_add` exists. (Notice that in C, `__radd__` and `__add__` often point to the exact same slot logic).
5. If it returns a value, return it. If it returns `Py_NotImplemented`, throw a `TypeError`.

---

## 3. The Object Overwrite Bug Explained

In Python, `a += b` evaluates to `a = a.__iadd__(b)`. 

If you forget to `return self` in `__iadd__`, the method implicitly returns `None`. The `INPLACE_ADD` opcode takes the return value off the evaluation stack and binds it to the variable `a`. Because the pointer returned was `Py_None`, the reference count to your original object drops, and `a` becomes `None`. 
This is why failing to return `self` from an in-place operator permanently destroys the object reference.
