# NAEA Enrolled Agent Enrichment Plugin

Enriches the IRS Enrolled Agent FOIA roster (~66K names) with verified emails and LinkedIn URLs. Outputs a single deliverable CSV segmented for downstream campaign use.

## Pipeline

```
IRS roster CSV
   │
   ▼
ingest ─► enricher (Apollo → Outscraper → Snov → Clearbit waterfall)
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
| source | apollo / outscraper / snov / clearbit / pattern |
| enriched_at | ISO timestamp |

## Setup

1. Copy `.env.example` to `.env` and fill in API keys:
   - `APOLLO_API_KEY`
   - `OUTSCRAPER_API_KEY`
   - `SNOV_CLIENT_ID`, `SNOV_CLIENT_SECRET`
   - `CLEARBIT_API_KEY`
   - `NEVERBOUNCE_API_KEY`

2. Place the IRS roster CSV at `data/irs_enrolled_agents.csv`. FOIA-released format expected: `first_name,last_name,credential,city,state,zip,ptin`.

3. Install MCP server deps:
   ```
   pip install -r .claude/plugins/naea-enrichment/requirements.txt
   ```

4. Run the pipeline:
   ```
   /enrich
   ```

## Cost budget (60K agents, one-time)

| Layer | Estimated cost |
|---|---|
| Apollo bulk credits | $2,400–4,800 |
| Outscraper (firm + LinkedIn lookup) | $520–600 |
| Snov.io fallback | $200 |
| Clearbit fallback | $1,000 |
| NeverBounce verification | $600 |
| Buffer | $500 |
| **Total** | **$5,220–7,700** |

Realistic yield: ~30% direct emails + ~55% LinkedIn URLs = ~50K usable records.
