# API Keys — exactly what to sign up for

You need **two** keys to run the lean pipeline. Everything else is optional.

## Required (lean budget ~$800–1,000)

### 1. Outscraper — covers firm lookup, email scraping, LinkedIn search

- **Sign up:** https://app.outscraper.com/signup
- **Get key:** dashboard → "Profile" → "API Token"
- **Pricing:** pay-as-you-go, no monthly minimum
  - Google Maps search: ~$0.003 per result
  - Emails & Contacts scraper: ~$0.01 per domain
  - Google Search (LinkedIn finder): ~$0.005 per query
- **Budget for 60K agents:** ~$500–700
- **Free credits:** $5 on signup (good for testing ~500 lookups)
- **Env var:** `OUTSCRAPER_API_KEY`

### 2. NeverBounce — SMTP-level email verification

- **Sign up:** https://app.neverbounce.com/signup
- **Get key:** dashboard → "Apps & Integrations" → "Custom Integration" → copy API key
- **Pricing:** pay-as-you-go credits
  - Single verifications: $0.008/check (small volumes)
  - Bulk (5K+): $0.004/check
  - 1M+ tier: $0.002/check
- **Budget for 60K agents:** ~$200–300 (most agents don't need verification — only the pattern-guesser uses it heavily)
- **Free credits:** 1,000 verifications on signup (free)
- **Env var:** `NEVERBOUNCE_API_KEY`

**Bulk-mode tip:** Once your `pending pattern-guesses` queue is more than
~5,000 emails, switch to NeverBounce's `/jobs/create` endpoint instead of
`single/check`. Cuts cost in half. (Not currently in `run_pipeline.py` —
add as an extension if volume justifies it.)

---

## Optional (if you want a higher yield or fallbacks)

### 3. Apollo.io — people-level enrichment (LinkedIn + verified emails)

- **Sign up:** https://app.apollo.io/signup
- **Get key:** Settings → Integrations → "API" → generate
- **Pricing tiers:**
  - **Free**: 50 lookups/month (basically useless for 60K, fine for testing)
  - **Basic**: $49/user/month, 1,200 credits/month
  - **Professional**: $79/user/month, 2,400 credits/month
  - **Organization**: $99/user/month, plus bulk credit packs
  - **Pay-as-you-go credit packs**: ~$0.04–$0.08 per enrichment depending on plan
- **For our use:** skip unless you want their LinkedIn matching (better
  than Outscraper Google-search for ambiguous names). If you do use it:
  one month of Professional ($79) = 2,400 enrichments. Run those on
  agents who came back as `linkedin_only` from the cheaper path to
  upgrade them with verified emails.
- **Env var:** `APOLLO_API_KEY`

### 4. Hunter.io — domain → likely email pattern

- **Sign up:** https://hunter.io/users/sign_up
- **Get key:** Dashboard → API → "Show your API key"
- **Pricing:**
  - **Free**: 25 lookups/month
  - **Starter**: $49/month, 500 lookups
  - **Growth**: $149/month, 5,000 lookups
- **For our use:** Hunter's `email-finder` endpoint (name+domain → email)
  is more accurate than pattern-guessing in many cases. One month of
  Growth ($149) easily covers the firm-resolved subset.
- **When to use:** as a substitute for the NeverBounce pattern-guesser
  if you want higher accuracy and don't mind the monthly fee.
- **Env var:** `HUNTER_API_KEY`

### 5. Snov.io — fallback email finder

- **Sign up:** https://app.snov.io/register
- **Get keys:** Settings → API → generate Client ID + Client Secret
- **Pricing:**
  - **Free**: 50 credits/month, 1,000 recipients
  - **Starter**: $39/month, 1,000 credits
  - **Pro 5K**: $99/month, 5,000 credits
- **For our use:** skip unless Outscraper + Hunter both fall short.
- **Env vars:** `SNOV_CLIENT_ID`, `SNOV_CLIENT_SECRET`

### 6. Clearbit — enterprise enrichment (most expensive, last resort)

- **Sign up:** https://clearbit.com (now owned by HubSpot — pricing is sales-led)
- **Pricing:** quote-based, typically $99/month minimum, $0.20–$1 per
  enrichment depending on tier.
- **For our use:** skip on lean budget. Worth it only if you'll keep
  enriching ongoing (HubSpot integration nice-to-have).
- **Env var:** `CLEARBIT_API_KEY`

---

## Recommended starter pack

If you want to spend the minimum and prove it works:

| Service | Plan | Cost | Why |
|---|---|---|---|
| Outscraper | pay-as-you-go | ~$5 deposit for testing | Required |
| NeverBounce | free 1K + pay-as-you-go | $0 for testing | Required |
| **Total** | | **$5** | Run on 500-row sample |

Once the sample looks good, top up:

| Service | Plan | Cost | Volume |
|---|---|---|---|
| Outscraper | pay-as-you-go | ~$600 | 60K agents full pipeline |
| NeverBounce | pay-as-you-go | ~$250 | Verification of pattern guesses + non-pattern emails |
| **Total** | | **~$850** | Full 60K enrichment |

If yield disappoints (< 20% direct emails), add:

| Service | Plan | Cost | Adds |
|---|---|---|---|
| Hunter.io | Growth 1 month | $149 | ~5K additional direct emails |
| Apollo | Professional 1 month | $79 | ~2,400 LinkedIn-verified-email upgrades |

That ceiling: **~$1,080** for the absolute maximum-yield pass at 60K.

---

## Signup order (do this in sequence)

1. **Outscraper first.** $5 deposit, get the API token, paste into `.env`.
2. **Test:** run `python scripts/run_pipeline.py ingest enrich` on a 500-row sample. Confirm you see firm domains coming back.
3. **NeverBounce next.** Sign up free, paste API key, run `python scripts/run_pipeline.py guess` on the sample.
4. **Spot-check 20 emails by hand** — do they look real? Send a test email to one of them to confirm SMTP works.
5. **Top up Outscraper to $700.** Run the full enrichment.
6. **Top up NeverBounce to $300.** Run verify + guess at full volume.
7. **Decide on Hunter/Apollo only if yield is below target.**

---

## Where to charge it back to NAEA

In your invoice, list these as pass-through data costs (per `pricing-model.md`):

```
Data acquisition — IRS Enrolled Agent enrichment
  Outscraper API usage             $   [actual]
  NeverBounce verification         $   [actual]
  [Hunter.io / Apollo if used]     $   [actual]
                          Subtotal $   [actual, at-cost]
```

Keep receipts. Most clients want screenshots of the dashboard usage page.
