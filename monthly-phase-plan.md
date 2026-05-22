# Monthly Enrichment Phase Plan + Cost Per Phase

How to spread enrichment across monthly cohorts of 5,000 agents — and exactly what each phase costs NAEA.

## Why phase it

- **Cash flow** — $90/month in data is much easier than $1,200 upfront
- **Campaign cadence** — each batch gets 4 weeks of dedicated outreach before the next drops
- **Quality feedback** — first batch teaches you which messaging works; later batches are smarter
- **Vendor stability** — 5K through Outscraper monthly is gentler than 65K in one push
- **Tier alignment** — every tier paces at 5K/month; tier just determines how many months total

## Cost per 5K phase (data only, no labor)

This is what you pay vendors per cohort, billed at-cost on NAEA's monthly invoice.

| Vendor line | Per 5K cohort |
|---|---|
| Outscraper — Google Maps firm lookup (3K × $0.003) | $9 |
| Outscraper — LinkedIn search (5K × $0.005) | $25 |
| Outscraper — Email scraper (3K domains × $0.013) | $39 |
| NeverBounce — bulk verify (~4K × $0.004) | $16 |
| Retry buffer (~10%) | $10 |
| **Per-phase data cost** | **~$99** |

Round to **$100/phase** for client conversation. Real spend tracked in `data/pipeline.sqlite` `spend` table.

---

## Per-tier monthly cost (what NAEA pays each month)

### Tier 1 — Starter (5K total, 1 phase)

| | Setup | Month 1 | Month 2 | Month 3 | **Q1 total** |
|---|---|---|---|---|---|
| Setup fee | $2,000 | — | — | — | $2,000 |
| Retainer | — | $1,250 | $1,250 | $1,250 | $3,750 |
| Data (1 cohort × $90) | — | $90 | — | — | $90 |
| **Monthly total** | $2,000 | **$1,340** | **$1,250** | **$1,250** | **$5,840** |

After Q1: $1,250/mo retainer only. No more enrichment.

### Tier 2 — Foundation (10K, 2 phases)

| | Setup | Month 1 | Month 2 | Month 3 | **Q1 total** |
|---|---|---|---|---|---|
| Setup fee | $2,500 | — | — | — | $2,500 |
| Retainer | — | $1,450 | $1,450 | $1,450 | $4,350 |
| Data (2 cohorts × $90) | — | $90 | $90 | — | $180 |
| **Monthly total** | $2,500 | **$1,540** | **$1,540** | **$1,450** | **$7,030** |

After Q1: $1,450/mo retainer only.

### Tier 3 — Growth (25K, 5 phases over 5 months)

| | Setup | M1 | M2 | M3 | M4 | M5 | **Total** |
|---|---|---|---|---|---|---|---|
| Setup fee | $3,500 | — | — | — | — | — | $3,500 |
| Retainer | — | $1,750 | $1,750 | $1,750 | $1,750 | $1,750 | $8,750 |
| Data (5 cohorts × $90) | — | $90 | $90 | $90 | $90 | $90 | $450 |
| **Monthly total** | $3,500 | **$1,840** | **$1,840** | **$1,840** | **$1,840** | **$1,840** | **$12,700** |

Q1 total: $3,500 + 3×$1,750 + 3×$90 = **$9,020** (data covers only first 3 months of enrichment in Q1; remaining 2 months land in early Q2).

After enrichment complete (month 6+): $1,750/mo retainer only.

### Tier 4 — Scale (40K, 8 phases over 8 months)

| | Setup | M1–8 each | M9+ |
|---|---|---|---|
| Setup fee | $5,000 | — | — |
| Retainer | — | $2,250/mo | $2,250/mo |
| Data (8 × $90 = $720 total) | — | $90/mo for 8 mo | $0 |
| **Monthly total during enrichment** | $5,000 (one-time) | **$2,340/mo** | $2,250/mo |

Q1 total: $5,000 + 3×$2,250 + 3×$90 = **$12,020** (rounded earlier to $12,475 to include misc buffer).

Months 4–8: $2,340/mo each = $11,700.
Months 9–12: $2,250/mo each = $9,000.
**Year 1 total: ~$32,720.**

### Tier 5 — Enterprise (65K, 13 phases over 13 months)

| | Setup | M1–13 each | M14+ |
|---|---|---|---|
| Setup fee | $7,000 | — | — |
| Retainer | — | $3,000/mo | $3,000/mo |
| Data (13 × $90 = ~$1,200 total) | — | $90/mo | $25/mo (refresh-only) |
| **Monthly total during enrichment** | $7,000 (one-time) | **$3,090/mo** | $3,025/mo |

Q1 total: $7,000 + 3×$3,000 + 3×$90 = **$16,270** (rounded earlier to $17,200 for setup/buffer).

After enrichment complete (year 2+): $3,000/mo retainer + ~$25/mo quarterly refresh data.

---

## State-by-state cohort schedule (Tier 5, full 65K)

| Month | Cohort | EAs | Data |
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

Tiers 1–4 use the same ordering but stop at their roster cap (e.g. Tier 3 stops after month 5 at 25K).

## What "month N" actually looks like

```
Day 1–3   Run pipeline on this month's cohort. Verify output CSV.
Day 4–7   Hand off to outreach: email list to SMTP tool, LinkedIn URLs
          to LinkedIn Campaign Manager as custom audience.
Week 2    Send sequence 1 (intro). LinkedIn ad campaign starts.
Week 3    Send sequence 2 (value drop). Adjust ad creative based on CTR.
Week 4    Send sequence 3 (offer). Pull conversion data. Brief NAEA.
Day 28-30 Decision: continue campaign on this cohort or move on.
          Next month's enrichment kicks off Day 1.
```

## Accelerated pacing (10K/month)

If NAEA has outbound capacity for 10K names/month (rare but possible), halve the timeline:

| Tier | At 10K/month | Data per month |
|---|---|---|
| 2 — Foundation (10K) | 1 month | $180 |
| 3 — Growth (25K) | 3 months | $180/mo × 2 + $90 |
| 4 — Scale (40K) | 4 months | $180/mo × 4 |
| 5 — Enterprise (65K) | 7 months | $180/mo × 6 + ~$90 |

Caveat: enriched-but-uncampaigned leads sitting in the database are wasted spend. Only accelerate if outreach capacity matches.

## What happens if NAEA pauses mid-program

Each month is a clean stopping point. SQLite remembers what's done. If NAEA pauses after month 5, you've delivered 25K enriched agents (a full Tier 3 in itself) and the engine is paused, not broken. Resume in any later month — no re-payment for work already complete.

## Sample monthly invoice (Tier 3, month 2)

```
NAEA — Engagement Invoice
Period: [Month] [Year]

  Retainer (podcast SEO + content engine +
    outreach + briefs + dashboard maintenance)         $1,750.00
  Data acquisition — Outscraper + NeverBounce, at-cost $   90.00
                                                  Total $1,840.00

Payment due: [Date]
```

Predictable for them, transparent for you. Data line moves with each cohort's actual usage.

## Anti-patterns to avoid

- **Don't run all 65K in one weekend.** You'll burn $1,200 in data and have stale leads sitting unused for 11 months.
- **Don't skip the smallest states.** Tail states (Wyoming, Vermont) have surprisingly high member-engagement rates per agent — they're not noise.
- **Don't re-enrich an existing cohort.** Only re-run for *new* PTINs added to the FOIA roster. The SQLite `INSERT OR IGNORE` handles this automatically.
- **Don't quote NAEA a fixed "data line" if their roster grows.** Always show "at-cost" so it can flex up or down with reality.
