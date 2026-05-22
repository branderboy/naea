# Podcast SEO Checklist — EA Advocate

## Per-episode (do this every episode, no exceptions)

- [ ] Title in `[Pain Point] + [Audience]` format. Avoid clever titles. Examples:
  - "How Enrolled Agents Survive an IRS Audit Storm"
  - "PTIN Renewal 2026: What Changed and What Tripped Everyone Up"
  - "Why Big Box Tax Firms Are Losing Clients to Solo EAs"
- [ ] Generate AI transcript (Riverside, Descript, or Whisper). Publish in full on the episode page.
- [ ] Write a 150-word episode summary with the top 5 keywords in the first 2 sentences.
- [ ] Add timestamp chapters to Spotify + Apple. Use real keyword phrases for each chapter.
- [ ] Pull 3 "key takeaways" as bullet points (LLMs cite these).
- [ ] Build an FAQ section: 4–6 questions a listener might Google after the episode. Answer in 2–3 sentences each.
- [ ] Add `PodcastEpisode` schema markup to the episode page (template in `templates/episode-page.html`).
- [ ] Internal-link from the episode page to the parent topic cluster page.
- [ ] Publish a 600-word LinkedIn article from the host's profile excerpting the episode. Link back.
- [ ] Cut 3 short clips for TikTok / Reels / Shorts (handled by the content engine).

## Per topic cluster (every 4–6 episodes)

- [ ] Build / update the pillar page (`/enrolled-agent-resources/`, `/irs-audit-help/`, etc.).
- [ ] Pillar page has: definition, "who needs this," 5–10 sub-topics linking to episodes, FAQ.
- [ ] Add internal links from older episodes to new cluster page.

## Apple / Spotify ranking factor checklist

- [ ] Show title contains primary keyword ("Enrolled Agent")
- [ ] First 250 chars of show description repeat the keyword + audience
- [ ] Episodes published on consistent cadence (weekly minimum)
- [ ] Subscriber growth (paid promo + cross-promo)
- [ ] Completion rate > 65% (cut episodes shorter if not hitting)
- [ ] 20+ ratings + reviews in first 90 days (ask listeners directly in episodes)
- [ ] Categories chosen: Business → Investing AND Education (not just one)

## GEO factors (covered separately in geo-strategy.md)

- [ ] `llms.txt` at site root
- [ ] Listed on Listen Notes, Podchaser, Goodpods with full descriptions
- [ ] Wikipedia entry for podcast or host (if criteria met)
- [ ] Reddit citations in r/tax, r/Accounting
- [ ] HARO responses citing podcast as source

## Monthly review

- [ ] Pull Apple Podcasts search rank for top 10 target keywords
- [ ] Pull Google search positions for episode pages
- [ ] Pull LLM citation count (search ChatGPT/Claude/Perplexity for show name + episode topics)
- [ ] Identify 3 underperforming episodes — rewrite titles + thumbnails
- [ ] Identify 1 overperforming episode — clone its structure for next month
