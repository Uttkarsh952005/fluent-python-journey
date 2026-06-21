"""
Chapter 4: Unicode Text Versus Bytes — Examples
=================================================
Original implementations covering:

  Part 1  -- Characters, code points, and the encode/decode divide
  Part 2  -- bytes, bytearray, memoryview — the binary sequence types
  Part 3  -- Basic codecs: UTF-8, UTF-16, latin-1, cp1252
  Part 4  -- UnicodeEncodeError and UnicodeDecodeError handling
  Part 5  -- Unicode sandwich: the right way to handle text I/O
  Part 6  -- Unicode normalization: NFC, NFD, NFKC, NFKD
  Part 7  -- Case folding, diacritic removal, str.isascii()
  Part 8  -- Encoding defaults: locale, sys.stdout, platform traps

Run with: python examples.py
"""

from __future__ import annotations

import locale
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


# =============================================================================
# PART 1: Characters, Code Points, Encode/Decode
# =============================================================================


def char_and_codepoint_demo() -> None:
    """
    The fundamental divide: a 'character' is a Unicode code point (an integer).
    A 'byte sequence' is what gets stored or transmitted.
    encode = code points → bytes.  decode = bytes → code points.
    """
    print("=== Part 1: Characters, Code Points, Encode/Decode ===\n")

    s = "café"
    print(f"str: {s!r}  len={len(s)}")  # 4 Unicode characters

    # Encode to bytes — UTF-8 uses variable-length encoding
    b_utf8 = s.encode("utf-8")
    print(f"encode('utf-8'):  {b_utf8}  len={len(b_utf8)}")   # 5 bytes! 'é' = 2 bytes

    # Decode back
    decoded = b_utf8.decode("utf-8")
    print(f"decode('utf-8'): {decoded!r}  roundtrip_ok={decoded == s}\n")

    # Code points: each character has a unique integer identity
    print("Code points in 'café':")
    for char in s:
        cp = ord(char)
        name = unicodedata.name(char, "UNKNOWN")
        print(f"  U+{cp:04X}  {char!r}  {name}")

    # The same code point can be encoded differently
    print("\nSame code point, different encodings:")
    test_chars = [("é", "U+00E9"), ("€", "U+20AC"), ("A", "U+0041")]
    for char, label in test_chars:
        encodings = ["utf-8", "utf-16-le", "latin-1"]
        parts = []
        for enc in encodings:
            try:
                b = char.encode(enc)
                parts.append(f"{enc}:{b.hex()}")
            except UnicodeEncodeError:
                parts.append(f"{enc}:N/A")
        print(f"  {char!r} ({label}): {' | '.join(parts)}")


# =============================================================================
# PART 2: bytes, bytearray, memoryview
# =============================================================================


def binary_types_demo() -> None:
    """
    bytes   — immutable sequence of integers 0-255
    bytearray — mutable version of bytes
    memoryview — zero-copy view of binary data

    CRITICAL: bytes[0] returns an int; bytes[:1] returns a bytes object.
    This is different from str behavior and surprises everyone once.
    """
    print("\n=== Part 2: bytes, bytearray, memoryview ===\n")

    # bytes: immutable
    cafe = bytes("café", encoding="utf-8")
    print(f"bytes: {cafe}")
    print(f"cafe[0]:   {cafe[0]}   ← int (99 = ord('c'))")
    print(f"cafe[:1]:  {cafe[:1]}  ← bytes slice, even length-1 slices are bytes")
    print(f"cafe[-1]:  {cafe[-1]}  ← int (169 = 0xa9, part of é's UTF-8 encoding)\n")

    # bytearray: mutable
    ba = bytearray(cafe)
    print(f"bytearray: {ba}")
    ba[0] = ord("C")   # Capitalize the first byte
    print(f"After ba[0] = ord('C'): {ba}")
    print(f"bytearray slice: {ba[-2:]}  (also bytearray)\n")

    # Building bytes different ways
    print("Building bytes:")
    from_str   = bytes("hello", "ascii")
    from_ints  = bytes([104, 101, 108, 108, 111])   # ord values for 'hello'
    from_hex   = bytes.fromhex("68 65 6C 6C 6F")
    print(f"  from str+encoding: {from_str}")
    print(f"  from int iterable: {from_ints}")
    print(f"  from hex string:   {from_hex}")
    assert from_str == from_ints == from_hex
    print(f"  all equal: True\n")

    # memoryview: zero-copy reinterpretation
    import array
    nums = array.array("h", [-1, 0, 1, 2, 3])  # 5 signed shorts = 10 bytes
    mv = memoryview(nums)
    print(f"array as shorts: {list(mv.tolist())}")
    mv_bytes = mv.cast("B")   # same memory, viewed as unsigned bytes
    print(f"same bytes as unsigned chars: {list(mv_bytes.tolist())}")
    print(f"zero bytes copied — same memory object: {mv.obj is nums}\n")

    # The key memoryview insight: slicing does NOT copy
    big = bytearray(b"X" * 1_000_000)  # 1 MB
    view = memoryview(big)
    chunk = view[100_000:200_000]       # 100KB view — zero bytes copied
    print(f"memoryview slice of 1MB buffer: {chunk.nbytes:,} bytes, no copy made")


