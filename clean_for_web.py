#!/usr/bin/env python3
"""
Clean the CSV that was produced by extract_isolates_v4.py.
The script automatically finds the single CSV in
`extracted_sheets/`, keeps the columns you want,
renames them to snake_case, normalises dates,
sorts by isolate ID, and writes a tidy file in
the `public/` folder (or whatever folder you choose).

Author: CBorg Chat (Gemma‑based)
Date:   2026‑06‑23
"""

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# 1️⃣  Where the extraction script puts its CSV
# ------------------------------------------------------------------
EXTRACT_DIR = Path("extracted_sheets")

# Find the *only* CSV file that lives there.
candidates = sorted(EXTRACT_DIR.glob("*.csv"))

if not candidates:
    raise FileNotFoundError(
        f"❌  No CSV found in {EXTRACT_DIR}\n"
        "   Did you run extract_isolates_v4.py?"
    )

# If you really have two files in that folder, pick the most recent
# (or decide how you want to pick one).
input_file = candidates[-1]    # last in the sorted list
print(f"📂  Using input file: {input_file}")

# ------------------------------------------------------------------
# 2️⃣  Columns you actually want to keep
# ------------------------------------------------------------------
KEEP_COLUMNS = [
    "Real Isolate ID",
    "Project",
    "Source",
    "Date Isolated",
    "Source_tab",
    "Genome Sequence",
]

# ------------------------------------------------------------------
# 3️⃣  Rename mapping – snake_case
# ------------------------------------------------------------------
RENAME_MAP = {
    "Real Isolate ID":   "real_isolate_id",
    "Project":            "project",
    "Source":             "source",
    "Date Isolated":     "date_isolated",
    "Source_tab":         "source_tab",
    "Genome Sequence":   "genome_sequence",
}

# ------------------------------------------------------------------
# 4️⃣  Main routine
# ------------------------------------------------------------------
def main():
    # Load as string to keep every cell intact
    df = pd.read_csv(input_file, dtype=str)

    # Keep only the columns we care about
    df = df[[c for c in KEEP_COLUMNS if c in df.columns]]

    # Rename columns
    df = df.rename(columns=RENAME_MAP)

    # Normalise the date column to ISO format
    df["date_isolated"] = pd.to_datetime(df["date_isolated"], errors="coerce")
    df["date_isolated"] = df["date_isolated"].dt.strftime("%Y-%m-%d")

    # Sort by the isolate ID (numeric/alpha)
    df = df.sort_values("real_isolate_id", ignore_index=True)

    # Output folder + file
    output_dir  = Path("public")          # default – change if you have a different path
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "cleaned_isolates.csv"

    # Write CSV (UTF‑8 with BOM so Excel opens nicely)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"\n✅  Finished.  Clean CSV written to: {output_file}")
    print(f"   → Rows: {len(df)}   Columns: {len(df.columns)}")

# ------------------------------------------------------------------
if __name__ == "__main__":
    main()