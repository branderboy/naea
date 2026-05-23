"""Bulk pipeline runner. Use this for the 60K-record run instead of the
LLM-driven subagents (which are fine for ad-hoc lookups but too expensive
in tokens for bulk).

Usage:
    python scripts/run_pipeline.py ingest
    python scripts/run_pipeline.py enrich
    python scripts/run_pipeline.py guess
    python scripts/run_pipeline.py verify
    python scripts/run_pipeline.py linkedin
    python scripts/run_pipeline.py export
    python scripts/run_pipeline.py all   # runs everything in order
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from lib.common import email_patterns, http_get, http_post, normalize_domain  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv(HERE / ".env")
except ImportError:
    pass

INPUT_CSV = os.environ.get("INPUT_CSV", "data/irs_enrolled_agents.csv")
OUTPUT_CSV = os.environ.get("OUTPUT_CSV", "data/enrolled_agents_enriched.csv")
STATE_DB = os.environ.get("STATE_DB", "data/pipeline.sqlite")
MAX_PARALLEL = int(os.environ.get("MAX_PARALLEL", "8"))
BUDGET_USD = float(os.environ.get("BUDGET_USD", "1000"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
  ptin TEXT PRIMARY KEY,
  first_name TEXT, last_name TEXT, credential TEXT,
  city TEXT, state TEXT, zip TEXT,
  firm_name TEXT, firm_domain TEXT,
  email TEXT, email_confidence TEXT,
  linkedin_url TEXT, linkedin_confidence TEXT,
  source TEXT, status TEXT DEFAULT 'pending',
  enriched_at TEXT, notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_status ON agents(status);
CREATE TABLE IF NOT EXISTS spend (
  vendor TEXT, calls INTEGER DEFAULT 0, usd REAL DEFAULT 0
);
"""


def db() -> sqlite3.Connection:
    Path(STATE_DB).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(STATE_DB)
    conn.executescript(SCHEMA)
    conn.row_factory = sqlite3.Row
    return conn


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def track_spend(conn: sqlite3.Connection, vendor: str, usd: float) -> None:
    conn.execute("INSERT OR IGNORE INTO spend (vendor) VALUES (?)", (vendor,))
    conn.execute("UPDATE spend SET calls = calls + 1, usd = usd + ? WHERE vendor = ?", (usd, vendor))
    conn.commit()


def total_spend(conn: sqlite3.Connection) -> float:
    r = conn.execute("SELECT COALESCE(SUM(usd), 0) FROM spend").fetchone()
    return float(r[0])


# ---------- Stage 1: ingest ----------

def ingest():
    if not Path(INPUT_CSV).exists():
        print(f"Missing input CSV at {INPUT_CSV}")
        sys.exit(1)
    conn = db()
    inserted = skipped = 0
    with open(INPUT_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        keymap = {k.lower().replace(" ", "_"): k for k in reader.fieldnames or []}

        def g(row, k):
            return (row.get(keymap.get(k, k)) or "").strip()

        for row in reader:
            ptin = g(row, "ptin").upper()
            if not ptin:
                continue
            try:
                conn.execute(
                    "INSERT INTO agents (ptin, first_name, last_name, credential, city, state, zip) VALUES (?,?,?,?,?,?,?)",
                    (
                        ptin,
                        g(row, "first_name").title(),
                        g(row, "last_name").title(),
                        g(row, "credential") or "EA",
                        g(row, "city").title(),
                        g(row, "state").upper(),
                        g(row, "zip"),
                    ),
                )
                inserted += 1
            except sqlite3.IntegrityError:
                skipped += 1
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0]
    print(f"ingest: inserted={inserted} skipped={skipped} total_in_db={total}")


# ---------- Stage 2: enrich (Outscraper + optional Apollo) ----------

OUTSCRAPER_BASE = "https://api.app.outscraper.com"


def outscraper_find_business(name: str, city: str, state: str) -> dict:
    key = os.environ.get("OUTSCRAPER_API_KEY")
    if not key:
        return {"found": False, "skipped": True}
    q = f"{name} {city} {state}".strip()
    try:
        data = http_get(
            f"{OUTSCRAPER_BASE}/maps/search-v2",
            params={"query": q, "limit": 1, "async": "false"},
            headers={"X-API-KEY": key},
        )
    except Exception as e:
        return {"found": False, "error": str(e)}
    items = (data.get("data") or [[]])[0] if data.get("data") else []
    if not items:
        return {"found": False}
    b = items[0]
    site = b.get("site") or ""
    return {
        "found": True,
        "name": b.get("name"),
        "domain": normalize_domain(site) if site else None,
        "phone": b.get("phone"),
    }


def outscraper_find_emails(domain: str) -> dict:
    key = os.environ.get("OUTSCRAPER_API_KEY")
    if not key or not domain:
        return {"found": False}
    try:
        data = http_get(
            f"{OUTSCRAPER_BASE}/emails-and-contacts",
            params={"query": domain, "async": "false"},
            headers={"X-API-KEY": key},
        )
    except Exception as e:
        return {"found": False, "error": str(e)}
    items = data.get("data") or []
    if not items:
        return {"found": False, "emails": []}
    row = items[0]
    return {"found": bool(row.get("emails")), "emails": row.get("emails") or []}