# =============================================================================
# PART 3: Basic Codecs
# =============================================================================


def codecs_demo() -> None:
    """
    Python bundles 100+ codecs. The critical ones to know:
    - utf-8:     variable-width, ASCII-compatible, dominant on the web (97%+)
    - utf-16:    fixed-width (mostly), uses BOM, common in Windows APIs
    - latin-1:   8-bit, 256 chars, basis of cp1252 and Unicode itself
    - cp1252:    Microsoft superset of latin-1, common Windows default
    - ascii:     7-bit, 128 chars, strict subset of all the above
    """
    print("\n=== Part 3: Codecs ===\n")

    samples = ["café", "El Niño", "Ω ohm", "naïve résumé"]

    print(f"{'Text':<20} {'utf-8':>14} {'utf-16-le':>14} {'latin-1':>14}")
    print("-" * 66)
    for text in samples:
        parts = []
        for enc in ["utf-8", "utf-16-le", "latin-1"]:
            try:
                b = text.encode(enc)
                parts.append(f"{b.hex()[:14]}")
            except UnicodeEncodeError:
                parts.append("N/A (unencodable)")
        print(f"{text:<20} {parts[0]:>14} {parts[1]:>14} {parts[2]:>14}")

    # BOM (Byte Order Mark) in UTF-16
    print("\nUTF-16 BOM demonstration:")
    u16 = "Hi".encode("utf-16")
    u16le = "Hi".encode("utf-16-le")
    u16be = "Hi".encode("utf-16-be")
    print(f"  utf-16   (with BOM):    {list(u16)}   BOM={u16[:2].hex()}")
    print(f"  utf-16-le (no BOM):     {list(u16le)}")
    print(f"  utf-16-be (no BOM):     {list(u16be)}")
    print("  BOM 0xff 0xfe = little-endian; 0xfe 0xff = big-endian")
    print("  UTF-16 auto-adds BOM; UTF-16-LE/BE are explicit, no BOM\n")

    # ASCII is a safe common subset
    print("str.isascii() — useful for choosing encoding strategy:")
    for text in ["hello", "café", "naïve", "pure ASCII text"]:
        print(f"  {text!r}.isascii() = {text.isascii()}")


# =============================================================================
# PART 4: Error Handling — UnicodeEncodeError and UnicodeDecodeError
# =============================================================================


def encoding_error_demo() -> None:
    """
    UnicodeEncodeError: str → bytes, character not in target encoding
    UnicodeDecodeError: bytes → str, bytes not valid in assumed encoding

    Four error handlers:
    'strict' (default) — raise immediately
    'ignore'            — silently drop unencodable characters (data loss!)
    'replace'           — substitute '?' or U+FFFD
    'xmlcharrefreplace' — XML entity (&#xxx;) — safe for XML output
    """
    print("\n=== Part 4: Encode/Decode Error Handling ===\n")

    city = "São Paulo"
    print(f"Encoding {city!r}:")

    # UTF-8 handles all Unicode — always succeeds
    print(f"  utf-8:          {city.encode('utf-8')}")

    # latin-1 happens to cover this string
    print(f"  latin-1:        {city.encode('latin-1')}")

    # cp437 cannot encode 'ã' — different error strategies:
    print(f"  cp437 strict:   ", end="")
    try:
        city.encode("cp437")
        print("(ok)")
    except UnicodeEncodeError as e:
        print(f"UnicodeEncodeError: {e}")

    print(f"  cp437 ignore:   {city.encode('cp437', errors='ignore')}")
    print(f"  cp437 replace:  {city.encode('cp437', errors='replace')}")
    print(f"  cp437 xmlcharrefreplace: {city.encode('cp437', errors='xmlcharrefreplace')}\n")

    # UnicodeDecodeError: wrong codec for binary data
    # b'\xe9' is 'é' in latin-1, but invalid in strict UTF-8
    octets = b"Montr\xe9al"  # latin-1 encoded "Montréal"
    print(f"Decoding {octets!r} with wrong encoding:")
    print(f"  cp1252 (works):        {octets.decode('cp1252')!r}  (correct)")
    print(f"  iso8859_7 (garbled):   {octets.decode('iso8859_7')!r}  (Greek codec!)")
    print(f"  koi8_r (garbled):      {octets.decode('koi8_r')!r}  (Russian codec!)")

    try:
        octets.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"  utf-8 strict:          UnicodeDecodeError: {e}")

    replaced = octets.decode("utf-8", errors="replace")
    print(f"  utf-8 replace:         {replaced!r}  (U+FFFD replacement char)\n")

    # Key insight: legacy 8-bit codecs (cp1252, latin-1, koi8_r) decode ANY bytes
    # without error — they just produce garbage. UTF-8 is strict — it detects errors.
    print("INSIGHT: latin-1/cp1252/koi8_r decode any byte sequence silently.")
    print("         UTF-8 raises UnicodeDecodeError on invalid byte sequences.")
    print("         This makes UTF-8 the SAFER default: fail loud > silent garbage.")


