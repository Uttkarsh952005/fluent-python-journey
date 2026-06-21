"""
Chapter 4: Benchmarks — Unicode Text Versus Bytes
===================================================
Measuring real encoding/decoding costs and memory overhead.

Run with: python benchmarks.py

Benchmarks:
  1. Memory: UTF-8 vs UTF-32 for strings with different char ranges
  2. encode/decode speed: UTF-8 vs UTF-16 vs latin-1
  3. str vs bytes: memory layout comparison
  4. Normalization overhead: NFC vs NFKC
  5. casefold() vs lower() overhead
  6. memoryview zero-copy vs bytearray slicing
"""

from __future__ import annotations

import array
import sys
import timeit
import tracemalloc
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")

NUMBER = 200_000


def section(title: str) -> None:
    print(f"\n{'=' * 62}")
    print(f"  {title}")
    print(f"{'=' * 62}")


def row(label: str, ns: float) -> None:
    print(f"  {label:<50} {ns:>8.1f} ns/op")


def measure(stmt: str, setup: str = "", n: int = NUMBER) -> float:
    elapsed = timeit.timeit(stmt=stmt, setup=setup, number=n, globals=globals())
    return (elapsed / n) * 1e9


# ─────────────────────────────────────────────────────────────────────────────
# Test data
# ─────────────────────────────────────────────────────────────────────────────

ASCII_TEXT = "Hello, World! " * 100          # pure ASCII, 1400 chars
LATIN_TEXT = "café résumé naïve " * 100      # Latin chars, mostly 2-byte in UTF-8
CJK_TEXT   = "日本語テスト " * 100           # CJK chars, 3-byte in UTF-8
MIXED_TEXT = ASCII_TEXT[:400] + LATIN_TEXT[:400] + CJK_TEXT[:200]  # realistic mix

# =============================================================================
# Benchmark 1: Memory — CPython str internal representation
# =============================================================================

section("Benchmark 1: str memory layout — CPython's 3 internal encodings")
print("  CPython stores str in the most compact form that fits all chars:")
print("  latin-1 (1 byte/char), UCS-2 (2 bytes/char), UCS-4 (4 bytes/char)\n")

texts = [
    ("ASCII only", ASCII_TEXT),
    ("Latin-1 range (é, à, ü)", LATIN_TEXT),
    ("CJK chars (日本語)", CJK_TEXT),
    ("Mixed", MIXED_TEXT),
]

print(f"  {'Text type':<30} {'chars':>8} {'str bytes':>12} {'bytes/char':>12}")
print("  " + "-" * 66)
for label, text in texts:
    size = sys.getsizeof(text)
    chars = len(text)
    bpc = size / chars if chars else 0
    print(f"  {label:<30} {chars:>8,} {size:>12,} {bpc:>12.2f}")

print("""
  CPython automatically picks:
    1-byte/char  if all code points <= U+00FF (latin-1 range)
    2-byte/char  if any code point > U+00FF but <= U+FFFF
    4-byte/char  if any code point > U+FFFF (emoji, rare chars)
  A single emoji in a string makes every char cost 4 bytes!
""")


# =============================================================================
# Benchmark 2: encode/decode speed across codecs
# =============================================================================

section("Benchmark 2: encode/decode speed — UTF-8 vs UTF-16 vs latin-1")
print("  Testing with ASCII-only text (best case for all codecs)\n")

for codec in ["utf-8", "utf-16", "utf-16-le", "latin-1", "ascii"]:
    t_enc = measure(f"ASCII_TEXT.encode({codec!r})")
    row(f"encode (ascii text) → {codec}", t_enc)

print()
print("  Testing with Latin text (has non-ASCII chars)\n")
for codec in ["utf-8", "utf-16-le"]:
    try:
        t_enc = measure(f"LATIN_TEXT.encode({codec!r})")
        row(f"encode (latin text) → {codec}", t_enc)
    except Exception as e:
        print(f"  encode latin text → {codec}: {e}")

print()
# Decode benchmarks
latin1_bytes = LATIN_TEXT.encode("utf-8")
for codec in ["utf-8", "utf-16-le"]:
    if codec == "utf-16-le":
        data = LATIN_TEXT.encode("utf-16-le")
    else:
        data = latin1_bytes
    t_dec = measure(f"data.decode({codec!r})", setup="data = data")
    row(f"decode (latin text) ← {codec}", t_dec)

print("""
  Rule of thumb:
    UTF-8:  fastest for ASCII-heavy data (1 byte/ASCII char, validated)
    UTF-16: fixed overhead from BOM, slower for ASCII-heavy text
    UTF-16-LE: no BOM overhead, faster than UTF-16 for encode
    latin-1: fastest possible (1:1 byte mapping) but limited to 256 chars
""")


