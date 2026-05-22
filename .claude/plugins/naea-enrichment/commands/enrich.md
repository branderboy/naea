---
description: Run the full NAEA enrichment pipeline end-to-end on the IRS Enrolled Agent roster.
---

Run the NAEA enrichment pipeline. Execute these workers in sequence, halting if any reports a failure:

1. Invoke the `ingest` subagent to load `data/irs_enrolled_agents.csv` into the SQLite store.
2. Invoke the `enricher` subagent to run the Outscraper → Apollo waterfall.
3. Invoke the `pattern-guesser` subagent for agents with resolved firm domains.
4. Invoke the `verifier` subagent to confirm all non-pattern emails are deliverable.
5. Invoke the `linkedin-matcher` subagent to fill in LinkedIn URLs.
6. Invoke the `csv-builder` subagent to write the final deliverable CSV + summary.

After each step, print the worker's summary. After the full run, surface `data/enrolled_agents_enriched.csv` and `data/run_summary.md` to the user.

If `$BUDGET_USD` is exceeded at any step, stop, write a partial CSV, and ask the user whether to top up and continue.

$ARGUMENTS