# =============================================================================
# PART 5: Unicode Sandwich — Text I/O Best Practice
# =============================================================================


def unicode_sandwich_demo() -> None:
    """
    The Unicode sandwich (Ned Batchelder's term, cited by Ramalho):

      bytes → [decode early] → str → [business logic] → str → [encode late] → bytes

    Rule: ALWAYS pass explicit encoding= when opening files.
    The default (locale.getpreferredencoding()) differs by OS and system config.
    On Linux/macOS: UTF-8.  On Windows: often cp1252.
    """
    print("\n=== Part 5: Unicode Sandwich — Text I/O ===\n")

    test_file = Path("_ch4_test_cafe.txt")

    # WRONG: write UTF-8, read with platform default
    test_file.write_bytes("café".encode("utf-8"))
    with open(test_file) as f:
        platform_encoding = f.encoding
        content_wrong = f.read()
    print(f"Platform default encoding: {platform_encoding!r}")
    print(f"Read with default: {content_wrong!r}  <- may be garbled on Windows\n")

    # CORRECT: explicit encoding on both sides
    test_file.write_text("café", encoding="utf-8")
    content_right = test_file.read_text(encoding="utf-8")
    print(f"Read with explicit utf-8: {content_right!r}  <- always correct\n")

    test_file.unlink()  # cleanup

    # The different encoding settings on a system
    print("Encoding defaults on this system:")
    print(f"  locale.getpreferredencoding(): {locale.getpreferredencoding()!r}")
    print(f"  sys.getdefaultencoding():      {sys.getdefaultencoding()!r}")
    print(f"  sys.getfilesystemencoding():   {sys.getfilesystemencoding()!r}")
    print(f"  sys.stdout.encoding:           {sys.stdout.encoding!r}")

    print("""
Unicode Sandwich rules:
  1. Decode bytes → str as EARLY as possible (at the I/O boundary)
  2. All internal business logic works with str objects only
  3. Encode str → bytes as LATE as possible (at the output boundary)
  4. ALWAYS specify encoding= explicitly — never rely on defaults
  5. Use UTF-8 everywhere unless you have a specific reason not to
""")


# =============================================================================
# PART 6: Unicode Normalization — NFC, NFD, NFKC, NFKD
# =============================================================================


def normalization_demo() -> None:
    """
    The same visual character can be encoded as multiple distinct code point sequences.
    'café' can be 4 code points (NFC) or 5 code points (NFD — 'e' + combining accent).

    NFC:  Composed — shortest form, what keyboards produce
    NFD:  Decomposed — base chars + combining marks
    NFKC: Compatibility composed — also maps 'ﬁ' → 'fi', '½' → '1/2'
    NFKD: Compatibility decomposed — most aggressive normalization

    Rule: normalize to NFC before comparing or storing user input.
    """
    print("\n=== Part 6: Unicode Normalization ===\n")

    # Two strings that look identical but are NOT equal
    s1 = "café"                          # é as single code point U+00E9
    s2 = "cafe\N{COMBINING ACUTE ACCENT}"  # e + combining accent U+0301

    print(f"s1 = {s1!r}  len={len(s1)} code points")
    print(f"s2 = {s2!r}  len={len(s2)} code points")
    print(f"s1 == s2:  {s1 == s2}  (different code point sequences!)")
    print(f"s1 looks like s2: True (same visual rendering)\n")

    # Normalization resolves this
    from unicodedata import normalize

    for form in ["NFC", "NFD", "NFKC", "NFKD"]:
        n1 = normalize(form, s1)
        n2 = normalize(form, s2)
        print(f"{form}: len(n1)={len(n1)}, len(n2)={len(n2)}, equal={n1 == n2}")

    # NFKC maps compatibility characters
    print("\nNFKC compatibility mappings:")
    compat_chars = [
        ("\N{VULGAR FRACTION ONE HALF}", "½ → 1/2"),
        ("\N{LATIN SMALL LIGATURE FI}", "ﬁ → fi"),
        ("\N{OHM SIGN}", "Ω ohm → Ω omega"),
        ("\N{MICRO SIGN}", "µ micro → μ mu"),
    ]
    for char, desc in compat_chars:
        nfkc = normalize("NFKC", char)
        nfc = normalize("NFC", char)
        changed = nfkc != nfc
        print(f"  {desc}: NFC={nfc!r}  NFKC={nfkc!r}  changed={changed}")

    print("""
When to use which:
  NFC  — storing/comparing user-typed text (safe, reversible)
  NFD  — splitting base chars from diacritics (e.g., accent stripping)
  NFKC — search/indexing (maps ligatures, fractions → canonical forms)
  NFKD — same but decomposed (use before diacritic removal)
  WARNING: NFKC/NFKD can change meaning ('½' → '1/2' changes character count)
""")


