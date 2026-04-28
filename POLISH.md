# Sprint 3 — Polish and Refinement List

## Classifier Quality
1. Transport keyword false positives — "transport" matches too broadly
2. Country relevance filter — require climate/finance keyword alongside country name
3. EU collective tagging — propagate EU articles to member state ISOs
4. "port" residual — use word boundary matching for all sector keywords

## Source Coverage
5. 22 failed scrape sources — need Playwright for JS-rendered and anti-bot sites
6. Image extraction — fetch og:image from article pages as fallback
7. Date extraction — improve per-source date parsing for scraped articles

## Dashboard Display
8. Credibility score — show to user or rank invisibly?
9. Source tier badge — visual indicator in article cards
10. Subsidy vs news separation — filter by category field in dashboard

## Infrastructure
11. Google CSE revival — fresh Google Cloud project
12. Aggregator cron — automate weekly runs
13. Feed health monitoring — scheduled checks with notifications
14. Carbon registries — revisit for voluntary carbon market layer

## Data Quality
15. Article deduplication — group same story across sources

## Data Integrations (Pending)
16. OECD CRS / Rio Markers — API unstable, download CSV manually from data-explorer.oecd.org and process locally
17. IATI — d-portal data quality too low (dominated by small NGO projects). Revisit with official IATI datastore API key, filter by major DFIs only
18. Blocked news sources (14) — Reuters, Bloomberg, FT, Devex, IRENA, AfDB, IADB need paid proxy or official API access