def outscraper_find_linkedin(first: str, last: str, city: str, state: str) -> dict:
    key = os.environ.get("OUTSCRAPER_API_KEY")
    if not key:
        return {"found": False}
    q = f'site:linkedin.com/in "{first} {last}" "{city}" enrolled agent tax'
    try:
        data = http_get(
            f"{OUTSCRAPER_BASE}/google-search-v2",
            params={"query": q, "limit": 5, "async": "false"},
            headers={"X-API-KEY": key},
        )
    except Exception as e:
        return {"found": False, "error": str(e)}
    results = (data.get("data") or [[]])[0] if data.get("data") else []
    for r in results:
        link = r.get("link", "")
        if "linkedin.com/in/" in link:
            return {
                "found": True,
                "url": link,
                "title": r.get("title") or "",
                "snippet": r.get("description") or r.get("snippet") or "",
            }
    return {"found": False}


def enrich_one(row: dict) -> dict:
    """Outscraper-only path. Apollo optional and called separately if needed."""
    name_q = f"{row['first_name']} {row['last_name']} EA tax"
    biz = outscraper_find_business(name_q, row["city"], row["state"])
    update = {"status": "no_firm"}
    if biz.get("found") and biz.get("domain"):
        update["firm_name"] = biz.get("name")
        update["firm_domain"] = biz["domain"]
        update["status"] = "firm_resolved"
        update["source"] = "outscraper"
        # Try domain email pull
        emails = outscraper_find_emails(biz["domain"])
        if emails.get("found"):
            # Prefer email that contains the last name
            ln = row["last_name"].lower()
            best = next((e for e in emails["emails"] if ln in e.lower()), emails["emails"][0])
            update["email"] = best
            update["email_confidence"] = "valid"
            update["status"] = "enriched"
    return update


def enrich():
    conn = db()
    pending = conn.execute("SELECT * FROM agents WHERE status='pending' LIMIT 100000").fetchall()
    print(f"enrich: {len(pending)} pending rows")
    cost_per_call = 0.013  # business + emails average
    done = 0
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        futures = {pool.submit(enrich_one, dict(r)): dict(r) for r in pending}
        for fut in as_completed(futures):
            r = futures[fut]
            try:
                up = fut.result()
            except Exception as e:
                up = {"status": "error", "notes": str(e)[:200]}
            sets, vals = [], []
            for k, v in up.items():
                sets.append(f"{k}=?")
                vals.append(v)
            sets.append("enriched_at=?")
            vals.append(now())
            vals.append(r["ptin"])
            conn.execute(f"UPDATE agents SET {', '.join(sets)} WHERE ptin=?", vals)
            track_spend(conn, "outscraper", cost_per_call)
            done += 1
            if done % 100 == 0:
                spent = total_spend(conn)
                print(f"  {done}/{len(pending)}  spend=${spent:.2f}")
                if spent > BUDGET_USD:
                    print("BUDGET EXCEEDED — stopping. Re-run after topping up.")
                    return
    conn.commit()
    print("enrich: done")


# ---------- Stage 3: pattern guesser ----------

NB_BASE = "https://api.neverbounce.com/v4"


def nb_verify(email: str) -> dict:
    key = os.environ.get("NEVERBOUNCE_API_KEY")
    if not key:
        return {"result": "skipped"}
    try:
        data = http_get(
            f"{NB_BASE}/single/check",
            params={"key": key, "email": email, "address_info": 1},
        )
    except Exception as e:
        return {"result": "error", "error": str(e)}
    return data


def guess_one(row: dict, max_checks: int = 4) -> dict:
    cands = email_patterns(row["first_name"], row["last_name"], row["firm_domain"])[:max_checks]
    for c in cands:
        v = nb_verify(c)
        if v.get("result") == "valid":
            return {"email": c, "email_confidence": "pattern-guess", "source": "pattern", "status": "enriched"}
        if v.get("result") == "catchall":
            return {"email_confidence": "catch-all", "status": "catchall", "notes": "Domain accepts all"}
    return {"status": "no_email"}


def guess():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM agents WHERE status='firm_resolved' AND email IS NULL"
    ).fetchall()
    print(f"guess: {len(rows)} candidates")
    cost = 0.004
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        futures = {pool.submit(guess_one, dict(r)): dict(r) for r in rows}
        for fut in as_completed(futures):
            r = futures[fut]
            up = fut.result()
            sets, vals = [], []
            for k, v in up.items():
                sets.append(f"{k}=?"); vals.append(v)
            vals.append(r["ptin"])
            conn.execute(f"UPDATE agents SET {', '.join(sets)} WHERE ptin=?", vals)
            track_spend(conn, "neverbounce", cost * 4)
    conn.commit()
    print("guess: done")


