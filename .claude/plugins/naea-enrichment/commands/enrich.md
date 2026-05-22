---
description: Run the full NAEA enrichment pipeline end-to-end on the IRS Enrolled Agent roster.
---

The actual work is done by the batch script (so it doesn't burn LLM tokens on 60K rows).

Run:

```
cd .claude/plugins/naea-enrichment && python scripts/run_pipeline.py all
```

After it finishes, surface `data/enrolled_agents_enriched.csv` and `data/run_summary.md` to the user.

If you want to run only one stage (for testing or recovery from a partial run):

```
python scripts/run_pipeline.py ingest      # load CSV → SQLite
python scripts/run_pipeline.py enrich      # Outscraper firm + email lookup
python scripts/run_pipeline.py guess       # pattern-guess remaining emails
python scripts/run_pipeline.py verify      # NeverBounce verify
python scripts/run_pipeline.py linkedin    # LinkedIn URL match
python scripts/run_pipeline.py export      # write final CSV
```

If `$BUDGET_USD` is exceeded mid-run, the script stops cleanly and reports.
The SQLite state file (`data/pipeline.sqlite`) lets you resume — just re-run
the same command and it picks up where it left off.

$ARGUMENTS