# =============================================================================
# PART 7: Case Folding and Diacritic Removal
# =============================================================================


def case_folding_demo() -> None:
    """
    str.casefold() — Unicode-aware case folding for comparison.
    More aggressive than str.lower() for non-ASCII characters.

    Diacritic removal: normalize to NFD, then filter out combining marks.
    Useful for fuzzy search (searching 'resume' finds 'résumé').
    """
    print("\n=== Part 7: Case Folding and Diacritic Removal ===\n")

    # casefold() vs lower()
    test_words = ["Straße", "ÑOÑO", "Ω", "ß"]
    print("casefold() vs lower():")
    for word in test_words:
        lower = word.lower()
        folded = word.casefold()
        diff = "DIFFERENT" if lower != folded else "same"
        print(f"  {word!r:<12} lower={lower!r:<12} casefold={folded!r:<12} [{diff}]")

    # German ß: lower() keeps ß, casefold() converts to 'ss'
    # This is why casefold() is right for case-insensitive comparison

    def remove_diacritics(text: str) -> str:
        """
        Strip all diacritic marks from text.
        NFD decomposes: 'é' → 'e' + combining accent.
        Then filter out anything in category 'Mn' (Mark, Nonspacing).
        """
        nfd = unicodedata.normalize("NFD", text)
        return "".join(
            c for c in nfd
            if unicodedata.category(c) != "Mn"
        )

    print("\nDiacritic removal (for fuzzy search):")
    examples = ["café", "naïve", "résumé", "São Paulo", "Zürich", "Ångström"]
    for word in examples:
        stripped = remove_diacritics(word)
        print(f"  {word!r:<16} → {stripped!r}")

    print("""
Normalized comparison for search:
  query 'resume' should find 'résumé' in a document index.
  Solution: normalize both query and indexed terms with remove_diacritics()
  before comparison. This is called 'ASCII folding' in search engines.
""")


# =============================================================================
# PART 8: Encoding Defaults — The Platform Trap
# =============================================================================


def encoding_defaults_demo() -> None:
    """
    Python's encoding defaults differ by OS:

    Linux/macOS:  UTF-8 everywhere (safe)
    Windows:      locale encoding (often cp1252) for files,
                  UTF-8 for console I/O in interactive mode,
                  cp1252 when stdout is redirected to a file

    This is the source of the majority of "works on my machine" encoding bugs.
    """
    print("\n=== Part 8: Encoding Defaults ===\n")

    settings = {
        "locale.getpreferredencoding()": locale.getpreferredencoding(),
        "sys.getdefaultencoding()":      sys.getdefaultencoding(),
        "sys.getfilesystemencoding()":   sys.getfilesystemencoding(),
        "sys.stdout.encoding":           sys.stdout.encoding,
        "sys.stdin.encoding":            getattr(sys.stdin, "encoding", "N/A"),
    }

    for name, value in settings.items():
        print(f"  {name:<40} {value!r}")

    print(f"\n  Running on: {sys.platform}")

    print("""
The DANGER zone:
  open('file.txt', 'w').write('café')         # uses platform default!
  open('file.txt').read()                     # same default — might work

  But if file was written on Linux (UTF-8) and read on Windows (cp1252):
    b'\\xc3\\xa9' (UTF-8 for é) decoded as cp1252 = 'Ã©' (mojibake!)

THE RULE: Always pass encoding= explicitly.
  open('file.txt', 'w', encoding='utf-8').write('café')  # safe everywhere
  open('file.txt', encoding='utf-8').read()               # safe everywhere
""")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    char_and_codepoint_demo()
    binary_types_demo()
    codecs_demo()
    encoding_error_demo()
    unicode_sandwich_demo()
    normalization_demo()
    case_folding_demo()
    encoding_defaults_demo()
