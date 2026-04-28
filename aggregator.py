# ============================================================
# NDC Investment Dashboard
# aggregator.py — RSS + scrape news aggregation engine
# Sprint 3
# ============================================================

import os
import json
import sqlite3
import time
import logging
import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

# Playwright for JS-rendered sites (optional)
try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

from feed_registry import SOURCES, credibility_score

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

# ============================================================
# CONFIGURATION
# ============================================================

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "database", "ndc_dashboard.db"
)

REQUEST_TIMEOUT  = 15
REQUEST_HEADERS  = {
    "User-Agent": "NDC-Dashboard/1.0 (climate research aggregator)",
    "Accept"    : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
MAX_ARTICLE_AGE  = 365   # days — prune older articles
MAX_PER_SOURCE   = 20    # articles per source per run


# ============================================================
# DATABASE SETUP
# ============================================================

def _ensure_tables():
    """Creates news_feed and feed_health tables."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS news_feed (
            article_id      TEXT PRIMARY KEY,
            title           TEXT NOT NULL,
            summary         TEXT,
            url             TEXT NOT NULL UNIQUE,
            image_url       TEXT,
            source_domain   TEXT NOT NULL,
            source_label    TEXT NOT NULL,
            source_tier     INTEGER NOT NULL,
            category        TEXT,
            published_date  TEXT,
            countries       TEXT DEFAULT '',
            sectors         TEXT DEFAULT '',
            credibility_score INTEGER DEFAULT 0,
            fetched_at      REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feed_health (
            domain          TEXT PRIMARY KEY,
            label           TEXT,
            method          TEXT,
            last_checked    REAL,
            status          TEXT,
            articles_found  INTEGER DEFAULT 0,
            error_message   TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

_ensure_tables()


def _article_id(url):
    """Generates a deterministic ID from article URL."""
    return hashlib.md5(url.encode()).hexdigest()[:16]


# ============================================================
# DATE PARSING
# ============================================================

def _parse_date(date_str):
    """
    Best-effort date parsing from various formats.
    Returns ISO date string YYYY-MM-DD or None.
    """
    if not date_str:
        return None

    # feedparser time struct
    if hasattr(date_str, "tm_year"):
        try:
            return time.strftime("%Y-%m-%d", date_str)
        except Exception:
            return None

    if isinstance(date_str, str):
        date_str = date_str.strip()
        # Try common formats
        for fmt in [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d %b %Y",
            "%d %B %Y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ]:
            try:
                dt = datetime.strptime(date_str[:len(fmt)+5], fmt)
                return dt.strftime("%Y-%m-%d")
            except (ValueError, IndexError):
                continue
        # Last resort — extract any YYYY-MM-DD pattern
        import re
        match = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
        if match:
            return match.group(1)

    return None


def _days_old(date_str):
    """Returns number of days since published date."""
    if not date_str:
        return 180  # assume ~6 months if unknown
    try:
        pub = datetime.strptime(date_str, "%Y-%m-%d")
        delta = datetime.now() - pub
        return max(0, delta.days)
    except Exception:
        return 180


# ============================================================
# RSS FETCHER
# ============================================================

def fetch_rss(source):
    """
    Fetches and parses an RSS/Atom feed.
    Returns list of article dicts.
    """
    feed_url = source.get("feed_url", "")
    if not feed_url:
        return []

    try:
        feed = feedparser.parse(
            feed_url,
            agent=REQUEST_HEADERS["User-Agent"]
        )

        if feed.bozo and not feed.entries:
            logging.warning(
                f"RSS parse error for {source['label']}: "
                f"{feed.bozo_exception}"
            )
            return []

        articles = []
        for entry in feed.entries[:MAX_PER_SOURCE]:
            title = entry.get("title", "").strip()
            link  = entry.get("link", "").strip()
            if not title or not link:
                continue

            # Summary — try several fields
            summary = ""
            if hasattr(entry, "summary"):
                summary = entry.summary
            elif hasattr(entry, "description"):
                summary = entry.description
            # Strip HTML from summary
            if summary:
                soup = BeautifulSoup(summary, "html.parser")
                summary = soup.get_text(separator=" ").strip()[:300]

            # Date
            date_raw = (
                entry.get("published_parsed")
                or entry.get("updated_parsed")
                or entry.get("published")
                or entry.get("updated")
            )
            pub_date = _parse_date(date_raw)

            # Image — check media, enclosures, content
            image_url = None
            if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                image_url = entry.media_thumbnail[0].get("url")
            elif hasattr(entry, "media_content") and entry.media_content:
                for mc in entry.media_content:
                    if mc.get("medium") == "image" or "image" in mc.get("type", ""):
                        image_url = mc.get("url")
                        break
            elif hasattr(entry, "enclosures") and entry.enclosures:
                for enc in entry.enclosures:
                    if "image" in enc.get("type", ""):
                        image_url = enc.get("href")
                        break
            # Fallback: check for og:image in content
            if not image_url and hasattr(entry, "content"):
                for c in entry.content:
                    soup = BeautifulSoup(c.get("value", ""), "html.parser")
                    img = soup.find("img")
                    if img and img.get("src"):
                        image_url = img["src"]
                        break

            days = _days_old(pub_date)
            score = credibility_score(source["tier"], days)

            articles.append({
                "article_id"       : _article_id(link),
                "title"            : title[:200],
                "summary"          : summary[:300],
                "url"              : link,
                "image_url"        : image_url,
                "source_domain"    : source["domain"],
                "source_label"     : source["label"],
                "source_tier"      : source["tier"],
                "category"         : source.get("category", "news"),
                "published_date"   : pub_date,
                "credibility_score": score,
            })

        return articles

    except Exception as e:
        logging.warning(f"RSS fetch failed for {source['label']}: {e}")
        return []


# ============================================================
# GENERIC HTML SCRAPER
# ============================================================

def fetch_scrape(source):
    """
    Scrapes a news listing page for article links.
    Uses common HTML patterns to find articles.
    Returns list of article dicts.
    """
    scrape_url = source.get("scrape_url", "")
    if not scrape_url:
        return []

    try:
        resp = requests.get(
            scrape_url,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = []

        # Strategy: find article-like containers, then extract
        # title (linked heading) and optional summary/date/image

        # Candidate containers — try in order of specificity
        containers = (
            soup.find_all("article", limit=MAX_PER_SOURCE)
            or soup.find_all("div", class_=lambda c: c and any(
                x in str(c).lower() for x in
                ["post", "story", "article", "card", "item",
                 "news", "entry", "listing", "result"]
            ), limit=MAX_PER_SOURCE)
            or soup.find_all("li", class_=lambda c: c and any(
                x in str(c).lower() for x in
                ["post", "story", "article", "item", "news"]
            ), limit=MAX_PER_SOURCE)
        )

        if not containers:
            # Fallback: find all headings with links
            headings = soup.find_all(["h2", "h3", "h4"], limit=MAX_PER_SOURCE)
            for h in headings:
                a = h.find("a", href=True)
                if a and a.get("href"):
                    link = urljoin(scrape_url, a["href"])
                    title = a.get_text(strip=True)
                    if title and len(title) > 10:
                        days = 90  # unknown date for heading-only
                        score = credibility_score(source["tier"], days)
                        articles.append({
                            "article_id"       : _article_id(link),
                            "title"            : title[:200],
                            "summary"          : "",
                            "url"              : link,
                            "image_url"        : None,
                            "source_domain"    : source["domain"],
                            "source_label"     : source["label"],
                            "source_tier"      : source["tier"],
                            "category"         : source.get("category", "news"),
                            "published_date"   : None,
                            "credibility_score": score,
                        })
            return articles

        for container in containers:
            # Find linked heading
            heading = container.find(["h1", "h2", "h3", "h4", "h5"])
            a_tag   = None

            if heading:
                a_tag = heading.find("a", href=True)
            if not a_tag:
                a_tag = container.find("a", href=True)
            if not a_tag or not a_tag.get("href"):
                continue

            link  = urljoin(scrape_url, a_tag["href"])
            title = (
                heading.get_text(strip=True) if heading
                else a_tag.get_text(strip=True)
            )
            if not title or len(title) < 10:
                continue

            # Summary — look for <p> or summary-like class
            summary = ""
            p_tag = container.find("p")
            if p_tag:
                summary = p_tag.get_text(strip=True)[:300]
            if not summary:
                desc = container.find(
                    class_=lambda c: c and any(
                        x in str(c).lower() for x in
                        ["desc", "summary", "excerpt", "teaser", "blurb"]
                    )
                )
                if desc:
                    summary = desc.get_text(strip=True)[:300]

            # Date — look for <time> or date-like class
            pub_date = None
            time_tag = container.find("time")
            if time_tag:
                pub_date = _parse_date(
                    time_tag.get("datetime") or time_tag.get_text(strip=True)
                )
            if not pub_date:
                date_el = container.find(
                    class_=lambda c: c and any(
                        x in str(c).lower() for x in
                        ["date", "time", "published", "posted"]
                    )
                )
                if date_el:
                    pub_date = _parse_date(date_el.get_text(strip=True))

            # Image
            image_url = None
            img_tag = container.find("img")
            if img_tag:
                image_url = img_tag.get("src") or img_tag.get("data-src")
                if image_url:
                    image_url = urljoin(scrape_url, image_url)

            days  = _days_old(pub_date)
            score = credibility_score(source["tier"], days)

            articles.append({
                "article_id"       : _article_id(link),
                "title"            : title[:200],
                "summary"          : summary[:300],
                "url"              : link,
                "image_url"        : image_url,
                "source_domain"    : source["domain"],
                "source_label"     : source["label"],
                "source_tier"      : source["tier"],
                "category"         : source.get("category", "news"),
                "published_date"   : pub_date,
                "credibility_score": score,
            })

        return articles

    except Exception as e:
        logging.warning(f"Scrape failed for {source['label']}: {e}")
        return []


# ============================================================
# PLAYWRIGHT FETCHER (for JS-rendered sites)
# ============================================================

def fetch_playwright(source):
    """
    Fetches a JS-rendered page using Playwright headless browser.
    Falls back to regular scrape if Playwright unavailable.
    """
    if not HAS_PLAYWRIGHT:
        logging.warning(f"Playwright not installed, skipping {source['label']}")
        return []

    scrape_url = source.get("scrape_url", "")
    if not scrape_url:
        return []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/124.0.0.0 Safari/537.36"
            )
            page = ctx.new_page()
            page.goto(scrape_url, timeout=20000)
            page.wait_for_timeout(4000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        articles = []

        # Find links that look like news articles
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)

            # Skip navigation, short text, and self-links
            if len(text) < 20:
                continue
            if href == scrape_url or href.endswith(("/news", "/news/")):
                continue
            # Skip obvious navigation and category pages
            nav_words = ["browse all", "read more", "view all",
                         "see all", "load more", "reports and research",
                         "policy papers", "publications", "subscribe",
                         "sign up", "contact us", "about us"]
            if any(nw in text.lower() for nw in nav_words):
                continue
            # Skip root category pages (but not individual articles)
            skip_endings = ["/news", "/stories", "/press-releases",
                           "/blog", "/publications", "/reports"]
            clean_href = href.rstrip("/")
            if any(clean_href.endswith(e) for e in skip_endings):
                continue

            # Must look like a news/article URL
            news_patterns = ["/news/", "/news-and-stories/",
                           "/stories/", "/story/",
                           "/press-release", "/article/", "/blog/",
                           "/update/", "/feature/", "/publication",
                           "/media-advisories/", "/speech-statements/",
                           "/climatechange/", "/climate/",
                           "/energy/", "/sustainability/"]
            if not any(pat in href for pat in news_patterns):
                continue

            link = urljoin(scrape_url, href)
            title = text[:200]

            # Look for date near the link
            pub_date = None
            parent = a.find_parent(["div", "article", "li", "section"])
            if parent:
                time_tag = parent.find("time")
                if time_tag:
                    pub_date = _parse_date(
                        time_tag.get("datetime") or time_tag.get_text(strip=True)
                    )
                if not pub_date:
                    # Try to extract date from the text around the link
                    parent_text = parent.get_text(" ", strip=True)
                    import re
                    date_match = re.search(
                        r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4})",
                        parent_text
                    )
                    if date_match:
                        pub_date = _parse_date(date_match.group(1))

            # Look for image
            image_url = None
            if parent:
                img = parent.find("img")
                if img:
                    image_url = img.get("src") or img.get("data-src")
                    if image_url:
                        image_url = urljoin(scrape_url, image_url)

            # Summary from sibling paragraph
            summary = ""
            if parent:
                p_tag = parent.find("p")
                if p_tag:
                    summary = p_tag.get_text(strip=True)[:300]

            # Fallback: extract date from URL path (e.g. /2026/04/)
            if not pub_date:
                import re as _re
                url_date = _re.search(r"/(\d{4})/(\d{2})/", link)
                if url_date:
                    pub_date = f"{url_date.group(1)}-{url_date.group(2)}-01"

            days = _days_old(pub_date)
            score = credibility_score(source["tier"], days)

            articles.append({
                "article_id"       : _article_id(link),
                "title"            : title,
                "summary"          : summary,
                "url"              : link,
                "image_url"        : image_url,
                "source_domain"    : source["domain"],
                "source_label"     : source["label"],
                "source_tier"      : source["tier"],
                "category"         : source.get("category", "news"),
                "published_date"   : pub_date,
                "credibility_score": score,
            })

            if len(articles) >= MAX_PER_SOURCE:
                break

        return articles

    except Exception as e:
        logging.warning(f"Playwright fetch failed for {source['label']}: {e}")
        return []


# ============================================================
# STORAGE
# ============================================================

def store_articles(articles):
    """
    Writes articles to the news_feed table.
    Skips duplicates by URL (via article_id).
    Returns count of newly inserted articles.
    """
    if not articles:
        return 0

    conn = sqlite3.connect(DB_PATH)
    inserted = 0

    for a in articles:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO news_feed
                (article_id, title, summary, url, image_url,
                 source_domain, source_label, source_tier, category,
                 published_date, countries, sectors,
                 credibility_score, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                a["article_id"],
                a["title"],
                a.get("summary", ""),
                a["url"],
                a.get("image_url"),
                a["source_domain"],
                a["source_label"],
                a["source_tier"],
                a.get("category", "news"),
                a.get("published_date"),
                a.get("countries", ""),
                a.get("sectors", ""),
                a.get("credibility_score", 0),
                time.time(),
            ))
            if conn.total_changes:
                inserted += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    return inserted


def prune_old_articles():
    """Removes articles older than MAX_ARTICLE_AGE days."""
    cutoff = (
        datetime.now() - timedelta(days=MAX_ARTICLE_AGE)
    ).strftime("%Y-%m-%d")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(
            "DELETE FROM news_feed WHERE published_date < ? "
            "AND published_date IS NOT NULL", (cutoff,)
        )
        pruned = cursor.rowcount
        conn.commit()
        conn.close()
        return pruned
    except Exception:
        return 0


# ============================================================
# HEALTH TRACKING
# ============================================================

def _log_health(source, status, count, error=""):
    """Records source health after a fetch attempt."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT OR REPLACE INTO feed_health
            (domain, label, method, last_checked, status,
             articles_found, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            source["domain"],
            source["label"],
            source["method"],
            time.time(),
            status,
            count,
            str(error)[:200],
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass


# ============================================================
# MAIN AGGREGATOR
# ============================================================

def run_aggregator(sources=None):
    """
    Runs the full aggregation cycle.
    Fetches from all sources, stores results, prunes old data.
    Returns summary dict.
    """
    if sources is None:
        sources = SOURCES

    total_articles  = 0
    total_inserted  = 0
    sources_ok      = 0
    sources_failed  = 0
    source_details  = []

    logging.info(f"Starting aggregation: {len(sources)} sources")

    for source in sources:
        label  = source["label"]
        method = source["method"]

        try:
            if method == "rss":
                articles = fetch_rss(source)
            elif method == "playwright":
                articles = fetch_playwright(source)
            elif method == "scrape":
                articles = fetch_scrape(source)
            else:
                logging.warning(f"Unknown method for {label}: {method}")
                continue

            count    = len(articles)
            inserted = store_articles(articles)

            total_articles += count
            total_inserted += inserted

            if count > 0:
                sources_ok += 1
                _log_health(source, "ok", count)
                logging.info(
                    f"  {label}: {count} found, {inserted} new"
                )
            else:
                sources_failed += 1
                _log_health(source, "empty", 0)
                logging.warning(f"  {label}: no articles found")

            source_details.append({
                "label"    : label,
                "method"   : method,
                "found"    : count,
                "inserted" : inserted,
                "status"   : "ok" if count > 0 else "empty",
            })

        except Exception as e:
            sources_failed += 1
            _log_health(source, "error", 0, str(e))
            logging.error(f"  {label}: ERROR — {e}")
            source_details.append({
                "label"    : label,
                "method"   : method,
                "found"    : 0,
                "inserted" : 0,
                "status"   : f"error: {e}",
            })

    # Prune old articles
    pruned = prune_old_articles()

    summary = {
        "sources_total"   : len(sources),
        "sources_ok"      : sources_ok,
        "sources_failed"  : sources_failed,
        "articles_found"  : total_articles,
        "articles_new"    : total_inserted,
        "articles_pruned" : pruned,
        "details"         : source_details,
    }

    logging.info(
        f"Aggregation complete: {sources_ok}/{len(sources)} sources, "
        f"{total_articles} articles found, {total_inserted} new, "
        f"{pruned} pruned"
    )

    return summary


# ============================================================
# QUERY HELPERS (used by dashboard)
# ============================================================

def get_articles_for_country(iso_code, limit=5):
    """Returns top articles tagged with a country ISO code."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("""
            SELECT title, summary, url, image_url,
                   source_label, source_tier, published_date,
                   credibility_score
            FROM news_feed
            WHERE countries LIKE ?
            ORDER BY credibility_score DESC, published_date DESC
            LIMIT ?
        """, (f"%{iso_code}%", limit)).fetchall()
        conn.close()
        return [
            {
                "title"       : r[0],
                "summary"     : r[1],
                "url"         : r[2],
                "image_url"   : r[3],
                "source"      : r[4],
                "tier"        : r[5],
                "date"        : r[6],
                "score"       : r[7],
            }
            for r in rows
        ]
    except Exception:
        return []


def get_articles_for_sector(iso_code, sector, limit=5):
    """Returns top articles tagged with a country + sector."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("""
            SELECT title, summary, url, image_url,
                   source_label, source_tier, published_date,
                   credibility_score
            FROM news_feed
            WHERE countries LIKE ?
            AND sectors LIKE ?
            ORDER BY credibility_score DESC, published_date DESC
            LIMIT ?
        """, (f"%{iso_code}%", f"%{sector}%", limit)).fetchall()
        conn.close()
        return [
            {
                "title"       : r[0],
                "summary"     : r[1],
                "url"         : r[2],
                "image_url"   : r[3],
                "source"      : r[4],
                "tier"        : r[5],
                "date"        : r[6],
                "score"       : r[7],
            }
            for r in rows
        ]
    except Exception:
        return []


def get_feed_stats():
    """Returns summary stats for the news feed."""
    try:
        conn = sqlite3.connect(DB_PATH)
        total = conn.execute(
            "SELECT COUNT(*) FROM news_feed"
        ).fetchone()[0]
        with_country = conn.execute(
            "SELECT COUNT(*) FROM news_feed WHERE countries != ''"
        ).fetchone()[0]
        sources = conn.execute(
            "SELECT COUNT(DISTINCT source_domain) FROM news_feed"
        ).fetchone()[0]
        conn.close()
        return {
            "total_articles"  : total,
            "tagged_articles" : with_country,
            "active_sources"  : sources,
        }
    except Exception:
        return {"total_articles": 0, "tagged_articles": 0, "active_sources": 0}


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    print("Aggregator module loaded")
    stats = get_feed_stats()
    print(f"  DB articles : {stats['total_articles']}")
    print(f"  Tagged      : {stats['tagged_articles']}")
    print(f"  Sources     : {stats['active_sources']}")
    print()
    print("  To run full aggregation:")
    print("    python3 aggregator.py --run")

    import sys
    if "--run" in sys.argv:
        summary = run_aggregator()
        print(f"\n  Results:")
        print(f"    Sources OK    : {summary['sources_ok']}/{summary['sources_total']}")
        print(f"    Articles found: {summary['articles_found']}")
        print(f"    New stored    : {summary['articles_new']}")
        print(f"    Pruned        : {summary['articles_pruned']}")
