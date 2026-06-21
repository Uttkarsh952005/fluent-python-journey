# Chapter 23: Attribute Descriptors — Notes

## 1. The Nomenclature of Descriptors
Understanding descriptors requires a strict vocabulary because multiple objects interact at the exact same time:
*   **Descriptor Class:** A class implementing the descriptor protocol (`__get__`, `__set__`, or `__delete__`).
*   **Descriptor Instance:** An instance of the descriptor class, assigned as a class attribute of the managed class.
*   **Managed Class:** The class where the descriptor instances are declared as class attributes.
*   **Managed Instance:** One specific instance of the managed class.
*   **Storage Name:** The string name of the attribute where the descriptor stores its data in the managed instance's `__dict__`.

## 2. Overriding vs Non-Overriding Descriptors
The presence of `__set__` completely changes how Python handles the descriptor during the attribute lookup chain (Chapter 22).
*   **Overriding Descriptors (Data Descriptors):** They implement `__set__`. Because Python checks them *before* looking in the instance `__dict__`, they unconditionally intercept all reads and writes. A user cannot overwrite them. The `@property` decorator creates an overriding descriptor.
*   **Non-Overriding Descriptors (Non-Data Descriptors):** They only implement `__get__`. Because Python checks the instance `__dict__` *before* checking non-overriding descriptors, if a user types `obj.x = 5`, Python just creates a raw variable `obj.__dict__['x'] = 5`. The next time you call `obj.x`, you get 5. The descriptor is completely shadowed and hidden forever. Standard Python functions and `@cached_property` are non-overriding descriptors.

## 3. `__set_name__`
Before Python 3.6, descriptors were blind. If you typed `weight = Quantity()`, the `Quantity` instance had no idea it was called "weight". Developers had to manually pass the name: `weight = Quantity("weight")`.
Python 3.6 introduced `__set_name__(self, owner, name)`. When the managed class is parsed, Python automatically calls this method on every descriptor it finds, handing it the exact variable name it was bound to.
