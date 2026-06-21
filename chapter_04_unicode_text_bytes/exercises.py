"""
Chapter 4: Exercises — Unicode Text Versus Bytes
=================================================
Original exercises grounded in the book's actual examples (4-1 through 4-12).
These push at edge cases you'll encounter in real code.

Run with: python exercises.py
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


# =============================================================================
# EXERCISE 1: Encoding Detective
# =============================================================================
#
# Given a byte sequence of unknown encoding, try to identify it using
# heuristics inspired by the book's discussion (pages 128-130):
# - If it decodes as valid UTF-8 with high-bit bytes → probably UTF-8
# - BOM detection for UTF-16/UTF-32
# - Fallback: try common legacy encodings


def detect_encoding(data: bytes) -> str:
    """
    Heuristic encoding detector (educational, not production quality).
    Returns the most likely encoding as a string.
    """
    # UTF-32 BOM checks
    if data[:4] in (b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff"):
        return "utf-32"

    # UTF-16 BOM checks
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return "utf-16"

    # UTF-8 BOM check (UTF-8-SIG)
    if data[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"

    # Try strict UTF-8: if it succeeds with high-bit bytes, likely UTF-8
    if any(b > 127 for b in data):
        try:
            data.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            pass

    # ASCII: all bytes <= 127
    if all(b <= 127 for b in data):
        return "ascii"

    # Fall back to latin-1 (always succeeds, may produce garbage)
    return "latin-1 (assumed)"


def exercise_1_encoding_detective() -> None:
    print("=== Exercise 1: Encoding Detective ===\n")

    samples = [
        (b"hello world", "pure ASCII"),
        ("café".encode("utf-8"), "UTF-8 encoded 'café'"),
        ("café".encode("utf-8-sig"), "UTF-8 with BOM"),
        ("El Niño".encode("utf-16"), "UTF-16 with BOM"),
        (b"Montr\xe9al", "latin-1 'Montréal'"),
        (b"\x00\x00\xfe\xffhello", "UTF-32 BOM (big-endian)"),
    ]

    for data, desc in samples:
        detected = detect_encoding(data)
        print(f"  {desc:<35} → detected: {detected!r}")

    print("""
Note: True encoding detection (chardet/charset-normalizer) uses statistical
analysis of byte frequency patterns. This heuristic just covers common cases.
The book's lesson: "You can't reliably detect encoding — you must be told."
""")


# =============================================================================
# EXERCISE 2: Multi-Encoding Renderer
# =============================================================================
#
# Show how the same byte sequence looks when decoded with the wrong codec.
# This is how mojibake (garbled text) happens in the wild.


def exercise_2_mojibake_museum() -> None:
    """
    Demonstrate mojibake: correct bytes, wrong decoder.
    The 'museum' shows what real encoding bugs look like.
    """
    print("=== Exercise 2: Mojibake Museum ===\n")

    # Text that commonly gets garbled
    originals = [
        ("Montréal", "latin-1"),     # French, common in legacy databases
        ("São Paulo", "latin-1"),    # Portuguese
        ("Ångström", "latin-1"),     # Swedish
    ]

    # Wrong decoders to try on the latin-1 bytes
    wrong_decoders = ["cp1252", "iso8859_7", "koi8_r", "utf-8"]

    for text, orig_enc in originals:
        raw = text.encode(orig_enc)
        print(f"Original: {text!r} → encoded as {orig_enc}: {raw.hex()}")
        for dec in wrong_decoders:
            try:
                garbled = raw.decode(dec)
                match = "✓" if garbled == text else "✗"
                print(f"  {dec:<12} → {garbled!r} {match}")
            except UnicodeDecodeError as e:
                print(f"  {dec:<12} → UnicodeDecodeError (strict UTF-8 detected the error)")
        print()

    print("""Key insight:
  cp1252/latin-1 silently produce garbled text for wrong encodings.
  UTF-8 raises UnicodeDecodeError for invalid byte sequences.
  Prefer UTF-8: fail loudly is better than silent mojibake.
