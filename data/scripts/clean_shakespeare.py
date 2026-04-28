#!/usr/bin/env python3
"""
Clean Shakespeare .txt files in source-raw/ by removing:
  - Project Gutenberg headers and footers
  - Title pages ("by William Shakespeare")
  - Table of Contents
  - Dramatis Personæ / cast lists

The actual play text is preserved, starting from the Prologue
(if present) or ACT I.

Originals are NEVER modified. Cleaned files are written to
  ../source-clean/  (sibling to source-raw/ inside data/)
preserving filenames.
"""

import re
import shutil
from pathlib import Path

# All paths cascade from PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent   # shakespeare/
DATA_DIR     = PROJECT_ROOT / "data"
BASE         = DATA_DIR / "source-raw"                         # data/source-raw/
OUTPUT       = DATA_DIR / "source-clean"                       # data/source-clean/


# ─── Utility ────────────────────────────────

def write_clean(src: Path, text: str):
    """Write cleaned text to OUTPUT, mirroring the source path relative to BASE."""
    rel = src.relative_to(BASE)
    dest = OUTPUT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


# ─── Gutenberg removal ─────────────────────

def strip_gutenberg(text: str) -> str:
    """Remove everything before the START marker and after the END marker."""
    # Header
    start_pat = re.compile(
        r"^\*{3}\s*START OF (?:THE |THIS )?PROJECT GUTENBERG.*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = start_pat.search(text)
    if m:
        text = text[m.end():]

    # Primary footer
    end_pat = re.compile(
        r"^\*{3}\s*END OF (?:THE |THIS )?PROJECT GUTENBERG.*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = end_pat.search(text)
    if m:
        text = text[: m.start()]

    # Secondary footer (without ***)
    end2_pat = re.compile(
        r"^End of (?:the )?Project Gutenberg.*$",
        re.MULTILINE | re.IGNORECASE,
    )
    m = end2_pat.search(text)
    if m:
        text = text[: m.start()]

    return text.strip() + "\n"


# ─── Front-matter removal ──────────────────

def strip_front_matter(text: str) -> str:
    """
    Remove everything before the play text begins.

    Strategy: find the FIRST "ACT I" heading that appears after all the
    front matter.  If a Prologue heading appears *before* that ACT I,
    use the Prologue as the start instead (e.g. Romeo and Juliet).

    This avoids false matches on "PROLOGUE" that appear mid-play as
    character speech headings (e.g. A Midsummer Night's Dream Act 5).
    """
    lines = text.split("\n")

    act_i_pat = re.compile(r"^\s*ACT\s+I\b", re.IGNORECASE)
    prologue_pats = [
        re.compile(r"^\s*THE PROLOGUE\s*$", re.IGNORECASE),
        re.compile(r"^\s*PROLOGUE\.?\s*$", re.IGNORECASE),
    ]

    # Find the first ACT I line
    act_i_idx = None
    for i, line in enumerate(lines):
        if act_i_pat.search(line):
            act_i_idx = i
            break

    # Look for a Prologue heading BEFORE ACT I (or in the whole file if no ACT I)
    search_limit = act_i_idx if act_i_idx is not None else len(lines)
    for pat in prologue_pats:
        for i, line in enumerate(lines[:search_limit]):
            if pat.search(line):
                return "\n".join(lines[i:])

    # Use ACT I if found
    if act_i_idx is not None:
        return "\n".join(lines[act_i_idx:])

    # Fallback: return as-is
    return text


# ─── Full cleaning pipeline ────────────────

def clean_shakespeare(text: str) -> str:
    """Run the full cleaning pipeline on a Shakespeare Gutenberg text."""
    text = strip_gutenberg(text)
    text = strip_front_matter(text)
    # Collapse runs of 4+ blank lines down to 3
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


# ─── Main ──────────────────────────────────

def main():
    print("=" * 60)
    print("Shakespeare Cleaner")
    print("=" * 60)
    print(f"  Reading from : {BASE}")
    print(f"  Writing to   : {OUTPUT}")
    print()

    if not BASE.exists():
        print(f"ERROR: source directory not found: {BASE}")
        return

    # Wipe previous output so it's always a fresh clean
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    txt_files = sorted(BASE.glob("*.txt"))
    if not txt_files:
        print("  No .txt files found.")
        return

    for f in txt_files:
        raw = f.read_text(encoding="utf-8", errors="replace")
        cleaned = clean_shakespeare(raw)
        write_clean(f, cleaned)
        print(f"  {f.name}  ({len(raw):,} → {len(cleaned):,} chars)")

    print()
    print("=" * 60)
    print(f"Done!  Clean files → {OUTPUT}")
    print("Originals in source-raw/ are untouched.")
    print("=" * 60)


if __name__ == "__main__":
    main()
