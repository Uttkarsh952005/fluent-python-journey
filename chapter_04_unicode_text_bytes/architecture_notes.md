# Chapter 4 — Architecture Notes: Unicode Text Versus Bytes

Design decisions behind Python's str/bytes model, CPython's internal string representation, and why Unicode is designed the way it is.

---

## Why Python 3 Made `str` and `bytes` Incompatible

Python 2 had a single string type (`str`) that was really a byte sequence, plus a separate `unicode` type. Implicit coercion between them using ASCII was allowed:

```python
# Python 2 — silently broken for non-ASCII
"hello" + u"world"   # works (implicit ascii decode)
"café" + u"world"    # UnicodeDecodeError — but only at runtime, only with non-ASCII input
```

This meant ASCII-only code appeared to work, but broke on real-world international data. The bug was invisible until it hit production.

**Python 3's decision**: make the divide explicit and absolute. `str` is text (code points). `bytes` is binary data. No implicit conversion — ever. Every boundary crossing is deliberate and auditable.

**Cost**: More explicit code, especially for developers who only deal with ASCII.  
**Benefit**: Encoding bugs become immediately visible TypeErrors rather than silent data corruption appearing downstream.

---

## CPython's str Internal Representation (PEP 393)

Before Python 3.3, CPython stored all strings as UCS-4 (4 bytes per character) — simple but wasteful for ASCII-heavy text.

**PEP 393 (Python 3.3)** introduced the "flexible string representation": CPython picks the most compact encoding that can represent all characters in the string.

```
Three possible formats:
┌─────────────────────────────────────────────────────────┐
│ Latin-1 (compact)                                       │
│ All code points ≤ U+00FF → 1 byte per character        │
│ "hello", "café", "naïve"                               │
├─────────────────────────────────────────────────────────┤
│ UCS-2                                                   │
│ Any code point > U+00FF but ≤ U+FFFF → 2 bytes/char   │
│ "日本語", "Привет", "مرحبا"                           │
├─────────────────────────────────────────────────────────┤
│ UCS-4                                                   │
│ Any code point > U+FFFF → 4 bytes per character        │
│ Any string with emoji (😀 = U+1F600), rare scripts     │
└─────────────────────────────────────────────────────────┘
```

**The critical implication**: CPython must use ONE format for the entire string. A single code point above U+FFFF forces the entire string to UCS-4. Adding one emoji to a 1MB ASCII string quadruples its memory usage.

**Why not use UTF-8 internally?** Variable-width encoding makes `s[i]` O(n) instead of O(1). Python requires O(1) indexing for strings. The flexible-but-fixed representation achieves both memory efficiency (for most strings) and O(1) character access.

---

## The Unicode Standard's Two-Level Model

Unicode separates **identity** from **representation**:

**Level 1 — Code space**: 1,114,112 code points (U+0000 to U+10FFFF)
- About 150,000 are assigned characters (as of Unicode 15)
- The rest are unassigned, reserved, or private use

**Level 2 — Encodings**: algorithms that map code points to byte sequences
- UTF-8: variable width, ASCII-compatible, dominant
- UTF-16: variable width (with surrogate pairs for > U+FFFF), used internally by Windows/Java
- UTF-32: fixed width (4 bytes always), simple but memory-intensive

This two-level design was intentional: it decouples the *meaning* of characters from their *storage format*. The same Unicode text can be represented in any encoding — the text content is encoding-independent.

**Historical context**: Unicode started in 1987 as a fixed 16-bit scheme (UCS-2), intending to cover all characters in 65,536 code points. This proved insufficient — CJK extensions, emoji, and historical scripts pushed the count well above 65,536. Surrogate pairs and UTF-32 were added as solutions.

---

## Why Normalization Exists

Unicode allows multiple ways to encode the same visual character. The letter `é` can be:
1. **Precomposed**: U+00E9 (LATIN SMALL LETTER E WITH ACUTE) — one code point
2. **Decomposed**: U+0065 (LATIN SMALL LETTER E) + U+0301 (COMBINING ACUTE ACCENT) — two code points

Both render identically. Both are valid Unicode. Neither is "more correct."

