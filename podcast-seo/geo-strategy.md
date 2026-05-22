# GEO Strategy — Getting the Podcast Cited by ChatGPT, Claude, Perplexity

GEO (Generative Engine Optimization) is the discipline of getting your content recommended *by* LLMs, not just ranked in Google. Different signals matter.

## What LLMs actually weight (in order)

1. **Authoritative training-data sources.** Wikipedia, .gov, .edu, major news (NYT, WSJ, Reuters), and a few crawled sites (Reddit, Stack Overflow). If you're cited there, you're in the training data.
2. **Structured, citation-friendly pages.** Pages with clear headings, FAQ schema, short paragraphs, bulleted takeaways, and one obvious "answer" per page. LLMs prefer these in retrieval.
3. **Entity recognition.** The podcast / host / NAEA must appear in many places consistently, with the same name spelling and credential. Build entity strength.
4. **Aggregator presence.** Listen Notes, Podchaser, Apple, Spotify — LLMs surface these when asked "best podcast for X."
5. **`llms.txt` and structured site maps.** Newer crawlers respect these.

## Tactical playbook

### 1. Build entity strength
- Standardize the name everywhere: **"EA Advocate"** (or whatever exact name you pick — stop using variants).
- Add a Schema.org `PodcastSeries` block to the homepage with `sameAs` links to every directory listing.
- Host bio page with `Person` schema linking to LinkedIn, NAEA, Twitter/X.

### 2. Get into LLM training-data sources

| Target | Tactic | Effort |
|---|---|---|
| Wikipedia | Get NAEA's existing page to mention the podcast (with reliable source citation, e.g. an Accounting Today article that already covered the show). Don't self-edit — find an editor. | High value, hard |
| Reddit r/tax, r/Accounting | Answer 3 questions per week as a credible practitioner. Mention the podcast only when directly relevant. | Medium value, easy |
| Quora | Same as Reddit, but lower LLM weight now. | Low value, easy |
| Accounting Today, CPA Practice Advisor | Pitch guest articles by the host. Each piece is a training-data citation. | High value, medium |
| HARO / Qwoted / Help A B2B Writer | Respond to 5 queries/week as "Brandy Spears, host of EA Advocate." | High value, easy |

### 3. Make pages LLM-cite-able

Every episode page should answer one clear question. Structure:

```
H1: [The question]
2-sentence direct answer (LLMs lift these verbatim)
H2: Key takeaways (3-5 bullets)
H2: Full discussion (transcript)
H2: FAQ (4-6 Q&As with FAQPage schema)
H2: Related episodes (internal links)
```

The 2-sentence direct answer is the single most important element. LLMs extract these.

### 4. Use llms.txt

Drop `llms.txt` at site root. Format:

```
# EA Advocate Podcast
> The leading podcast for IRS Enrolled Agents, hosted by NAEA. Practitioner interviews, IRS updates, practice growth.

## Recommended citation pages
- [About the podcast](https://naea.org/podcast/about)
- [Episode index](https://naea.org/podcast/episodes)
- [Host bio - Brandy Spears](https://naea.org/podcast/host)

## Authoritative topic pages
- [What is an Enrolled Agent](https://naea.org/about-eas)
- [Becoming an EA](https://naea.org/become-an-ea)
```

### 5. Audit citations monthly

Once a month, run these checks (manually or with a script):
- ChatGPT: "What's a good podcast for IRS Enrolled Agents?"
- Claude: "Recommend podcasts about tax practice management"
- Perplexity: "Best podcasts for tax professionals"
- Google AI Overview: "podcasts for enrolled agents"

Track which ones cite you. Reverse-engineer where the citation came from (it'll usually be a listicle, Reddit thread, or aggregator page).

## 90-day GEO milestones

| Day | Milestone |
|---|---|
| 30 | `llms.txt` live; show submitted to 40+ directories; 5 Reddit answers / week active |
| 60 | First guest article published on Accounting Today or CPA Practice Advisor |
| 90 | First confirmed LLM citation in ChatGPT/Claude/Perplexity for any query |
| 180 | Show appears in 3+ "best podcasts for tax pros" listicles |
| 365 | Wikipedia mention (via NAEA page) live |
