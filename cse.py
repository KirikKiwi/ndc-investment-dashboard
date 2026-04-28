# ============================================================
# NDC Investment Dashboard
# cse.py — Google Custom Search Engine integration
# Sprint 3: News and subsidy data for country + sector panels
# ============================================================

import os
import json
import sqlite3
import time
import logging
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

CSE_API_KEY = os.getenv("GOOGLE_CSE_KEY", "")
CSE_ID      = os.getenv("GOOGLE_CSE_ID", "")

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "database", "ndc_dashboard.db"
)

CACHE_TTL   = 86400      # 24 hours
API_TIMEOUT = 10         # seconds
MAX_RESULTS = 5

# ============================================================
# CACHE LAYER
# ============================================================

def _ensure_cache_table():
    """Creates cse_cache table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cse_cache (
                cache_key  TEXT PRIMARY KEY,
                results    TEXT NOT NULL,
                fetched_at REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logging.warning(f"CSE cache table creation failed: {e}")

_ensure_cache_table()


def _cache_key(query_type, country, sector=None):
    """Deterministic cache key from query parameters."""
    parts = [query_type, country.lower().strip()]
    if sector:
        parts.append(sector.lower().strip())
    return "|".join(parts)


def _get_cached(key):
    """Returns cached results if within TTL, else None."""
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT results, fetched_at FROM cse_cache WHERE cache_key = ?",
            (key,)
        ).fetchone()
        conn.close()
        if row and (time.time() - row[1]) < CACHE_TTL:
            return json.loads(row[0])
    except Exception:
        pass
    return None


def _set_cache(key, results):
    """Writes results to cache."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT OR REPLACE INTO cse_cache "
            "(cache_key, results, fetched_at) VALUES (?, ?, ?)",
            (key, json.dumps(results), time.time())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


# ============================================================
# API LAYER
# ============================================================

def _cse_query(query):
    """
    Executes a single Google CSE query.
    Returns list of result dicts or empty list on failure.
    """
    if not CSE_API_KEY or not CSE_ID:
        logging.warning("CSE credentials not configured")
        return []

    params = urlencode({
        "key"  : CSE_API_KEY,
        "cx"   : CSE_ID,
        "q"    : query,
        "num"  : MAX_RESULTS,
        "sort" : "date",
    })
    url = f"https://www.googleapis.com/customsearch/v1?{params}"

    try:
        req = Request(url, headers={"User-Agent": "NDC-Dashboard/1.0"})
        with urlopen(req, timeout=API_TIMEOUT) as resp:
            data = json.loads(resp.read())

        items = data.get("items", [])
        results = []
        for item in items:
            title = item.get("title", "").strip()
            link  = item.get("link", "")
            if not title or not link:
                continue

            # Extract date from metadata if available
            metatags = item.get("pagemap", {}).get("metatags", [{}])
            meta = metatags[0] if metatags else {}
            date = (
                meta.get("article:published_time", "")
                or meta.get("og:updated_time", "")
                or meta.get("date", "")
                or item.get("snippet", "")[:15]  # fallback: snippet start
            )
            # Clean date to just the date portion
            date = date[:10] if len(date) >= 10 else date

            results.append({
                "title"   : title,
                "link"    : link,
                "snippet" : item.get("snippet", "").strip(),
                "source"  : item.get("displayLink", ""),
                "date"    : date,
            })

        return results

    except Exception as e:
        logging.warning(f"CSE query failed for '{query}': {e}")
        return []


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def get_cse_news(country_name):
    """
    Fetches climate investment news for a country.
    Used in: country panel news section.
    """
    key    = _cache_key("news", country_name)
    cached = _get_cached(key)
    if cached is not None:
        return cached

    query   = f'"{country_name}" climate investment finance'
    results = _cse_query(query)
    _set_cache(key, results)
    return results


def get_cse_subsidies(country_name):
    """
    Fetches subsidy and incentive data for a country.
    Used in: country panel subsidies section.
    """
    key    = _cache_key("subsidies", country_name)
    cached = _get_cached(key)
    if cached is not None:
        return cached

    query   = f'"{country_name}" climate subsidy incentive renewable policy'
    results = _cse_query(query)
    _set_cache(key, results)
    return results


def get_cse_sector_news(country_name, sector_name):
    """
    Fetches sector-specific climate investment news.
    Used in: Tier 3 panel news section.
    """
    key    = _cache_key("sector_news", country_name, sector_name)
    cached = _get_cached(key)
    if cached is not None:
        return cached

    query   = f'"{country_name}" {sector_name} investment climate'
    results = _cse_query(query)
    _set_cache(key, results)
    return results


def is_configured():
    """Returns True if CSE credentials are set."""
    return bool(CSE_API_KEY and CSE_ID)


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    print("CSE module loaded")
    print(f"  Configured : {is_configured()}")
    print(f"  API key    : {CSE_API_KEY[:8]}..." if CSE_API_KEY else "  API key    : NOT SET")
    print(f"  CSE ID     : {CSE_ID[:8]}..." if CSE_ID else "  CSE ID     : NOT SET")
    print(f"  DB path    : {DB_PATH}")
    print(f"  Cache TTL  : {CACHE_TTL // 3600}h")
