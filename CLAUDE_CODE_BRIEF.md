# Claude Code Project Brief — Green-Gott's Vault (NDC Climate Investment Dashboard)

## What This Is
An interactive climate investment intelligence dashboard for PE/investment analysts. Maps NDC commitments, sector investment signals and climate risk data across 199 countries. Currently named "NDC Intelligence" — being renamed to "Green-Gott's Vault" as part of beta 2.0.

## Tech Stack
- Python 3.13, Plotly Dash 4.x, SQLite, D3.js v7, TopoJSON
- Run: `cd ~/Documents/ndc_dashboard && source venv/bin/activate && python app.py`
- URL: http://127.0.0.1:8050

## File Structure
ndc_dashboard/

├── app.py              — Entry point

├── layout.py           — Page routing (/ → landing, /dashboard → globe)

├── callbacks.py        — All Dash callbacks

├── data.py             — DB queries, regions, groups, benchmark scoring

├── components.py       — C dict (colours), T dict (typography), UI components

├── cse.py              — Google CSE module (written, API auth parked)

├── aggregator.py       — RSS + scrape news aggregation (37/51 sources working)

├── classifier.py       — Country/sector tagging for news articles

├── feed_registry.py    — 51 curated news sources with tier/method config

├── news_render.py      — Dash components for news article cards

├── wgi.py              — World Bank governance indicators (207 countries)

├── oecd_rio.py         — OECD Rio Markers climate finance data (151 countries)

├── export_feed.py      — Excel export of news feed

├── POLISH.md           — Tracked refinement items

├── CLAUDE_CODE_BRIEF.md — This file

├── .env                — Google CSE credentials (gitignored)

├── pages/

│   ├── __init__.py

│   ├── landing.py      — Landing page

│   ├── globe.py        — Globe page + country panel (section_title, country_panel_content)

│   ├── analytics.py    — Global analytics (4 sections + filter bar)

│   └── tier3.py        — Sector deep-dive panel (tier3_content)

├── assets/

│   ├── globe.css       — Globe, controls, panel positioning, info-tip tooltip

│   ├── globe2.js       — D3 globe logic (named globe2.js not globe.js — cache bust)

│   ├── grid.css        — Background grid

│   └── world-110m.json — TopoJSON country boundaries

└── data/

├── database/ndc_dashboard.db  — SQLite (~12MB, 17 tables)

└── exports/                   — CSV/Excel exports

## Database Tables (17)
- master_countries (199) — joined master with benchmark_score, tiers, indicators
- ndc_indicators (82,941) — 671 indicators × 198 countries
- ndc_sector_tags (1,304) — 7 sectors × 197 countries with dimensions
- ndc_country_summary (198) — NDC text summaries per country
- wb_indicators (198) — 16 economic indicators
- ndgain_scores (187) — 10 vulnerability/readiness scores
- mdb_projects (500) — World Bank climate projects
- finance_signals (45) — Conditional/unconditional % extraction
- policy_renewable_electricity (213) — OWID renewable data
- news_feed (638) — Aggregated news articles with country/sector tags
- feed_health (50) — Source health tracking
- cse_cache (1) — Google CSE cache (mostly unused)
- wgi_governance (207) — World Bank governance indicators
- oecd_rio_markers (3,392) — OECD climate finance flows
- carbon_emissions (240), policy_emissions_extra (278), policy_renewable_share_electricity (251)

## Colour System (components.py)
```python
bg=#0a0a0a, surface=#111111, surface_high=#1a1a1a, border=#2a2a2a
emerald=#00c896, crimson=#c0392b, amber=#e67e22, cobalt=#2980b9
tier1=#00c896, tier2=#e67e22, tier3=#c0392b
```

## Key Architecture Patterns
- globe2.js (not globe.js) — D3 globe, renamed to bust browser cache
- D3→Dash communication via hidden inputs: d3-click-input, tier3-sector-input, tier3-close-input
- Pattern matching callbacks avoided — unreliable for re-rendered components
- Tier3 uses data-sector-key HTML attribute + JS listener → hidden input → Dash callback
- PROJECTS_WITH_ISO pre-computed at import in data.py
- _benchmark_lookup dict pre-computed at import in data.py
- suppress_callback_exceptions=True in app.py
- section_title() in globe.py supports tooltip parameter (CSS hover, class="info-tip")

## What's Built and Working
- Landing page with content sections
- D3 orthographic globe with rotation, zoom, drag, 4 colour modes
- Country panel (slides in from right) with 10+ sections including governance, climate finance, news, subsidies
- Tier 3 sector deep-dive panel (slides in from left)
- Global analytics (4 sections + filter bar with region/group/country/reset/export)
- News feed pipeline (37/51 sources, classifier, credibility scoring)
- WGI governance indicators in country panel
- OECD Rio Markers climate finance in country panel
- CSS tooltips for methodology explanations
- Excel export for news feed

## Composite Benchmark Formula
Readiness Score       30%

GDP per Capita        25%

Renewable %           20%

Vulnerability (inv.)  15%

WB Project Count       5%

Conditional Uplift     5% (inverted)

All metrics normalised 0-1. Countries missing data get median.

## Workflow Rules
1. ALWAYS verify imports and function output before restarting server
2. Commit at every working checkpoint with descriptive messages
3. When editing large files, verify the edit landed correctly
4. Test with Kenya (KEN), Germany (DEU), and a SIDS country for coverage
5. The app must remain functional after every change — no breaking deployments
6. Read files before editing — understand the current state first
