#!/usr/bin/env python3
"""
Pull all non‑ENIGMA worksheets and also remove any data row that contains
the word “ENIGMA” (case‑insensitive) in *any* cell.
"""

import os, re, pandas as pd

# ---------- CONFIG ----------
XLSX_PATH  = "Isolates Inventory.xlsx"  # keep in the same folder as the script
OUTPUT_DIR = "extracted_sheets"

# Regex that matches any column name containing “ENIGMA”
ENIGMA_COL_RE = re.compile(r"enigma", re.IGNORECASE)

# Regex that matches the word “ENIGMA” **anywhere** in a cell value
ENIGMA_CELL_RE = re.compile(r"enigma", re.IGNORECASE)

# --------------------------------------------------------------------
def is_non_enigma_sheet(name: str) -> bool:
    """Skip any sheet whose name contains the word ENIGMA."""
    return "enigma" not in name.lower()

# --------------------------------------------------------------------
def main():
    # Load workbook
    try:
        xl = pd.ExcelFile(XLSX_PATH, engine="openpyxl")
    except FileNotFoundError:
        raise SystemExit(f"❌ File not found: {XLSX_PATH}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find candidate sheets (no “ENIGMA” in the sheet name)
    sheets = [s for s in xl.sheet_names if is_non_enigma_sheet(s)]
    if not sheets:
        raise SystemExit("❌  No non‑ENIGMA worksheets found.")

    all_dfs = []

    for sheet in sheets:
        # Heed merged header rows – try header=0 then header=1
        for hdr in (0, 1):
            try:
                df = xl.parse(sheet, header=hdr, dtype=str)
                if not df.empty:
                    break
            except Exception:
                continue
        else:
            print(f"⚠️  Sheet '{sheet}' is empty or unreadable; skipping.")
            continue

        # 1️⃣ Drop columns that contain “ENIGMA”
        cols_to_drop = [c for c in df.columns if ENIGMA_COL_RE.search(c)]
        df = df.drop(columns=cols_to_drop, errors="ignore")

        # 2️⃣ **Remove rows** that have “ENIGMA” in *any* cell
        #    (use `na=False` so that missing cells don't raise warnings)
        mask = df.apply(lambda row: row.str.contains("enigma", case=False, na=False).any(), axis=1)
        df = df[~mask]               # keep rows that do NOT match the mask

        # 3️⃣ Keep the source sheet identifier
        df["source_tab"] = sheet

        all_dfs.append(df)

    if not all_dfs:
        raise SystemExit("❌ No data left after filtering; check input file.")

    # Concatenate all sheets together
    master = pd.concat(all_dfs, ignore_index=True)

    # 4️⃣ Write the tidy CSV
    out_path = os.path.join(OUTPUT_DIR, "non_enigma_columns_and_rows_filtered.csv")
    master.to_csv(out_path, index=False, encoding="utf-8-sig")

    # 5️⃣ Print a concise summary
    print("\n✅  Extraction finished.")
    print(f"   → CSV written to: {out_path}")
    print(f"   → Total rows   : {len(master)}")
    print(f"   → Total columns: {len(master.columns)}\n")
    print("Top 5 rows (preview):")
    print(master.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
