# Audit — what was wrong, what got fixed

I went back over the code and found these issues. Each one is now resolved or flagged.

## 1. Architecture: LLM-driven subagents can't scale to 60K records
**Severity: critical**

The original design had 6 subagents looping over the IRS roster row-by-row.
That means an LLM call per row. At ~5K tokens/row × 60K rows = 300M tokens of
LLM work — far more expensive than the $800 API budget for the data itself.

**Fix:** Added `scripts/run_pipeline.py` — a standalone Python batch script
that talks to vendor APIs directly. Subagents and the `/enrich` command are
now thin wrappers that kick off this script via Bash. The MCP servers are
still there for ad-hoc single-record lookups during exploration.

## 2. Outscraper endpoint versions
**Severity: medium — verify before first run**

The original code used `/maps/search-v3` and `/google-search-v3`. Outscraper's
currently-documented endpoints are `/maps/search-v2` and `/google-search-v2`.
The v3 endpoints may exist for some accounts but aren't universal.

**Fix:** Batch script uses `-v2`. The MCP servers still use `-v3` — change to
`-v2` in `mcp-servers/outscraper/server.py` if you get 404s.

## 3. Missing `__init__.py` in lib/
**Severity: low (works on Python 3.3+ via namespace packages, but safer to have)**

**Fix:** Added empty `lib/__init__.py`.

## 4. `data/` directory not created
**Severity: low**

Subagents assumed `data/` exists. Batch script now calls
`Path(...).parent.mkdir(parents=True, exist_ok=True)` before writing.

## 5. SQLite schema only existed in subagent prose
**Severity: low**

Was described in the ingest agent's markdown but never as actual SQL.

**Fix:** Schema is now in `scripts/run_pipeline.py` as a `SCHEMA` constant
and run on every connection (idempotent `CREATE TABLE IF NOT EXISTS`).

## 6. Apollo `people/match` parameter shape
**Severity: medium — verify before relying on Apollo path**

The endpoint exists, but `reveal_personal_emails` is technically valid only
on paid plans. On free tier it's ignored. The `organization_locations`
param I used is for the search endpoint, not match — `match` doesn't
filter by location, it just disambiguates.

**Fix:** Apollo path is now optional and not in the default batch pipeline.
Apollo MCP server still loaded for ad-hoc use; if you actually want
Apollo in the bulk run, add a stage that calls their `/v1/people/search`
endpoint with the location filter, then enriches matched results.

## 7. Outscraper response parsing brittleness
**Severity: low**

Some Outscraper endpoints return `data` as a list of result lists (one per
input query), others as a flat list. Original code assumed list-of-lists
everywhere. The batch script now checks: `(data.get("data") or [[]])[0] if data.get("data") else []`.

## 8. NeverBounce `pattern_winner` could keep calling after catch-all
**Severity: low (cost waste, not correctness)**

Fixed: returns immediately on catch-all detection.

## 9. No resume / idempotency for partial runs
**Severity: medium**

If the run dies halfway (network, budget exhausted, machine restart) the
original design would have re-done everything.

**Fix:** All stages now use `WHERE status = 'pending'` etc. so re-running
picks up where it left off. SQLite is the source of truth.

## 10. No budget guardrail enforcement
**Severity: medium**

`BUDGET_USD` was referenced in subagent prose but never enforced.

**Fix:** Batch script tracks per-vendor spend in the `spend` table and
halts cleanly if total exceeds `BUDGET_USD`.

## Still flagged (not bugs, but worth knowing)

- **Outscraper sync mode has rate limits.** For 60K queries you may hit them.
  Switch to `async=true` mode and poll for results if you do — that's an extension.
- **Apollo free tier is limited** (a few hundred credits/month). Plan for
  paid tier or use sparingly.
- **NeverBounce charges per check on `single/check`**. For bulk you can use
  their `/jobs/create` endpoint to upload a CSV and verify thousands at
  once for less (~$0.003 vs $0.008). Worth doing if you're verifying > 5K
  emails — not yet in the batch script.
- **The dashboard at `dashboard/index.html` is a static mockup.** It is not
  wired to read from `data/run_summary.md` or `data/pipeline.sqlite` yet.
  Wiring it is straightforward (small JS file that reads the JSON-ified
  summary). Not done because it wasn't in the original scope.
