#!/usr/bin/env python3
import os, re, argparse
from typing import List, Dict, Optional, Tuple
import psycopg2
from psycopg2.extras import execute_values

# ---------------- DB ----------------
def connect():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "api_genie"),
        user=os.getenv("POSTGRES_USER", "api_genie"),
        password=os.getenv("POSTGRES_PASSWORD", "api_genie_pw"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )

# ------------- Parsing --------------
# Category like: "### Animals"
RE_CATEGORY = re.compile(r"^###\s+(.+?)\s*$")

# Header line can be:
# "API | Description | Auth | HTTPS | CORS"
# "| API | Description | Auth | HTTPS | CORS |"
RE_TABLE_HDR = re.compile(
    r"^\s*\|?\s*API\s*\|\s*Description\s*\|\s*Auth\s*\|\s*HTTPS\s*\|\s*CORS\s*\|?\s*$",
    re.I,
)

# Alignment row (tolerant): e.g. "|:---|:---|:---|:---|:---|" or "| --- | --- | ... |"
RE_ALIGN_ROW = re.compile(r"^\s*\|[\s:\-\|]+\|?\s*$")

# API cell: "[Name](https://url)"
RE_MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")

def _to_bool(s: str) -> Optional[bool]:
    t = (s or "").strip().lower()
    if t.startswith("y") or t == "true": return True
    if t.startswith("n") or t == "false": return False
    return None

def _split_5(line: str) -> List[str]:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    while len(cells) < 5: cells.append("")
    return cells[:5]

def dedupe_items(items):
    """Remove duplicates by (api_name normalized, category). Keep first occurrence."""
    seen = set()
    out = []
    for r in items:
        key = (r["api_name"].strip().lower(), r["category"].strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def parse_all_tables(md_text: str) -> List[Dict]:
    entries: List[Dict] = []
    lines = md_text.splitlines()

    current_category = "Uncategorized"
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # track category
        mcat = RE_CATEGORY.match(line)
        if mcat:
            current_category = mcat.group(1).strip()

        # found a header?
        if RE_TABLE_HDR.match(line):
            # skip one or more alignment rows
            i += 1
            while i < n and RE_ALIGN_ROW.match(lines[i]):
                i += 1

            # consume data rows: lines that start with '|'
            while i < n:
                row = lines[i]
                if not row.lstrip().startswith("|"):  # data rows always start with '|'
                    break
                # avoid mis-detecting a header as data
                if RE_TABLE_HDR.match(row):
                    break

                api_cell, desc, auth, https, cors = _split_5(row)

                # name + url
                m = RE_MD_LINK.search(api_cell)
                if m:
                    api_name, base_url = m.group(1).strip(), m.group(2).strip()
                else:
                    api_name, base_url = api_cell.strip(), None

                if api_name and desc:
                    # normalize auth (strip backticks and map no/none → "None")
                    auth_clean = (auth or "").strip().strip("`")
                    if auth_clean.lower() in {"", "no", "none"}:
                        auth_clean = "None"

                    entries.append({
                        "api_name": api_name,
                        "base_url": base_url,
                        "description": desc.strip(),
                        "auth_type": auth_clean,
                        "https_supported": _to_bool(https),
                        "cors_supported": _to_bool(cors),
                        "category": current_category,
                        "pricing_tier": "Free",
                    })
                i += 1
            continue  # don’t double-increment after table block
        i += 1

    return entries

# ------------- Upsert ---------------
UPSERT_API_SQL = """
INSERT INTO api_catalog.api
(api_name, description, base_url, auth_type, https_supported, cors_supported, pricing_tier, category_id)
VALUES %s
ON CONFLICT (api_name, category_id) DO UPDATE
SET description = EXCLUDED.description,
    base_url = EXCLUDED.base_url,
    auth_type = EXCLUDED.auth_type,
    https_supported = EXCLUDED.https_supported,
    cors_supported = EXCLUDED.cors_supported,
    pricing_tier = EXCLUDED.pricing_tier;
"""

def upsert_categories_get_ids(cur, names: List[str]) -> Dict[str, int]:
    # upsert categories, then fetch ids
    uniq = sorted(set(names))
    for name in uniq:
        cur.execute(
            "INSERT INTO api_catalog.category (category_name) VALUES (%s) ON CONFLICT (category_name) DO NOTHING",
            (name,),
        )
    cur.execute(
        "SELECT category_id, category_name FROM api_catalog.category WHERE category_name = ANY(%s)",
        (uniq,),
    )
    return {name: cid for cid, name in cur.fetchall()}

def batch_upsert(cur, items: List[Dict], chunk_size: int = 500):
    # 1) dedupe rows by (api_name, category) to avoid ON CONFLICT twice in same statement
    items = dedupe_items(items)

    # 2) upsert categories and map to IDs
    cat_ids = upsert_categories_get_ids(cur, [r["category"] for r in items])

    # 3) build values list
    values = [
        (
            r["api_name"],
            r["description"],
            r["base_url"],
            r["auth_type"],
            r["https_supported"],
            r["cors_supported"],
            r["pricing_tier"],
            cat_ids[r["category"]],
        )
        for r in items
    ]

    # 4) insert in chunks
    for i in range(0, len(values), chunk_size):
        execute_values(cur, UPSERT_API_SQL, values[i:i+chunk_size])

# --------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", default="ingestion/public_apis_README.md",
                    help="Path to saved README.md from public-apis")
    args = ap.parse_args()

    if not os.path.exists(args.readme):
        print(f"[ingest] README not found at: {args.readme}")
        return

    with open(args.readme, "r", encoding="utf-8") as f:
        md = f.read()

    items = parse_all_tables(md)
    print(f"[ingest] parsed {len(items)} entries from README tables")

    with connect() as conn, conn.cursor() as cur:
        batch_upsert(cur, items)
        conn.commit()
        print(f"[ingest] Ingested {len(items)} records.")

if __name__ == "__main__":
    main()
