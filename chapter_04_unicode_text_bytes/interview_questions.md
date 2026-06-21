# Chapter 4 — Interview Questions: Unicode Text Versus Bytes

> Questions ranging from L3 (junior) to L6 (staff engineer) level.
> Encoding knowledge signals seriousness — most engineers don't invest in this.

---

## 🟢 L3 — Junior / Entry Level

### Q1: What is the difference between `str` and `bytes` in Python 3?

**Expected answer:**
- `str` is a sequence of **Unicode code points** — abstract characters (integers from 0 to 1,114,111). It represents human text in memory.
- `bytes` is a sequence of **integers 0–255** — raw binary data. It's what gets written to disk or sent over a network.

They are completely separate types. Python 3 will never implicitly convert between them. You must explicitly use `.encode(encoding)` to go from `str` → `bytes`, and `.decode(encoding)` to go from `bytes` → `str`.

```python
"café".encode("utf-8")          # str → bytes: b'caf\xc3\xa9'
b"caf\xc3\xa9".decode("utf-8") # bytes → str: 'café'
```

---

### Q2: What is UTF-8 and why is it the dominant encoding?

**Expected answer:**
UTF-8 is a variable-width encoding that represents Unicode code points as 1–4 bytes:
- U+0000–U+007F (ASCII): 1 byte (same as ASCII — backward compatible)
- U+0080–U+07FF: 2 bytes
- U+0800–U+FFFF: 3 bytes (CJK, most scripts)
- U+10000–U+10FFFF: 4 bytes (emoji, rare scripts)

Three reasons for dominance:
1. **ASCII compatibility** — existing ASCII tools work without modification
2. **Self-synchronizing** — you can find character boundaries anywhere in a stream
3. **Error detection** — invalid byte sequences raise `UnicodeDecodeError` (vs. latin-1 which silently misinterprets)

As of 2021, 97%+ of websites use UTF-8 as their character encoding.

---

### Q3: What does `bytes[0]` return vs `bytes[:1]`?

**Expected answer:**
```python
b = b"café"    # actually b'caf\xc3\xa9' in UTF-8
b[0]           # → 99  (int — the byte value)
b[:1]          # → b'c' (bytes — even a length-1 slice is bytes)
```

This is different from `str`, where `s[0] == s[:1]` (both are single-char strings). For binary sequences, indexing returns an integer, slicing returns a bytes/bytearray object. Python deliberately makes this distinction explicit.

---

## 🟡 L4 — Mid-Level

### Q4: What are the four Unicode normalization forms and when do you use them?

**Expected answer:**
The same visual character can have multiple Unicode representations:
```python
s1 = "café"                              # é as U+00E9 — 4 code points (NFC)
s2 = "cafe\N{COMBINING ACUTE ACCENT}"   # e + U+0301 — 5 code points (NFD)
s1 == s2  # False — despite looking identical!
```

| Form | Meaning | Use case |
|------|---------|----------|
| NFC | Composed — shortest representation | Store user input, DB storage |
| NFD | Decomposed — base + combining marks | Processing diacritics separately |
| NFKC | Compatibility composed | Search indexes (maps ﬁ→fi, ½→1/2) |
| NFKD | Compatibility decomposed | ASCII folding before diacritic removal |

**Rule**: Always normalize to NFC when storing or comparing user input.

---

### Q5: What is the "Unicode sandwich" pattern?

**Expected answer:**
A best practice for text I/O coined by Ned Batchelder:

```
bytes → [decode once, early] → str → [all processing] → str → [encode once, late] → bytes
```

1. At input boundaries (file read, HTTP response, DB query): decode bytes → str immediately
2. All business logic operates on str only — never mix bytes and str in processing
3. At output boundaries (file write, HTTP response, DB insert): encode str → bytes at the last moment

This prevents encoding/decoding from leaking into business logic, makes the code platform-independent, and isolates all encoding decisions at I/O boundaries.

```python
# ✅ Unicode sandwich
content = Path("data.txt").read_bytes().decode("utf-8")  # decode early
processed = content.upper().strip()                       # work in str
Path("out.txt").write_bytes(processed.encode("utf-8"))   # encode late
```

---

### Q6: Why should you use `str.casefold()` instead of `str.lower()` for case-insensitive comparison?

