# How the enrichment pipeline works

You feed it the IRS Enrolled Agent roster CSV. It hands you back a CSV with
verified emails and LinkedIn URLs, segmented so you know which records to use
for cold email vs LinkedIn ads vs awareness campaigns.

## The whole flow in 30 seconds

```
1. INGEST    Read IRS CSV → SQLite (one row per agent, status='pending')
2. ENRICH    For each agent: Outscraper Google Maps → find firm + domain
                              Outscraper email scraper → domain emails
                              (Stops the moment a domain email is found)
3. GUESS     For agents with a firm domain but no email yet:
                generate first.last@, flast@, etc.
                NeverBounce SMTP-verify each until one says "valid"
4. VERIFY    For any email we got from sources other than pattern-guessing:
                run it through NeverBounce one more time
5. LINKEDIN  For everyone still missing an email (or anyone missing LinkedIn):
                Outscraper Google search for "site:linkedin.com/in/ <name>"
                Score the match (high/medium/low) using name + city + tax keywords
6. EXPORT    Read SQLite → write final CSV with segment column
                (email_direct / email_catchall / linkedin_only / unverified)
```

Each stage updates SQLite. If the run dies (network, budget, machine), you
re-run and it picks up from the last successful stage.

## Running it

### Quickest path (one command, end to end)

```bash
cd /home/user/naea/.claude/plugins/naea-enrichment

# One-time setup
pip install -r requirements.txt
cp .env.example .env       # then edit .env and paste in your API keys
mkdir -p data
# Put the IRS FOIA CSV here:
cp ~/Downloads/irs_enrolled_agents.csv data/irs_enrolled_agents.csv

# Run everything
python scripts/run_pipeline.py all
```

That writes `data/enrolled_agents_enriched.csv` and `data/run_summary.md`.

### Run stages one at a time (for testing or recovery)

```bash
python scripts/run_pipeline.py ingest      # CSV → SQLite
python scripts/run_pipeline.py enrich      # Outscraper firm+domain+emails
python scripts/run_pipeline.py guess       # Pattern-guess + NeverBounce
python scripts/run_pipeline.py verify      # NeverBounce on non-pattern emails
python scripts/run_pipeline.py linkedin    # LinkedIn URL match
python scripts/run_pipeline.py export      # Final CSV + summary
```

### Test on a small batch first (recommended)

Before spending the whole $800, run on 500 rows:

```bash
head -501 data/irs_enrolled_agents.csv > data/sample.csv
INPUT_CSV=data/sample.csv STATE_DB=data/test.sqlite OUTPUT_CSV=data/test_out.csv \
  python scripts/run_pipeline.py all
```

Check the output. Confirm the yield matches expectations. Then run on full.

## Environment variables (`.env`)

```bash
# REQUIRED for the lean pipeline
OUTSCRAPER_API_KEY=
NEVERBOUNCE_API_KEY=

# OPTIONAL — only if you want them in the loop
APOLLO_API_KEY=
HUNTER_API_KEY=
SNOV_CLIENT_ID=
SNOV_CLIENT_SECRET=
CLEARBIT_API_KEY=

# Pipeline controls (defaults shown)
INPUT_CSV=data/irs_enrolled_agents.csv
OUTPUT_CSV=data/enrolled_agents_enriched.csv
STATE_DB=data/pipeline.sqlite
MAX_PARALLEL=8
BUDGET_USD=1000
```

## Output: what the deliverable CSV looks like

| column | example | meaning |
|---|---|---|
| ptin | P00012345 | IRS practitioner ID |
| first_name | Jane | |
| last_name | Doe | |
| credential | EA | EA / CPA / Attorney / RTRP |
| city | Austin | |
| state | TX | |
| zip | 78701 | |
| firm_name | Doe Tax & Advisory | from Outscraper Google Maps |
| firm_domain | doetax.com | normalized website domain |
| email | jane@doetax.com | verified |
| email_confidence | valid | valid / catch-all / pattern-guess / null |
| linkedin_url | https://linkedin.com/in/jane-doe-ea | |
| linkedin_confidence | high | high / medium / low / null |
| **segment** | email_direct | how to use this record (see below) |
| source | outscraper | which vendor produced the data |
| enriched_at | 2026-05-22T18:43:11Z | ISO timestamp |

