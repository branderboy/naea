# Monthly Enrichment Phase Plan

How to spread the 65K roster across months so data cost is monthly, not lump-sum, and each batch can be fully campaigned before the next one lands.

## Why phase it

- **Cash flow** — $90/month is much easier than $1,200 upfront
- **Campaign cadence** — each batch gets 4 weeks of dedicated outreach before the next one drops in
- **Quality feedback** — first batch teaches you which messaging works; later batches are smarter
- **Vendor stability** — running 5K through Outscraper monthly is gentler than 65K in one push
- **Tier alignment** — Tier 1 buys 5K total; Tier 2 buys 15K over 3 months; Tier 3 buys 40K over 8 months; Tier 4 buys 65K over 13 months

## Phase recommendation by tier

| Tier | Total agents | Cadence | Months |
|---|---|---|---|
| 1 — Starter | 5,000 | One batch | 1 month |
| 2 — Growth | 15,000 | 5K/month | 3 months |
| 3 — Scale | 40,000 | 5K/month | 8 months |
| 4 — Enterprise | 65,000 | 5K/month | 13 months |

A higher cadence (10K/month) is possible — halves the timeline. But 5K is the sweet spot for outbound team capacity (one person can run a tight email + LinkedIn campaign on ~5K names per month).

## Monthly cohort plan (full 65K roster, 13 months)

State picks ordered by EA density × campaign value. First six months hit the heaviest states with the highest concentration of practice owners — those are your highest LTV prospects.

| Month | Cohort | Approx EAs | Data cost (LinkedIn-first hybrid) |
|---|---|---|---|
| 1 | California (Bay Area + LA metro) | 5,000 | ~$92 |
| 2 | California (remainder) | 5,000 | ~$92 |
| 3 | New York | 5,500 | ~$100 |
| 4 | Texas | 5,000 | ~$92 |
| 5 | Florida | 4,500 | ~$83 |
| 6 | Illinois + Pennsylvania | 5,700 | ~$105 |
| 7 | New Jersey + Ohio | 4,200 | ~$77 |
| 8 | Georgia + Washington + Virginia | 5,300 | ~$98 |
| 9 | Massachusetts + Arizona + Colorado | 4,200 | ~$77 |
| 10 | Maryland + North Carolina + Michigan | 3,800 | ~$70 |
| 11 | Tennessee + 5 mid-tier states | 5,000 | ~$92 |
| 12 | 12 small-population states | 5,000 | ~$92 |
| 13 | Final 23 small states + cleanup | 6,800 | ~$125 |
| | **Totals** | **65,000** | **~$1,195** |

## What "month N" actually looks like

```
Day 1–3   Run /enrich on this month's cohort. Verify output CSV.
Day 4–7   Hand off to outreach: email list goes into the SMTP tool,
          LinkedIn URLs become a custom audience.
Week 2    Send sequence 1 (intro). LinkedIn ad campaign starts.
Week 3    Send sequence 2 (value drop). Adjust ad creative.
Week 4    Send sequence 3 (offer). Pull conversion data. Brief.
Day 28-30 Decision: continue campaign on this cohort or move on. Next
          month's enrichment kicks off Day 1.
```

## What happens if NAEA wants 10K/month instead

Same structure, half the months. Doable if there's outreach capacity for 10K names/month. Otherwise you'll have enriched-but-uncampaigned leads sitting in the database, which is wasted spend.

| Tier | At 10K/month |
|---|---|
| 2 — Growth (15K) | 1.5 months |
| 3 — Scale (40K) | 4 months |
| 4 — Enterprise (65K) | 6.5 months |

## What happens if budget gets cut mid-program

Each month is a clean stopping point. SQLite remembers what's done. If NAEA pauses after month 5, you've delivered 25K enriched agents (a full Tier 3 in itself) and the engine is paused, not broken. Resume in any later month by re-running `/enrich`.

## How this maps to invoices

If on **Tier 3 Scale ($2,250/mo retainer)**, each monthly invoice shows:

```
NAEA — [Month] [Year]
  Retainer (podcast SEO + content engine + outreach + briefs)  $2,250.00
  Data acquisition (Outscraper + NeverBounce, at-cost)         $   92.00
                                                          Total $2,342.00
```

Predictable for them, transparent for you. Data line goes up or down with each cohort's actual usage — no surprises.

## Anti-patterns to avoid

- **Don't run all 65K in one weekend.** You'll burn $1,200 in data and then have stale leads sitting unused for 11 months.
- **Don't skip the smallest states.** Tail states (Wyoming, Vermont) have surprisingly high member-engagement rates per agent — they're not noise.
- **Don't re-enrich an existing cohort just for refresh.** Only re-run for *new* PTINs added to the FOIA roster. The SQLite `INSERT OR IGNORE` handles this automatically.