**Expected answer:**
`str.lower()` does Unicode case conversion but doesn't handle all language-specific folding rules. `str.casefold()` is more aggressive — it maps additional characters for case-insensitive matching:

```python
"STRASSE".lower()   # 'strasse'
"STRAßE".lower()    # 'straße'  — ß stays as ß

"STRASSE".casefold()   # 'strasse'
"STRAßE".casefold()    # 'strasse'  — ß maps to 'ss'
```

In German, `ß` and `ss` are case equivalents. For search and comparison, `"Straße" == "Strasse"` should be True. `casefold()` handles this; `lower()` doesn't.

**Always use `casefold()` for case-insensitive Unicode comparison.**

---

## 🔴 L5 — Senior

### Q7: Explain how CPython stores str objects internally. Why does adding one emoji to a string change memory usage for all characters?

**Expected answer:**
CPython's str uses three possible internal formats, selected based on the maximum code point in the string:

| Internal format | Code point range | Bytes per char |
|----------------|-----------------|----------------|
| Latin-1 (compact ASCII) | U+0000–U+00FF | 1 byte |
| UCS-2 | U+0100–U+FFFF | 2 bytes |
| UCS-4 | U+10000–U+10FFFF | 4 bytes |

CPython must pick **one format per string object** — it can't mix. If a string contains even a single emoji (U+1F600 = 😀, above U+FFFF), the **entire string** switches to UCS-4 — 4 bytes for every character, including the ASCII ones.

```python
import sys
sys.getsizeof("a" * 100)         # ~149 bytes (1 byte/char)
sys.getsizeof("a" * 100 + "😀") # ~449 bytes (4 bytes/char — 4x more!)
```

This is why emoji in production data can cause unexpected memory spikes in text-processing code.

---

### Q8: What is the difference between `UnicodeEncodeError` and `UnicodeDecodeError`? How would you debug each?

**Expected answer:**
- **`UnicodeEncodeError`**: raised when converting `str` → `bytes` and the target encoding can't represent a character. Example: `"€".encode("ascii")`.
- **`UnicodeDecodeError`**: raised when converting `bytes` → `str` and the bytes don't conform to the expected encoding. Example: `b"\xe9".decode("utf-8")` (0xe9 is valid latin-1 but not valid UTF-8 as a standalone byte).

**Debugging approach:**
1. Check the exact exception type (encode vs decode) to know which direction you're in.
2. Check the `encoding`, `start`, `end`, and `reason` attributes of the exception.
3. For decode errors: try detecting the actual encoding (`chardet`/`charset-normalizer`).
4. For encode errors: consider `errors='xmlcharrefreplace'` for XML, or `errors='replace'` for display.

```python
try:
    ...
except UnicodeDecodeError as e:
    print(f"Failed decoding at bytes {e.start}-{e.end}: {e.reason}")
    print(f"Problematic bytes: {e.object[e.start:e.end].hex()}")
```

---

## 🟣 L6 — Staff Engineer / Internals

### Q9: Explain why `len("café")` returns 4 but `len("café".encode("utf-8"))` returns 5. Then explain what changes if you use `"café".encode("utf-32")`.

**Expected answer:**
`len("café")` counts **Unicode code points** — the abstract characters. The string has 4: `c`, `a`, `f`, `é` (U+00E9).

`len("café".encode("utf-8"))` counts **bytes**. UTF-8 encodes `é` (U+00E9) as two bytes: `0xC3 0xA9` (because U+00E9 > U+007F, falling in the 2-byte UTF-8 range). So: c(1) + a(1) + f(1) + é(2) = 5 bytes.

For UTF-32: 4 bytes per code point (fixed width, no variable encoding). `len("café".encode("utf-32"))` = 4×4 + 4 (BOM) = 20 bytes.

**The deeper point**: "length of a string" is meaningless without context — do you mean code points, bytes, grapheme clusters, or display columns? A single emoji might be:
- 1 code point (`😀`, U+1F600)
- 4 bytes in UTF-8
- But 2 UTF-16 code units (surrogate pair, because > U+FFFF)
- 1 grapheme cluster (user-visible character)
- 2 display columns in some terminals

This is why international text processing is hard, and why libraries like `grapheme` exist for grapheme-cluster counting.

---

*Depth note: Encoding questions at senior level should connect to real-world incidents — "we had a production bug where..." answers show practical experience, not just theoretical knowledge.*