# ---------- Stage 4: verify any non-pattern emails ----------

def verify_emails():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM agents WHERE email IS NOT NULL AND email_confidence IS NULL"
    ).fetchall()
    print(f"verify: {len(rows)} emails to check")
    cost = 0.004
    for r in rows:
        v = nb_verify(r["email"])
        if v.get("result") == "valid":
            conn.execute("UPDATE agents SET email_confidence='valid', status='verified' WHERE ptin=?", (r["ptin"],))
        elif v.get("result") == "catchall":
            conn.execute("UPDATE agents SET email_confidence='catch-all' WHERE ptin=?", (r["ptin"],))
        else:
            conn.execute("UPDATE agents SET email=NULL, email_confidence=NULL, status='no_email' WHERE ptin=?", (r["ptin"],))
        track_spend(conn, "neverbounce", cost)
    conn.commit()
    print("verify: done")


# ---------- Stage 5: LinkedIn matcher ----------

def confidence_for(title: str, snippet: str, first: str, last: str, city: str, state: str) -> str | None:
    blob = f"{title} {snippet}".lower()
    name_hit = first.lower() in blob and last.lower() in blob
    if not name_hit:
        return None
    tax_hit = any(k in blob for k in ["enrolled agent", "ea ", "tax", "irs", "cpa"])
    if city.lower() in blob and tax_hit:
        return "high"
    if state.lower() in blob or city.lower() in blob:
        return "medium"
    return "low"


def linkedin_one(row: dict) -> dict:
    r = outscraper_find_linkedin(row["first_name"], row["last_name"], row["city"], row["state"])
    if not r.get("found"):
        return {}
    conf = confidence_for(r.get("title", ""), r.get("snippet", ""),
                          row["first_name"], row["last_name"], row["city"], row["state"])
    if not conf:
        return {}
    update = {"linkedin_url": r["url"], "linkedin_confidence": conf}
    return update


def linkedin():
    conn = db()
    rows = conn.execute(
        "SELECT * FROM agents WHERE linkedin_url IS NULL AND status IN ('no_email','no_firm','catchall','verified','enriched')"
    ).fetchall()
    print(f"linkedin: {len(rows)} to search")
    cost = 0.005
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        futures = {pool.submit(linkedin_one, dict(r)): dict(r) for r in rows}
        for fut in as_completed(futures):
            r = futures[fut]
            up = fut.result()
            if up:
                conn.execute(
                    "UPDATE agents SET linkedin_url=?, linkedin_confidence=? WHERE ptin=?",
                    (up["linkedin_url"], up["linkedin_confidence"], r["ptin"]),
                )
            track_spend(conn, "outscraper", cost)
    conn.commit()
    print("linkedin: done")


# ---------- Stage 6: export ----------

def export():
    conn = db()
    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)

    def segment(row) -> str:
        if row["email"] and row["email_confidence"] == "valid":
            return "email_direct"
        if row["email_confidence"] == "catch-all":
            return "email_catchall"
        if row["linkedin_url"] and row["linkedin_confidence"] in ("high", "medium"):
            return "linkedin_only"
        return "unverified"

    cols = ["ptin", "first_name", "last_name", "credential", "city", "state", "zip",
            "firm_name", "firm_domain", "email", "email_confidence",
            "linkedin_url", "linkedin_confidence", "segment", "source", "enriched_at"]
    rows = conn.execute("SELECT * FROM agents").fetchall()
    counts = {"email_direct": 0, "email_catchall": 0, "linkedin_only": 0, "unverified": 0}
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            seg = segment(r)
            counts[seg] += 1
            w.writerow([r["ptin"], r["first_name"], r["last_name"], r["credential"], r["city"], r["state"], r["zip"],
                        r["firm_name"], r["firm_domain"], r["email"], r["email_confidence"],
                        r["linkedin_url"], r["linkedin_confidence"], seg, r["source"], r["enriched_at"]])
    total = len(rows)
    spend = total_spend(conn)
    summary_lines = [
        f"# Run summary ({now()})", "",
        f"- Total: {total}",
        *(f"- {k}: {v} ({v/total*100:.1f}%)" for k, v in counts.items()),
        f"- API spend: ${spend:.2f}",
    ]
    Path("data/run_summary.md").write_text("\n".join(summary_lines))
    print(f"export: {OUTPUT_CSV}  total={total}  spend=${spend:.2f}")
    for k, v in counts.items():
        print(f"  {k}: {v}")


# ---------- entry ----------

STAGES = {"ingest": ingest, "enrich": enrich, "guess": guess,
          "verify": verify_emails, "linkedin": linkedin, "export": export}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("stage", choices=list(STAGES.keys()) + ["all"])
    args = p.parse_args()
    if args.stage == "all":
        for s in ["ingest", "enrich", "guess", "verify", "linkedin", "export"]:
            print(f"\n=== {s} ===")
            STAGES[s]()
    else:
        STAGES[args.stage]()


if __name__ == "__main__":
    main()