# =============================================================================
# Benchmark 3: str vs bytes memory for the same content
# =============================================================================

section("Benchmark 3: str vs bytes memory for equivalent content")
print("  (str has per-char overhead; bytes is compact)\n")

samples = [
    ("ASCII text (100 chars)", "A" * 100),
    ("ASCII text (1000 chars)", "A" * 1000),
    ("Latin text (100 chars)", "é" * 100),
    ("CJK text (100 chars)", "中" * 100),
]

print(f"  {'Sample':<30} {'str bytes':>12} {'bytes obj':>12} {'ratio':>10}")
print("  " + "-" * 66)
for label, text in samples:
    str_size = sys.getsizeof(text)
    bytes_obj = text.encode("utf-8")
    bytes_size = sys.getsizeof(bytes_obj)
    ratio = str_size / bytes_size
    print(f"  {label:<30} {str_size:>12,} {bytes_size:>12,} {ratio:>9.2f}x")

print("""
  str has ~49 bytes of object overhead per string object.
  For very short strings, the overhead dominates.
  For large data: use bytes or array.array for memory efficiency.
  str with CJK uses 4 bytes/char internally due to UCS-4 encoding.
""")


# =============================================================================
# Benchmark 4: Normalization overhead
# =============================================================================

section("Benchmark 4: Unicode normalization overhead")
print("  (Is normalization cheap enough to do on every comparison?)\n")

from unicodedata import normalize

sample = "café résumé naïve " * 50   # ~900 chars, moderate diacritics

for form in ["NFC", "NFD", "NFKC", "NFKD"]:
    t = measure(f"normalize({form!r}, sample)", setup="sample = sample")
    row(f"normalize({form!r}, 900-char string)", t)

print("""
  NFC/NFD: lightweight — only combining char detection
  NFKC/NFKD: heavier — compatibility mappings require more lookups
  For user input normalization (NFC): cheap enough to do always
  For search index normalization (NFKC): do once at index time, not query time
""")


# =============================================================================
# Benchmark 5: casefold() vs lower()
# =============================================================================

section("Benchmark 5: casefold() vs lower()")
print("  (Use casefold() for Unicode-correct case-insensitive comparison)\n")

ascii_str  = "Hello World Python Programming"
latin_str  = "Café Résumé Naïve Straße"
german_str = "STRASSE MÜLLER BJÖRK" * 20

for label, text in [("ASCII string", ascii_str), ("Latin diacritics", latin_str), ("German capitals", german_str)]:
    t_lower = measure(f"text.lower()", setup=f"text = {text!r}")
    t_casefold = measure(f"text.casefold()", setup=f"text = {text!r}")
    print(f"  {label:<22} lower={t_lower:.0f}ns  casefold={t_casefold:.0f}ns  "
          f"delta={abs(t_casefold-t_lower):.0f}ns")

print("""
  lower() and casefold() have similar performance.
  Always use casefold() for case-insensitive Unicode comparison —
  it handles German ß → ss and other language-specific folding rules.
""")


# =============================================================================
# Benchmark 6: memoryview zero-copy vs slice copy
# =============================================================================

section("Benchmark 6: memoryview zero-copy vs bytearray slicing")
print("  (Do you pay a copy cost when slicing binary data?)\n")

SIZE = 10_000_000  # 10 MB buffer
big_buf = bytearray(b"A" * SIZE)
big_mv  = memoryview(big_buf)

# Slicing bytearray creates a COPY
t_ba_slice = measure("big_buf[1_000_000:2_000_000]", n=1_000)
row("bytearray[1M:2M]  (copies 1MB)", t_ba_slice)

# Slicing memoryview creates a VIEW (no copy)
t_mv_slice = measure("big_mv[1_000_000:2_000_000]", n=1_000)
row("memoryview[1M:2M] (no copy, zero-cost)", t_mv_slice)

ratio = t_ba_slice / t_mv_slice if t_mv_slice > 0 else float("inf")
print(f"\n  -> memoryview slice is {ratio:.0f}x faster than bytearray slice")
print("""
  bytearray slicing allocates new memory and copies bytes.
  memoryview slicing just creates a new view object (~200 bytes).
  For large binary data (image processing, network protocols, binary formats),
  memoryview eliminates copy overhead entirely.
""")


# =============================================================================
# Summary
# =============================================================================

section("Summary — Key Numbers")
print("""
  str memory:    ~49 byte overhead + 1/2/4 bytes per char (depends on max code point)
  bytes memory:  ~33 byte overhead + 1 byte per element
  encode UTF-8:  ~50-150 ns for typical short strings
  normalize NFC: ~200-500 ns for typical strings (cheap enough for user input)
  casefold():    same speed as lower() — always prefer it for Unicode correctness
  memoryview:    ~10x faster than bytearray for large binary slicing
""")