## The four segments

| segment | use for |
|---|---|
| `email_direct` | Cold email — these are verified deliverable |
| `email_catchall` | Awareness ads only; **do not** cold email (high bounce risk) |
| `linkedin_only` | LinkedIn ads (custom audience upload) or InMail |
| `unverified` | Hold for future. Re-run periodically as new sources appear. |

## What to expect (60K agents, full run)

| metric | low estimate | high estimate |
|---|---|---|
| email_direct | 15,000 (25%) | 21,000 (35%) |
| email_catchall | 1,800 (3%) | 3,600 (6%) |
| linkedin_only | 24,000 (40%) | 33,000 (55%) |
| unverified | 6,000 (10%) | 12,000 (20%) |
| API spend | $800 | $1,200 |
| Wall-clock time | 6 hours | 14 hours |

## Resuming after a crash / budget exhaust

Just run the same command again. SQLite tracks state per row. You won't
re-pay for work already done.

If the budget tripped:

```bash
# Top up your Outscraper / NeverBounce account, then
BUDGET_USD=2000 python scripts/run_pipeline.py enrich
```

## Re-running with a fresh roster (quarterly refresh)

When NAEA pulls a new IRS FOIA roster:

```bash
# Don't delete the old DB — the script de-dupes by PTIN.
# Just point it at the new CSV.
INPUT_CSV=data/irs_enrolled_agents_2026Q3.csv \
  python scripts/run_pipeline.py ingest

# Then re-run only stages for new rows
python scripts/run_pipeline.py enrich
python scripts/run_pipeline.py guess
python scripts/run_pipeline.py verify
python scripts/run_pipeline.py linkedin
python scripts/run_pipeline.py export
```

The new CSV will include the new rows + refreshed everything.

## Troubleshooting

**"Missing env var: OUTSCRAPER_API_KEY"** — you didn't load `.env`. Either
`export $(cat .env | xargs)` first, or use `python-dotenv` (already in
requirements; the script loads it automatically if installed).

**"404 on /maps/search-v3"** — Outscraper renamed the endpoint. Edit
`mcp-servers/outscraper/server.py` and change `v3` to `v2`. (Batch script
already uses v2.)

**"NeverBounce: insufficient credits"** — top up your account. Check current
balance: `curl 'https://api.neverbounce.com/v4/account/info?key=YOUR_KEY'`.

**Outscraper "rate limited"** — drop `MAX_PARALLEL` from 8 to 3, or use
their async API mode (extension — not implemented yet).

**Same row enriched twice** — won't happen. INSERT uses
`INSERT OR IGNORE` and updates are scoped by `status`.

**Garbage firm matches (wrong business with same name)** — increase
match strictness by adding zip-code matching to `enrich_one()`. The current
implementation trusts the first Google Maps hit.

## Files / where things live

```
.claude/plugins/naea-enrichment/
├── README.md              # High-level overview
├── HOW-IT-WORKS.md        # This file
├── API-KEYS.md            # Where to sign up for each vendor
├── AUDIT.md               # Issues fixed
├── plugin.json            # MCP server registration
├── requirements.txt       # Python deps
├── .env.example           # Copy to .env and fill in
├── scripts/
│   └── run_pipeline.py    # The actual batch pipeline (the real workhorse)
├── lib/
│   └── common.py          # Shared HTTP + pattern helpers
├── mcp-servers/           # For ad-hoc one-off lookups in Claude Code
│   ├── outscraper/
│   ├── neverbounce/
│   ├── apollo/
│   ├── snov/
│   └── clearbit/
├── agents/                # Subagent prompts (orchestrators)
└── commands/
    └── enrich.md          # /enrich slash command
```
