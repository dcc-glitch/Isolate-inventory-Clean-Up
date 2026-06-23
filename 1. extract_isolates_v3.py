#!/usr/bin/env python3
"""
Pull all worksheets that **do NOT** contain the word "ENIGMA" in any column header
(and also drop any sheet that *tells* you that word in the sheet name).
Add a column indicating the original tab, then output a single CSV.

Author: CBorg Chat (Gemma‑based)
Date:   2026‑06‑23
"""

import os
import re
import sys
import pandas as pd

# ---------- CONFIG ----------
XLSX_PATH = "Isolates Inventory.xlsx"   # file must live in the same folder
OUTPUT_DIR = "extracted_sheets"

# If you want to *force‑skip* certain sheets (e.g. "gracielle")
SHEETS_TO_EXCLUDE = {"gracielle"}      # set of exact sheet names (case‑sensitive)

# Regex that matches the word "ENIGMA" in any string (case‑insensitive)
ENIGMA_RE = re.compile(r"enigma", re.IGNORECASE)

# --------------------------------------------------------------------
def sheet_has_enigma_header(df: pd.DataFrame) -> bool:
    """Return True if **any** column header contains 'ENIGMA'."""
    return any(ENIGMA_RE.search(col) for col in df.columns)

# --------------------------------------------------------------------
def main():
    try:
        xl = pd.ExcelFile(XLSX_PATH, engine="openpyxl")
    except FileNotFoundError:
        raise SystemExit(f"❌  File not found: {XLSX_PATH}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_dfs = []

    for sheet in xl.sheet_names:
        # 1️⃣ Skip by *sheet name* if it contains ENIGMA (already excluded)
        if "enigma" in sheet.lower():
            print(f"⏭️  Skipping sheet '{sheet}' (name contains 'ENIGMA')")
            continue

        # 1️⃣2️⃣ Skip explicitly listed names
        if sheet in SHEETS_TO_EXCLUDE:
            print(f"⏭️  Skipping sheet '{sheet}' (explicitly on exclude list)")
            continue

        # 2️⃣ Read sheet (try header row 0, then 1)
        df = None
        for hdr in (0, 1):
            try:
                df = xl.parse(sheet, header=hdr, dtype=str)
                if not df.empty:
                    break
            except Exception:
                continue
        if df is None or df.empty:
            print(f"⚠️  Sheet '{sheet}' could not be read; skipping.")
            continue

        # 3️⃣ **Check column headers**
        if sheet_has_enigma_header(df):
            print(f"⏭️  Skipping sheet '{sheet}' (contains 'ENIGMA' in a header)")
            continue

        # 4️⃣ Add the tab identifier
        df["source_tab"] = sheet

        # 5️⃣ (Optional) Remove rows that contain 'ENIGMA' in any *cell*
        #    (keeps data cleaner if such accidental entries exist)
        mask = df.apply(lambda row: row.str.contains("enigma", case=False, na=False).any(), axis=1)
        df = df[~mask]

        all_dfs.append(df)

    if not all_dfs:
        raise SystemExit("❌  No sheets passed the filtering criteria.")

    # ------------------------------------------------------------------
    # Concatenate into one master DataFrame
    # ------------------------------------------------------------------
    master = pd.concat(all_dfs, ignore_index=True)

    # ------------------------------------------------------------------
    # Write out a tidy CSV
    # ------------------------------------------------------------------
    out_path = os.path.join(OUTPUT_DIR, "isolates_without_enigma.csv")
    master.to_csv(out_path, index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------------
    # Show a concise summary
    # ------------------------------------------------------------------
    print("\n✅  Extraction finished.")
    print(f"   → CSV written to: {out_path}")
    print(f"   → Total rows   : {len(master)}")
    print(f"   → Total columns: {len(master.columns)}")
    print("\nTop 5 rows (preview):")
    print(master.head(5).to_string(index=False))

if __name__ == "__main__":
    main()


