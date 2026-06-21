# Chapter 4 — Unicode Text Versus Bytes

> **Chapter goal**: Internalize the bytes/str divide, understand how Python handles encoding errors, and be able to write platform-safe text I/O — without thinking about it.

---

## What You'll Learn

| Section | Core concept |
|---------|-------------|
| Character Issues | Code points vs byte representations |
| Byte Essentials | `bytes`, `bytearray`, `memoryview` |
| Basic Codecs | UTF-8, UTF-16, latin-1, cp1252 |
| Encode/Decode Errors | Four error handlers, UnicodeEncodeError vs UnicodeDecodeError |
| Text File Handling | Unicode sandwich, always-explicit `encoding=` |
| Encoding Defaults | Why Windows breaks "works on my machine" code |
| Normalization | NFC, NFD, NFKC, NFKD — canonical equivalents |
| Case Folding | `casefold()` vs `lower()` for non-ASCII |

---

## Key Files

- [`examples.py`](examples.py) — 8-part annotated implementation of all major concepts
- [`exercises.py`](exercises.py) — 7 original exercises pushing at edge cases
- [`benchmarks.py`](benchmarks.py) — UTF-8 vs UTF-32 memory; encode/decode overhead; normalization cost
- [`mini_project.py`](mini_project.py) — Unicode-safe CSV cleaner and text normalizer
- [`notes.md`](notes.md) — Deep technical reference with tables and diagrams
- [`pitfalls.md`](pitfalls.md) — 7 common encoding bugs with root causes and fixes
- [`interview_questions.md`](interview_questions.md) — 9 questions from L3→L6
- [`architecture_notes.md`](architecture_notes.md) — Why Unicode was designed the way it was

---

## The Central Mental Model

```
         ENCODE                         DECODE
str  ─────────────────→  bytes  ────────────────────→  str
(code points)          (raw bytes)               (code points)
(abstract)             (concrete)                (abstract)
(in memory)            (on disk/network)         (in memory)

"café"  → utf-8 →  b'caf\xc3\xa9'  → utf-8 →  "café"
  4 chars             5 bytes                    4 chars
```

**`encode` = "serialize for machines"**  
**`decode` = "interpret for humans"**

---

## The str/bytes Separation — Why It Matters

Python 2 blurred the line between text and bytes. This caused:
- Silent mojibake (garbled text) instead of explicit errors
- Code that worked on ASCII input but silently corrupted international data
- No way to know whether a string contained text or raw bytes

Python 3 makes the divide explicit. The cost: you must think about encoding at boundaries. The benefit: encoding bugs become immediately visible as TypeErrors instead of appearing as corrupted data downstream.

---

## Encoding Error Handler Reference

```python
city = "São Paulo"

city.encode("cp437")                           # UnicodeEncodeError (default: 'strict')
city.encode("cp437", errors="ignore")          # b'So Paulo'  ← data loss!
city.encode("cp437", errors="replace")         # b'S?o Paulo' ← lossy
city.encode("cp437", errors="xmlcharrefreplace")  # b'S&#227;o Paulo' ← safe for XML
```

---

## Normalization Quick Reference

```python
from unicodedata import normalize

s1 = "café"                              # U+00E9 (composed é)
s2 = "cafe\N{COMBINING ACUTE ACCENT}"   # e + U+0301 (decomposed)

# Both forms, visually identical, compare as unequal:
s1 == s2  # False — different code point sequences

# Normalize before comparing:
normalize("NFC", s1) == normalize("NFC", s2)  # True
normalize("NFD", s1) == normalize("NFD", s2)  # True

# Diacritic removal (for fuzzy search):
nfd = normalize("NFD", s1)
"".join(c for c in nfd if unicodedata.category(c) != "Mn")  # "cafe"
```

---

## The Platform Encoding Trap — Reference

| Setting | Linux/macOS | Windows (typical) |
|---------|------------|-------------------|
| `locale.getpreferredencoding()` | `'UTF-8'` | `'cp1252'` |
| File open default | `'UTF-8'` | `'cp1252'` |
| `sys.stdout.encoding` (interactive) | `'utf-8'` | `'utf-8'` (since 3.6) |
| `sys.stdout.encoding` (redirected) | `'UTF-8'` | `'cp1252'` |
| `sys.getfilesystemencoding()` | `'utf-8'` | `'utf-8'` (since 3.6) |

**Fix everything at once**: `sys.stdout.reconfigure(encoding="utf-8")` at the top of scripts.

---

## Pre-Reading Checklist

Before working through this chapter, make sure you understand:
- [ ] Python's type system distinguishes `str` and `bytes` absolutely
- [ ] `"café"[1]` → `"a"` (a str); `b"caf\xc3\xa9"[3]` → `195` (an int!)
- [ ] `len("café")` → `4`; `len("café".encode("utf-8"))` → `5`

If any of those surprised you, start with `examples.py` Part 1.

---

*Reference: Fluent Python 2nd ed., Chapter 4 — pages 117–165*
