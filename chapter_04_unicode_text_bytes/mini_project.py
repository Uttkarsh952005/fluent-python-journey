"""
Chapter 4: Mini Project — Unicode-Safe CSV Processor
=====================================================
A real-world tool that handles the most common encoding challenges in data work:
ingesting CSV files from unknown sources, normalizing text, detecting encoding,
and exporting to clean UTF-8.

Problems this solves:
  - CSV files from Windows with cp1252 encoding
  - Mixed encodings in the same dataset
  - Diacritics inconsistency (é vs e + combining accent)
  - Column names with spaces, diacritics, and inconsistent casing
  - BOM markers breaking pandas/csv header detection

Features:
  - Auto-detects encoding (UTF-8, UTF-8-SIG, Latin-1, CP1252)
  - Normalizes all text to NFC form
  - ASCII-folds column names for safe programmatic access
  - Reports encoding errors and substitutions
  - Exports clean UTF-8 CSV

Run with: python mini_project.py
"""

from __future__ import annotations

import csv
import io
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


# =============================================================================
# Encoding Detection
# =============================================================================


def detect_encoding(raw: bytes) -> str:
    """
    Heuristic encoding detector for common cases:
    UTF-8-SIG (with BOM), UTF-8, and 8-bit fallback encodings.
    Production code should use charset-normalizer or chardet.
    """
    # BOM detection first — most reliable
    if raw[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return "utf-16"

    # Try strict UTF-8 — if it succeeds with non-ASCII bytes, probably UTF-8
    if any(b > 127 for b in raw):
        try:
            raw.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            pass

    # All bytes in ASCII range
    if all(b <= 127 for b in raw):
        return "ascii"

    # Fallback: assume cp1252 for Windows-origin files
    return "cp1252"


# =============================================================================
# Text Normalization
# =============================================================================


def normalize_text(text: str) -> str:
    """
    Normalize text for storage:
      1. Unicode NFC (canonical composition — shortest form)
      2. Strip leading/trailing whitespace
    Does NOT remove diacritics — that's for search, not storage.
    """
    return unicodedata.normalize("NFC", text.strip())


def ascii_fold(text: str) -> str:
    """
    Create an ASCII-safe identifier from text:
      1. Casefold (Unicode-correct lowercase)
      2. NFD decompose (split diacritics from base chars)
      3. Strip combining marks (category Mn)
      4. Replace non-alphanumeric with underscore
    Used for column name normalization.
    """
    casefolded = text.casefold()
    nfd = unicodedata.normalize("NFD", casefolded)
    stripped = "".join(
        c for c in nfd
        if unicodedata.category(c) != "Mn"  # Mn = Mark, Nonspacing
    )
    # Replace spaces and non-word chars with underscore
    result = "".join(c if c.isalnum() else "_" for c in stripped)
    # Collapse multiple underscores
    while "__" in result:
        result = result.replace("__", "_")
    return result.strip("_")


# =============================================================================
# CSV Processor
# =============================================================================


@dataclass
class ProcessingReport:
    """Summary of what happened during processing."""
    source_encoding: str
    rows_processed: int
    rows_skipped: int
    columns_renamed: dict[str, str] = field(default_factory=dict)
    encoding_substitutions: int = 0
    normalization_changes: int = 0

    def print_summary(self) -> None:
        print(f"\n{'─' * 50}")
        print(f"  Processing Report")
        print(f"{'─' * 50}")
        print(f"  Source encoding detected:  {self.source_encoding!r}")
        print(f"  Rows processed:            {self.rows_processed}")
        print(f"  Rows skipped (empty):      {self.rows_skipped}")
        print(f"  Normalization changes:     {self.normalization_changes}")
        print(f"  Encoding substitutions:    {self.encoding_substitutions}")
        if self.columns_renamed:
            print(f"  Columns renamed:")
            for orig, new in self.columns_renamed.items():
                print(f"    {orig!r:20} → {new!r}")
        print(f"{'─' * 50}\n")


class UnicodeCSVProcessor:
    """
    Processes CSV files from arbitrary encodings → clean UTF-8 output.

    Design: Unicode sandwich pattern
      1. Read bytes  → decode once → work with str throughout
      2. Normalize all str values (NFC)
      3. Output as UTF-8 bytes at the very end
    """

    def __init__(self) -> None:
        self.report = ProcessingReport(
            source_encoding="unknown",
            rows_processed=0,
            rows_skipped=0,
        )

    def process(
        self,
        source: Path | str,
        dest: Path | str,
        normalize_columns: bool = True,
    ) -> ProcessingReport:
        """
        Process a CSV file: detect encoding → normalize → write UTF-8.
        """
        source_path = Path(source)
        dest_path = Path(dest)

        # ── Step 1: Read raw bytes ────────────────────────────────────────
        raw = source_path.read_bytes()

        # ── Step 2: Detect encoding and decode ONCE (early decode) ────────
        encoding = detect_encoding(raw)
        self.report.source_encoding = encoding

        try:
            text = raw.decode(encoding, errors="replace")
            # Count replacement chars as substitutions
            self.report.encoding_substitutions = text.count("\ufffd")
        except LookupError:
            text = raw.decode("latin-1", errors="replace")
            self.report.source_encoding = f"latin-1 (fallback from {encoding})"

        # ── Step 3: Parse CSV in-memory (working entirely with str) ───────
        reader = csv.DictReader(io.StringIO(text))

        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")

        # Normalize column names
        original_cols = list(reader.fieldnames)
        if normalize_columns:
            new_cols = [ascii_fold(col) for col in original_cols]
            renamed = {
                orig: new
                for orig, new in zip(original_cols, new_cols)
                if orig != new
            }
            self.report.columns_renamed = renamed
            fieldnames = new_cols
        else:
            fieldnames = original_cols

        # ── Step 4: Process rows (normalize values) ────────────────────────
        processed_rows: list[dict[str, str]] = []
        for row in reader:
            if all(v.strip() == "" for v in row.values()):
                self.report.rows_skipped += 1
                continue

            normalized_row: dict[str, str] = {}
            for col_orig, col_new in zip(original_cols, fieldnames):
                raw_val = row.get(col_orig, "")
                normalized_val = normalize_text(raw_val)
                if normalized_val != raw_val.strip():
                    self.report.normalization_changes += 1
                normalized_row[col_new] = normalized_val

            processed_rows.append(normalized_row)
            self.report.rows_processed += 1

        # ── Step 5: Write UTF-8 output (late encode) ──────────────────────
        output_buf = io.StringIO()
        writer = csv.DictWriter(
            output_buf,
            fieldnames=fieldnames,
            lineterminator="\n",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        writer.writerows(processed_rows)

        # Encode to bytes at the very last step — UTF-8, explicit, always
        dest_path.write_bytes(output_buf.getvalue().encode("utf-8"))

        return self.report


# =============================================================================
# Demo: Generate sample "dirty" CSV files and process them
# =============================================================================


def generate_latin1_csv(path: Path) -> None:
    """Create a CSV with latin-1 encoding simulating legacy Windows export."""
    rows = [
        "Nom,Prénom,Ville,Salaire\n",
        "Dupont,François,São Paulo,85000\n",
        "Müller,Léa,Zürich,92000\n",
        "García,José,México City,78000\n",
        "Björk,Sigríður,Reykjavik,88000\n",
        "Smith,John,New York,95000\n",
    ]
    data = "".join(rows).encode("latin-1", errors="replace")
    path.write_bytes(data)


def generate_utf8sig_csv(path: Path) -> None:
    """Create a CSV with UTF-8-SIG (Windows Notepad / Excel export style)."""
    rows = [
        "Résumé Title,Candidate Name,Location,Experience (yrs)\n",
        "Senior Developer,María García,São Paulo,8\n",
        "Staff Engineer,François Dupont,Paris,12\n",
        "Lead Designer,Naïve Approach,Zürich,5\n",
    ]
    # UTF-8-SIG: UTF-8 with BOM (common Excel/Windows export)
    data = "\ufeff" + "".join(rows)
    path.write_bytes(data.encode("utf-8"))


def main() -> None:
    print("=" * 60)
    print("  Unicode-Safe CSV Processor")
    print("  Chapter 4 Mini Project — Unicode Text Versus Bytes")
    print("=" * 60)

    tmp_dir = Path("_ch4_csv_demo")
    tmp_dir.mkdir(exist_ok=True)

    # ── Demo 1: Latin-1 CSV ───────────────────────────────────────────────
    print("\n[DEMO 1] Processing latin-1 encoded CSV (legacy Windows export)\n")
    src1 = tmp_dir / "employees_latin1.csv"
    dst1 = tmp_dir / "employees_clean.csv"
    generate_latin1_csv(src1)

    processor = UnicodeCSVProcessor()
    report1 = processor.process(src1, dst1, normalize_columns=True)
    report1.print_summary()

    print("Clean output (UTF-8):")
    print(dst1.read_text(encoding="utf-8"))

    # ── Demo 2: UTF-8-SIG CSV ────────────────────────────────────────────
    print("[DEMO 2] Processing UTF-8-SIG CSV (Excel/Windows export with BOM)\n")
    src2 = tmp_dir / "resumes_utf8sig.csv"
    dst2 = tmp_dir / "resumes_clean.csv"
    generate_utf8sig_csv(src2)

    processor2 = UnicodeCSVProcessor()
    report2 = processor2.process(src2, dst2, normalize_columns=True)
    report2.print_summary()

    print("Clean output (UTF-8, no BOM, normalized column names):")
    print(dst2.read_text(encoding="utf-8"))

    # ── Demo 3: Normalization showcase ────────────────────────────────────
    print("[DEMO 3] Normalization — NFC canonical form\n")
    # Write a CSV where some values use NFD (decomposed) encoding
    nfd_content = (
        "name,description\n"
        "cafe\N{COMBINING ACUTE ACCENT},french drink\n"  # NFD 'café'
        "na\N{COMBINING DIAERESIS}ve,simple\n"           # NFD 'naïve'
    )
    src3 = tmp_dir / "nfd_input.csv"
    dst3 = tmp_dir / "nfc_output.csv"
    src3.write_bytes(nfd_content.encode("utf-8"))

    processor3 = UnicodeCSVProcessor()
    report3 = processor3.process(src3, dst3, normalize_columns=False)

    print(f"  NFD input  'cafe+accent' len={len('cafe\N{COMBINING ACUTE ACCENT}')}")
    result_name = dst3.read_text(encoding="utf-8").splitlines()[1].split(",")[0]
    print(f"  NFC output {result_name!r} len={len(result_name)}")
    print(f"  Normalization changes: {report3.normalization_changes}")
    print(f"  (NFD 5 code points → NFC 4 code points)\n")

    # ── Cleanup ────────────────────────────────────────────────────────────
    import shutil
    shutil.rmtree(tmp_dir)

    print("=" * 60)
    print("  Key Concepts Demonstrated")
    print("=" * 60)
    print("""
  Unicode Sandwich:
    1. Read bytes
    2. Detect encoding, decode ONCE → str
    3. All processing in str (normalize, transform)
    4. Encode to UTF-8 bytes at the very end

  Why this matters in data engineering:
    - CSV files from Excel/Windows often have BOM or cp1252 encoding
    - Mixing encodings causes pandas to misread characters silently
    - NFD vs NFC mismatches cause duplicate rows in GROUP BY queries
    - Column names with 'é' fail when used as Python identifiers
    - ASCII-folded column names work in all languages (SQL, Python, JSON)
""")


if __name__ == "__main__":
    main()
