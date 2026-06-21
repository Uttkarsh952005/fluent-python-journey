# Chapter 4 — Unicode Text Versus Bytes

## The Core Divide

Python 3's most important design decision for working programmers:

```
str   = sequence of Unicode code points  (human text, in memory)
bytes = sequence of integers 0–255       (raw bytes, for storage/transmission)
```

They are **completely separate types**. Python 3 will never implicitly convert between them. Every boundary crossing requires an explicit `encode()` or `decode()` call with a named encoding.

---

## Code Points vs Bytes

A **code point** is the abstract identity of a character — an integer from `U+0000` to `U+10FFFF`. About 150,000 are assigned (out of 1.1 million possible).

A **byte sequence** is the concrete representation — what gets written to disk or sent over a network. The mapping between code point and bytes depends on the **encoding**.

```
str  'café'  →  4 code points: U+0063 U+0061 U+0066 U+00E9
                ↓ encode('utf-8')
bytes         →  b'caf\xc3\xa9'  (5 bytes — 'é' needs 2 bytes in UTF-8)
                ↓ decode('utf-8')
str  'café'  ← back to 4 code points
```

Mental model: **decode = humanize; encode = serialize**.

---

## The Binary Sequence Types

Three types, in order of use:

| Type | Mutable | Use case |
|------|---------|----------|
| `bytes` | No | Immutable byte sequences, most common |
| `bytearray` | Yes | Mutable buffer for building byte sequences |
| `memoryview` | Depends | Zero-copy view — never copies underlying data |

**The `bytes[0]` vs `bytes[:1]` distinction:**
```python
b = b'café'   # as bytes
b[0]          # → 99 (int, not str)
b[:1]         # → b'c' (bytes, even length-1 slice)
```
This is the opposite of `str`, where `s[0] == s[:1]`. Every Python programmer gets bitten by this once.

**`memoryview.cast()`** lets you reinterpret the same bytes as different C types (e.g., view `array('h', ...)` as unsigned bytes) — without copying a single byte.

---

## Key Codecs

| Encoding | Bytes per char | Covers | Notes |
|----------|---------------|--------|-------|
| `ascii` | 1 | 128 chars | 7-bit, strict subset of all below |
| `latin-1` / `iso8859-1` | 1 | 256 chars | Basis for cp1252 and Unicode |
| `cp1252` | 1 | 256 chars | Microsoft superset of latin-1 |
| `utf-8` | 1–4 | All Unicode | ASCII-compatible, dominant on web (97%+) |
| `utf-16` | 2–4 | All Unicode | BOM, common in Windows APIs |
| `utf-32` | 4 (fixed) | All Unicode | Simple but wasteful |

**UTF-8 dominance**: as of 2021, 97%+ of websites use UTF-8 (up from 81% in 2014). Default for Python source files. Use it unless you have a specific reason not to.

---

## The Four Normal Forms

Unicode has **canonical equivalents** — the same visual character can be multiple code point sequences:

```python
s1 = "café"                              # é as U+00E9 — 4 code points
s2 = "cafe\N{COMBINING ACUTE ACCENT}"   # e + U+0301 — 5 code points
s1 == s2  # → False  (same look, different code points!)
```

| Form | What it does | When to use |
|------|-------------|-------------|
| `NFC` | Compose — shortest form | Store and compare user input |
| `NFD` | Decompose — base + combining | Splitting characters for processing |
| `NFKC` | Compatibility composed | Search indexes (maps ﬁ→fi, ½→1/2) |
| `NFKD` | Compatibility decomposed | ASCII folding before diacritic removal |

**Rule**: Always normalize to NFC before comparing or storing user-supplied strings.

---

## Error Handlers

When encoding/decoding fails:

| Handler | Effect | Use when |
|---------|--------|----------|
| `'strict'` (default) | Raises `UnicodeEncodeError` / `UnicodeDecodeError` | Always — fail loud |
| `'ignore'` | Silently drops unencodable chars | Almost never — silent data loss |
| `'replace'` | Substitutes `?` or `U+FFFD` | User-facing display only |
| `'xmlcharrefreplace'` | XML entities `&#xxx;` | XML/HTML output only |

**Key insight**: Legacy 8-bit codecs (cp1252, latin-1, koi8_r) decode **any** byte sequence without raising errors — they just produce garbage. UTF-8 is strict and detects invalid byte sequences. This makes UTF-8 the safer default for reading: fail-loud beats silent mojibake.

---

## Unicode Sandwich (The Right I/O Pattern)

```
      Input side          Business logic          Output side
  ┌─────────────┐        ┌────────────────┐      ┌─────────────┐
  │   bytes     │        │                │      │    bytes    │
  │   coming    │─decode→│  str only      │─encode→│   going    │
  │   in        │ (early)│  (in memory)   │(late)  │   out      │
  └─────────────┘        └────────────────┘      └─────────────┘
```

**Decode as early as possible. Encode as late as possible. Never mix bytes and str in business logic.**

---

## The Platform Encoding Trap

```python
# This is a BUG waiting to happen:
open("file.txt", "w").write("café")   # uses locale default!
open("file.txt").read()               # same default — might work locally

# Write on Linux (UTF-8), read on Windows (cp1252) → mojibake
```

On Linux/macOS: all defaults are UTF-8.  
On Windows: `locale.getpreferredencoding()` is often `'cp1252'` for file I/O, even when console is UTF-8.

**The fix — always explicit:**
```python
open("file.txt", "w", encoding="utf-8").write("café")  # safe everywhere
open("file.txt", encoding="utf-8").read()               # safe everywhere
```

`sys.stdout.reconfigure(encoding="utf-8")` — fixes console output on Windows in scripts.

---

## Quick Reference

```python
# encode / decode
"café".encode("utf-8")          # str → bytes
b"caf\xc3\xa9".decode("utf-8") # bytes → str

# check if safe to encode as ASCII
"hello".isascii()  # True
"café".isascii()   # False

# normalize before comparing
from unicodedata import normalize
normalize("NFC", s1) == normalize("NFC", s2)  # True even for canonical equivalents

# case fold (Unicode-aware, better than .lower() for non-ASCII)
"Straße".casefold()  # 'strasse' (ß → ss)
"Straße".lower()     # 'straße'  (ß unchanged)

# diacritic removal
import unicodedata
nfd = unicodedata.normalize("NFD", "café")
"".join(c for c in nfd if unicodedata.category(c) != "Mn")  # "cafe"

# always explicit encoding on file I/O
with open("data.txt", encoding="utf-8") as f:
    text = f.read()
```