This duality exists for historical reasons: many pre-Unicode character sets used precomposed characters. Unicode needed to accommodate them. Decomposed forms were added for mathematical and linguistic analysis.

**The consequence**: naïve string equality fails for canonical equivalents.

**The four normalization forms** are the standard's solution:
- NFC (Canonical Decomposition, followed by Canonical Composition): precompose everything that can be precomposed. What keyboards produce.
- NFD: fully decompose. Useful for analyzing diacritics.
- NFKC: additionally apply compatibility mappings (ﬁ→fi, ½→1/2). Search-oriented.
- NFKD: compatibility decomposed.

**Design lesson**: normalization is necessary complexity that arises from real-world character set history. It can't be removed without breaking compatibility with existing text.

---

## The Encoding Detection Problem

"How do you detect the encoding of a byte sequence?"

**The honest answer from the book**: You can't, in general. You must be told.

Some heuristics work well:
- **BOM detection**: UTF-8-SIG, UTF-16, and UTF-32 have distinctive byte sequences at the start
- **UTF-8 validation**: UTF-8 has strict byte patterns. If a sequence decodes as valid UTF-8 with non-ASCII bytes, it's very likely UTF-8 (false positives are extremely rare due to the bit patterns chosen)
- **Statistical analysis**: tools like `chardet` and `charset-normalizer` use frequency analysis of byte patterns against known language models

**Why heuristics work but aren't reliable**: Latin-1 and CP-1252 decode any byte sequence — they have no invalid byte values. A random 8-bit byte sequence is always valid latin-1. UTF-8, by design, restricts valid patterns — making validation useful as a heuristic.

**The practical rule**: For data you produce, always use UTF-8 and document it. For data from external sources, require encoding metadata (HTTP headers, XML declarations, BOM). Never silently assume.

---

## Hash Randomization and Bytes

Since Python 3.3, `hash(str)` is randomized per process (PYTHONHASHSEED). This security measure prevents hash collision attacks.

Critically: **`hash(bytes)` is also randomized**.

```python
# Different results in different Python processes:
hash(b"hello")  # -2345678901  (process 1)
hash(b"hello")  # +8765432109  (process 2)
```

**Implications**:
- Never persist or transmit the result of `hash()` — it will be different on restart
- For stable, cross-process-safe hashing: use `hashlib.sha256(data).hexdigest()`
- This is why you can't use raw bytes as dict keys across processes

---

## The Windows Encoding Landscape

Windows has several separate encoding settings that evolved independently:

| Setting | Controlled by | What it affects |
|---------|--------------|-----------------|
| OEM code page (`chcp`) | System locale | Console display, `cp437` etc. |
| ANSI code page | System locale | `locale.getpreferredencoding()`, file I/O defaults |
| Python stdout | PEP 528 (3.6+) | `sys.stdout.encoding` — now UTF-8 for interactive |
| Python filesystem | PEP 529 (3.6+) | `sys.getfilesystemencoding()` — now UTF-8 |

**The confusing part**: On Windows, `chcp` might say 437, but `sys.stdout.encoding` says `utf-8` (since Python 3.6 + Windows 1809). The two settings coexist and can diverge — especially when output is redirected to a file, which reverts to ANSI code page.

**Python's response** (PEP 528 and 529): standardize Python-controlled settings to UTF-8. Legacy Windows APIs still use OEM/ANSI pages, but Python programs can now generally use UTF-8 consistently.

The remaining footgun: `open()` file encoding still defaults to `locale.getpreferredencoding()` — often `cp1252` on Windows. This is the most common source of encoding bugs.

---

## Key Design Trade-offs Summary

| Decision | Trade-off |
|----------|-----------|
| Explicit str/bytes separation | More code verbosity, but no silent encoding bugs |
| CPython flexible str (1/2/4 byte) | O(1) indexing at the cost of memory jumps with high code points |
| 4 normalization forms | Complexity, but necessary to represent existing character sets |
| No implicit encoding detection | Forces explicitness — better than silent mojibake |
| UTF-8 as default source encoding | Enables international variable names, comments in Python source |
