# Chapter 4 — Pitfalls: Unicode Text Versus Bytes

Common encoding bugs — the ones that cause production incidents, data corruption,
and "works on my machine" failures that are hard to reproduce.

---

## Pitfall 1: Opening Text Files Without Explicit `encoding=`

### The Mistake
```python
# ❌ Platform-dependent — works on Linux, silently corrupts on Windows
with open("data.txt", "w") as f:
    f.write("café")

with open("data.txt") as f:
    content = f.read()   # reads with cp1252 on Windows → garbled!
```

### Why It Fails
On Windows, `open()` defaults to `locale.getpreferredencoding()` — often `'cp1252'`. If the file was written with UTF-8 (e.g., on Linux), the UTF-8 bytes for `'é'` (`\xc3\xa9`) get decoded as cp1252, producing `'Ã©'`.

### The Fix
```python
# ✅ Always explicit encoding — works identically on all platforms
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("café")

with open("data.txt", encoding="utf-8") as f:
    content = f.read()   # "café" — always correct
```

**Add this to every script that does I/O**: `sys.stdout.reconfigure(encoding="utf-8")`

---

## Pitfall 2: Mixing `str` and `bytes` in Operations

### The Mistake
```python
# ❌ TypeError — Python 3 refuses implicit conversion
name = "café"
prefix = b"User: "
result = prefix + name          # TypeError: can only concatenate bytes to bytes

# ❌ Also wrong
if "hello" in b"hello world":  # TypeError: a bytes-like object is required
    ...
```

### Why It Happens
Python 3 made str/bytes separation absolute. Python 2 would silently encode/decode using ASCII, producing errors only for non-ASCII chars. Python 3 makes the error immediate and explicit.

### The Fix
```python
# ✅ Explicit conversion at the boundary
result = prefix + name.encode("utf-8")

# ✅ Or decode bytes to str
result = prefix.decode("ascii") + name
```

---

## Pitfall 3: Comparing Unnormalized Strings

### The Mistake
```python
# ❌ Returns False — different code point sequences, same visual appearance
db_name   = "café"                              # stored as NFC (U+00E9)
user_input = "cafe\N{COMBINING ACUTE ACCENT}"   # typed as NFD (e + U+0301)

if db_name == user_input:  # False!
    print("found")         # Never prints — silent lookup failure
```

### Why It Fails
Unicode allows multiple representations of the same character. `'é'` can be one code point (`U+00E9`) or two (`'e'` + `COMBINING ACUTE ACCENT U+0301`). Python compares code points, not visual appearance.

### The Fix
```python
from unicodedata import normalize

def normalize_for_comparison(text: str) -> str:
    return normalize("NFC", text)

# ✅ Normalize before comparing
if normalize_for_comparison(db_name) == normalize_for_comparison(user_input):
    print("found")  # Works!
```

**Rule**: Normalize to NFC on ingestion (when data enters your system), not at comparison time.

---

## Pitfall 4: Using `str.lower()` Instead of `str.casefold()`

### The Mistake
```python
# ❌ lower() doesn't handle all Unicode case rules
def normalize_username(name: str) -> str:
    return name.lower().strip()

# German ß:
normalize_username("STRASSE")  # 'strasse' — correct
normalize_username("STRAßE")   # 'straße'  — lowercase ß stays as ß
# But 'straße' != 'strasse'!  Same word, different representations!
```

### Why It Fails
`str.lower()` does Unicode case conversion but doesn't handle special folding rules like German `ß` → `ss` (used in dictionary/search contexts). `str.casefold()` does.

### The Fix
```python
# ✅ Use casefold() for case-insensitive comparison
def normalize_username(name: str) -> str:
    return name.casefold().strip()

normalize_username("STRAßE")   # 'strasse' — matches 'STRASSE' after casefold
```

---

## Pitfall 5: Assuming UTF-8 is Always a Single Byte Per Character

### The Mistake
```python
# ❌ Wrong assumption: byte length = character length
text = "São Paulo"
raw  = text.encode("utf-8")

print(len(text))     # 9  (characters)
print(len(raw))      # 11 (bytes — ã takes 2 bytes in UTF-8)

# Slicing bytes at character boundaries breaks characters:
broken = raw[:4]                    # b'S\xc3\xa3o' — invalid UTF-8 split!
broken.decode("utf-8")              # OK here (4 → 4)
raw[:5].decode("utf-8")            # 'São' — but was this intentional?
```

### Why It Matters
UTF-8 uses 1–4 bytes per character. Slicing bytes without knowing character boundaries produces garbled output or UnicodeDecodeError. This is especially dangerous when truncating text for database varchar columns.

### The Fix
```python
# ✅ Work in str, encode only at the final step
text = "São Paulo"
truncated = text[:4]                 # safe: 'São ' (4 chars)
raw = truncated.encode("utf-8")      # then encode — b'S\xc3\xa3o '
```

---

## Pitfall 6: BOM Confusion with UTF-8-SIG

### The Mistake
```python
# File exported by Excel/Windows Notepad often starts with BOM
with open("excel_export.csv", encoding="utf-8") as f:
    reader = csv.reader(f)
    headers = next(reader)
    # headers[0] is '\ufeffName' — has invisible BOM character!
    # 'Name' != '\ufeffName' — column lookup fails silently
```

### Why It Happens
UTF-8-SIG adds a Byte Order Mark (`\xef\xbb\xbf`) at the start. Reading as plain `utf-8` includes the BOM as character `U+FEFF` (ZERO WIDTH NO-BREAK SPACE) in the first field.

### The Fix
```python
# ✅ Use utf-8-sig as the codec — it strips BOM automatically on read
with open("excel_export.csv", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    headers = next(reader)
    # headers[0] is 'Name' — BOM stripped
```

Or detect dynamically: if `raw[:3] == b'\xef\xbb\xbf'`, use `utf-8-sig`.

---

## Pitfall 7: Using `bytes` Where You Need `bytearray` (Immutability Bug)

### The Mistake
```python
# ❌ bytes is immutable — you can't patch it in place
packet = b"\x00\x01\x02\x03\x04"
packet[0] = 0xFF   # TypeError: 'bytes' object does not support item assignment

# Common workaround that's slow for large buffers:
packet = bytes([0xFF]) + packet[1:]   # creates a new bytes object — O(n) copy
```

### The Fix
```python
# ✅ Use bytearray when you need in-place mutation
packet = bytearray(b"\x00\x01\x02\x03\x04")
packet[0] = 0xFF   # works — O(1)
print(packet)      # bytearray(b'\xff\x01\x02\x03\x04')

# For large binary buffers (network packets, image frames, audio):
# 1. Receive as bytes
# 2. Convert to bytearray for mutation
# 3. Convert back to bytes for final output
```

---

## Interview Relevance

| Pitfall | Interview question |
|---------|-------------------|
| Explicit `encoding=` | "How would you fix a UnicodeDecodeError when reading a file?" |
| str/bytes mixing | "What causes TypeError: can only concatenate str (not 'bytes') to str?" |
| Normalization | "Why might string comparison fail for 'café' in a database lookup?" |
| casefold vs lower | "How do you do case-insensitive comparison for non-ASCII text?" |
| UTF-8 byte length | "Why is `len('São Paulo'.encode('utf-8'))` different from `len('São Paulo')`?" |
| BOM confusion | "Why does the first column from an Excel CSV have a weird character?" |