""")


# =============================================================================
# EXERCISE 3: Normalization Comparator
# =============================================================================
#
# Build a function that compares strings correctly despite normalization
# differences — the real-world use case from the book.


def normalize_for_comparison(text: str, form: str = "NFC") -> str:
    """Normalize text for reliable string comparison."""
    return unicodedata.normalize(form, text)


def caseless_equal(a: str, b: str) -> bool:
    """
    Unicode-correct case-insensitive comparison.
    Uses casefold() (not lower()) and normalizes both strings.
    """
    return (
        normalize_for_comparison(a.casefold())
        == normalize_for_comparison(b.casefold())
    )


def exercise_3_normalization() -> None:
    print("=== Exercise 3: Normalization Comparator ===\n")

    # Canonical equivalents — look identical, compare unequal without normalization
    pairs = [
        ("café", "cafe\N{COMBINING ACUTE ACCENT}"),          # NFC vs NFD
        ("naïve", "nai\N{COMBINING DIAERESIS}ve"),           # another NFC/NFD pair
        ("Ω", "\N{OHM SIGN}"),                               # Ω vs Ω (different code points!)
        ("ﬁle", "file"),                                     # ligature ﬁ vs fi (NFKC)
    ]

    print("Canonical equivalents (look same, compare different):")
    for a, b in pairs:
        raw_equal = a == b
        nfc_equal = normalize_for_comparison(a, "NFC") == normalize_for_comparison(b, "NFC")
        nfkc_equal = normalize_for_comparison(a, "NFKC") == normalize_for_comparison(b, "NFKC")
        print(f"  {a!r:12} vs {b!r:12}  raw={raw_equal}  NFC={nfc_equal}  NFKC={nfkc_equal}")

    # Case-insensitive comparison across languages
    print("\ncaseless_equal() — Unicode-correct case comparison:")
    case_pairs = [
        ("café", "CAFÉ"),
        ("straße", "STRASSE"),    # German: ß casefolds to ss
        ("Résumé", "RÉSUMÉ"),
        ("naïve", "NAÏVE"),
    ]
    for a, b in case_pairs:
        result = caseless_equal(a, b)
        print(f"  caseless_equal({a!r}, {b!r}) = {result}")

    print("""
Rule: Always normalize before comparing strings that may come from
different sources (user input, APIs, databases). Use NFC for storage,
NFKC for search/indexing.
""")


# =============================================================================
# EXERCISE 4: Safe File Writer
# =============================================================================
#
# Implement a file writer that ALWAYS uses UTF-8 and validates the content
# before writing — demonstrating the Unicode sandwich pattern.


def safe_write(path: str, content: str) -> dict[str, object]:
    """
    Unicode sandwich: normalize str → encode explicitly → write bytes.
    Validates that the content round-trips correctly.
    Returns a report of what was written.
    """
    # Normalize to NFC before storage (canonical form)
    normalized = unicodedata.normalize("NFC", content)
    encoded = normalized.encode("utf-8")

    Path(path).write_bytes(encoded)

    # Verify round-trip
    read_back = Path(path).read_bytes().decode("utf-8")
    roundtrip_ok = read_back == normalized

    return {
        "chars_written": len(normalized),
        "bytes_written": len(encoded),
        "encoding": "utf-8",
        "normalized_form": "NFC",
        "roundtrip_ok": roundtrip_ok,
        "bytes_per_char": len(encoded) / max(1, len(normalized)),
    }


def exercise_4_safe_file_writer() -> None:
    print("=== Exercise 4: Unicode Sandwich File Writer ===\n")

    test_cases = [
        ("Pure ASCII", "Hello, World!"),
        ("French (café)", "café au lait"),
        ("German (Straße)", "Guten Morgen, Straße"),
        ("Mixed scripts", "Python is 美丽 and ελληνικά"),
        ("Combining chars (NFD input)", "cafe\N{COMBINING ACUTE ACCENT}"),
    ]

    tmp = "_ch4_safe_write_test.txt"
    for desc, content in test_cases:
        report = safe_write(tmp, content)
        print(f"  {desc:<30}")
        print(f"    chars={report['chars_written']:4}  "
              f"bytes={report['bytes_written']:4}  "
              f"bytes/char={report['bytes_per_char']:.2f}  "
              f"roundtrip={report['roundtrip_ok']}")

    Path(tmp).unlink()
    print("""
Notice:
  'cafe' + combining accent (5 code points) → normalized to NFC (4 code points).
  Mixed scripts need more bytes/char since non-ASCII chars need 2-4 UTF-8 bytes.
  round-trip always True: UTF-8 is a perfect lossless encoding for all Unicode.
""")


# =============================================================================
# EXERCISE 5: ASCII Art Codec Comparison
# =============================================================================
#
# Show visually how the same code points are encoded differently across codecs.
# Inspired by Figure 4-1 in the book (page 123).


def exercise_5_codec_comparison() -> None:
    print("=== Exercise 5: Codec Comparison Table ===\n")

    test_chars = [
        "A",      # U+0041  — in all codecs
        "é",      # U+00E9  — in latin-1, utf-8; not in ascii
        "ñ",      # U+00F1  — in latin-1, utf-8; not in ascii
        "€",      # U+20AC  — in cp1252, utf-8; not in latin-1
        "中",     # U+4E2D  — only in utf-8/utf-32
        "𝄞",      # U+1D11E — musical G clef; utf-8 and utf-32 only
    ]

    codecs = ["ascii", "latin-1", "cp1252", "utf-8", "utf-16-le", "utf-32-le"]

    # Header
    header = f"  {'Char':^6} {'Code Point':^12} " + "".join(f"{c:^18}" for c in codecs)
    print(header)
    print("  " + "-" * (6 + 12 + 18 * len(codecs) + 4))

    for char in test_chars:
        cp = ord(char)
        row = f"  {char!r:^6} U+{cp:06X}     "
        for codec in codecs:
            try:
                b = char.encode(codec)
                row += f"{b.hex():^18}"
            except (UnicodeEncodeError, LookupError):
                row += f"{'N/A':^18}"
        print(row)

    print("""
