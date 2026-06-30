#!/usr/bin/env python3
"""
Build the public sales file from the private sales data.

Reads a private sales export (the "Canvas & Co Sales" Google Sheet, saved as a
markdown table by the Drive connector) plus the catalog (products.csv), and writes
sales_public.csv with ONLY three public columns: product, category, units_sold.

All private fields (customer_name, email, order_id, date, unit_price, line_total)
are dropped — they never reach the output. The script validates the result and
exits non-zero (writing nothing) if anything looks wrong, so a bad run can never
publish broken or unsafe data.

Usage:
    python scripts/build_public.py <sheet.md> <products.csv> <out.csv>
"""
import csv, sys

ALLOWED_HEADER = ["product", "category", "units_sold"]


def parse_sheet(path):
    """Parse the Drive 'natural language' markdown table into row dicts."""
    rows = []
    header = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            # skip a markdown separator row like | :-: | :-: | ...
            if all(set(c) <= set(":- ") and c for c in cells):
                continue
            if header is None:
                header = [c.replace("\\", "") for c in cells]
                continue
            rows.append(dict(zip(header, cells)))
    return rows


def main():
    sheet_path, products_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    # 1. Catalog = canonical product list (so 0-sellers are still listed).
    catalog = []
    with open(products_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            catalog.append({"name": r["name"].strip(), "category": r["category"].strip()})

    # 2. Sum units per product from the private sheet.
    units = {}
    for r in parse_sheet(sheet_path):
        name = r["product"].strip()
        try:
            q = int(r["quantity"])
        except (KeyError, ValueError):
            print(f"ABORT: bad quantity in row {r}", file=sys.stderr)
            sys.exit(2)
        units[name] = units.get(name, 0) + q

    # 3. Build sanitized rows (only the 3 allowed public columns).
    out_rows = [
        {"product": c["name"], "category": c["category"], "units_sold": units.get(c["name"], 0)}
        for c in catalog
    ]

    # 4. Validate before writing.
    assert out_rows, "ABORT: no catalog products"
    assert len(out_rows) == len(catalog), "ABORT: row count mismatch"
    for row in out_rows:
        assert list(row.keys()) == ALLOWED_HEADER, f"ABORT: stray columns in {row}"
        assert isinstance(row["units_sold"], int) and row["units_sold"] >= 0, \
            f"ABORT: bad units for {row['product']}"
    unknown = set(units) - {c["name"] for c in catalog}
    assert not unknown, f"ABORT: sheet has products not in catalog: {unknown}"

    # 5. Write (LF endings, matches existing file).
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ALLOWED_HEADER, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)

    print(f"OK: wrote {len(out_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
