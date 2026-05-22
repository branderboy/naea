# NAEA Enrolled Agent Enrichment Plugin

Enriches the IRS Enrolled Agent FOIA roster (~66K names) with verified emails and LinkedIn URLs. Outputs a single deliverable CSV segmented for downstream campaign use.

## Pipeline

```
IRS roster CSV
   │
   ▼
ingest ─► enricher (Outscraper → Apollo waterfall)
                    │
                    ├─► pattern-guesser ─► verifier (NeverBounce)
                    │
                    └─► linkedin-matcher
                              │
                              ▼
                        csv-builder ─► enrolled_agents_enriched.csv
```

## Output CSV schema

| column | description |
|---|---|
| ptin | IRS PTIN identifier |
| first_name | |
| last_name | |
| credential | EA / CPA / Attorney / RTRP |
| city | |
| state | |
| zip | |
| firm_name | from Outscraper Google Maps |
| firm_domain | resolved domain |
| email | verified email (if any) |
| email_confidence | valid / catch-all / pattern-guess / null |
| linkedin_url | resolved profile URL (if any) |
| linkedin_confidence | high / medium / low / null |
| segment | email_direct / linkedin_only / unverified |
| source | outscraper / apollo / snov / clearbit / pattern |
| enriched_at | ISO timestamp |

## Setup

1. Copy `.env.example` to `.env` and fill in API keys (minimum: `OUTSCRAPER_API_KEY`, `NEVERBOUNCE_API_KEY`).
2. Place the IRS roster CSV at `data/irs_enrolled_agents.csv`. FOIA-released format expected.
3. Install MCP server deps:
   ```
   pip install -r .claude/plugins/naea-enrichment/requirements.txt
   ```
4. Run the pipeline from Claude Code:
   ```
   /enrich
   ```

## Lean cost budget (60K agents, one-time)

| Layer | Vendor | Cost |
|---|---|---|
| LinkedIn URL finder | Outscraper | $300 |
| Google Maps firm + domain | Outscraper | $90 |
| Email finder | Outscraper / Hunter | $50–150 |
| Pattern guessing | free (local) | $0 |
| NeverBounce verification | NeverBounce bulk | $200 |
| Apollo (free tier + spot use) | Apollo | $0–100 |
| Buffer | — | $150 |
| **Total** | | **~$800–1,000** |

Realistic yield: ~25–30% direct emails + ~50–55% LinkedIn URLs = ~45K usable records out of 60K.

## Phase it (recommended if budget is tight)

Don't enrich all 66K up front. Phase 1: top 5 states (CA, NY, TX, FL, IL ≈ 25K agents) for ~$400 in API cost. Prove the campaign, then phase 2 with revenue from phase 1.

## Components

- `plugin.json` — registers the 5 MCP servers
- `mcp-servers/outscraper/` — Google Maps, LinkedIn search, email finder
- `mcp-servers/neverbounce/` — SMTP verification + pattern winner picker
- `mcp-servers/apollo/` — people enrichment (free-tier friendly)
- `mcp-servers/snov/` — fallback (optional)
- `mcp-servers/clearbit/` — last-resort (optional, expensive)
- `agents/` — 6 subagents that run the pipeline stages
- `commands/enrich.md` — `/enrich` slash command
- `lib/common.py` — shared HTTP + pattern helpers