Observations:
  'A' (U+0041): same byte value 41 in all encodings — ASCII is universal.
  'é' (U+00E9): latin-1 uses 1 byte (e9), utf-8 uses 2 (c3a9).
  '€' (U+20AC): not in latin-1! cp1252 adds it as byte 80. utf-8: e282ac.
  '中' (U+4E2D): only multi-byte encodings handle CJK characters.
  '𝄞' (U+1D11E): above BMP — needs 4 bytes in UTF-8, surrogate pair in UTF-16.
""")


# =============================================================================
# EXERCISE 6: Diacritic-Insensitive Search
# =============================================================================
#
# Real-world use case: search 'resume' and find 'résumé'.
# Remove diacritics from both query and indexed text.


def remove_diacritics(text: str) -> str:
    """Strip combining diacritic marks (category Mn) using NFD decomposition."""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def ascii_fold(text: str) -> str:
    """Lowercase + diacritic removal for search normalization."""
    return remove_diacritics(text.casefold())


def search(query: str, documents: list[str]) -> list[str]:
    """
    Diacritic-insensitive, case-insensitive document search.
    Both query and documents are ASCII-folded before comparison.
    """
    normalized_query = ascii_fold(query)
    results = []
    for doc in documents:
        if normalized_query in ascii_fold(doc):
            results.append(doc)
    return results


def exercise_6_diacritic_search() -> None:
    print("=== Exercise 6: Diacritic-Insensitive Search ===\n")

    corpus = [
        "My résumé includes experience at São Paulo offices.",
        "The Zürich naïve approach to café management.",
        "Strasse versus Straße: German spelling variants.",
        "Resume writing tips for software engineers.",
        "Pure ASCII document with no special characters.",
        "Ångström units are used in X-ray crystallography.",
    ]

    queries = ["resume", "sao paulo", "zurich", "strasse", "angstrom"]

    for query in queries:
        results = search(query, corpus)
        print(f"  Query: {query!r}")
        for r in results:
            print(f"    → {r!r}")
        if not results:
            print(f"    (no results)")
        print()

    # Show the folding that makes it work
    print("ASCII folding demo:")
    words = ["résumé", "Zürich", "Straße", "Ångström", "naïve"]
    for w in words:
        print(f"  {w!r:<16} → {ascii_fold(w)!r}")


# =============================================================================
# EXERCISE 7: Encoding Stress Test
# =============================================================================
#
# Test a function that must handle text from unknown sources — encode/decode
# defensively using error handlers, then report what was lost.


def safe_encode(text: str, encoding: str) -> tuple[bytes, list[str]]:
    """
    Encode text to the target encoding, collecting unencodable characters.
    Returns (encoded_bytes, list_of_lost_chars).
    """
    lost: list[str] = []
    result_parts: list[bytes] = []

    for char in text:
        try:
            result_parts.append(char.encode(encoding, errors="strict"))
        except UnicodeEncodeError:
            lost.append(char)
            # Replace with XML entity so we can see what was dropped
            result_parts.append(char.encode(encoding, errors="xmlcharrefreplace"))

    return b"".join(result_parts), lost


def exercise_7_encoding_stress() -> None:
    print("=== Exercise 7: Defensive Encoding ===\n")

    multilingual = (
        "Hello from Python! "
        "Café au lait. "
        "São Paulo & Zürich. "
        "日本語も大丈夫。"  # Japanese
        "Привет! "         # Russian
        "مرحبا"            # Arabic
    )

    target_encodings = ["ascii", "latin-1", "cp1252", "utf-8"]

    for enc in target_encodings:
        try:
            encoded, lost = safe_encode(multilingual, enc)
            loss_pct = len(lost) / len(multilingual) * 100
            print(f"  {enc:<10} bytes={len(encoded):5}  lost_chars={len(lost):3}  "
                  f"loss={loss_pct:.1f}%  "
                  f"{'✓ lossless' if not lost else f'lost: {lost[:5]}...' if len(lost) > 5 else f'lost: {lost}'}")
        except Exception as e:
            print(f"  {enc:<10} ERROR: {e}")

    print("""
Only UTF-8 handles all of Unicode losslessly.
  ascii:   loses everything above U+007F
  latin-1: loses everything above U+00FF
  cp1252:  loses CJK, Arabic, Cyrillic, etc.
  utf-8:   lossless — encodes all 1.1 million Unicode code points
""")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    exercise_1_encoding_detective()
    exercise_2_mojibake_museum()
    exercise_3_normalization()
    exercise_4_safe_file_writer()
    exercise_5_codec_comparison()
    exercise_6_diacritic_search()
    exercise_7_encoding_stress()
