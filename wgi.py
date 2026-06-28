# ============================================================
# NDC Investment Dashboard
# wgi.py: World Bank Worldwide Governance Indicators
# Sprint 3: Governance layer for country panel and benchmark
# ============================================================

import os
import json
import sqlite3
import time
import logging
from urllib.request import urlopen, Request
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "database", "ndc_dashboard.db"
)

# WGI indicators: .SC variants give 0-100 scores
WGI_CODES = {
    "GOV_WGI_PV.SC": "political_stability",
    "GOV_WGI_RL.SC": "rule_of_law",
    "GOV_WGI_GE.SC": "govt_effectiveness",
    "GOV_WGI_CC.SC": "control_corruption",
}

WGI_LABELS = {
    "political_stability" : "Political Stability",
    "rule_of_law"         : "Rule of Law",
    "govt_effectiveness"  : "Government Effectiveness",
    "control_corruption"  : "Control of Corruption",
}

API_BASE = "https://api.worldbank.org/v2"
API_TIMEOUT = 15
CALL_DELAY  = 0.5  # seconds between API calls


# ============================================================
# DATABASE
# ============================================================

def _ensure_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wgi_governance (
            iso_code             TEXT PRIMARY KEY,
            political_stability  REAL,
            rule_of_law          REAL,
            govt_effectiveness   REAL,
            control_corruption   REAL,
            governance_score     REAL,
            data_year            TEXT,
            fetched_at           REAL
        )
    """)
    conn.commit()
    conn.close()

_ensure_table()


# ============================================================
# API FETCHER
# ============================================================

def _fetch_indicator_all(indicator_code):
    """
    Fetches most recent value for all countries at once.
    Returns dict: ISO2 -> value
    """
    url = (
        f"{API_BASE}/country/all/indicator/{indicator_code}"
        f"?format=json&mrv=1&per_page=300&source=3"
    )

    try:
        req = Request(url, headers={"User-Agent": "NDC-Dashboard/1.0"})
        with urlopen(req, timeout=API_TIMEOUT) as resp:
            data = json.loads(resp.read())

        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return {}

        results = {}
        year = None
        for entry in data[1]:
            iso2 = entry.get("countryiso3code") or entry.get("country", {}).get("id", "")
            val  = entry.get("value")
            if iso2 and val is not None:
                results[iso2] = round(float(val), 1)
                if not year:
                    year = entry.get("date")

        return results, year

    except Exception as e:
        logging.warning(f"WGI fetch failed for {indicator_code}: {e}")
        return {}, None


def fetch_all_wgi():
    """
    Fetches all four WGI indicators for all countries.
    Returns dict: ISO3 -> {indicator_name: value, ...}
    """
    all_data = {}  # iso3 -> {col: val}

    for api_code, col_name in WGI_CODES.items():
        logging.info(f"Fetching {col_name}...")
        result = _fetch_indicator_all(api_code)

        if isinstance(result, tuple):
            values, year = result
        else:
            values, year = result, None

        for iso3, val in values.items():
            if len(iso3) == 3:  # skip region codes
                if iso3 not in all_data:
                    all_data[iso3] = {"data_year": year}
                all_data[iso3][col_name] = val

        time.sleep(CALL_DELAY)

    # Calculate composite governance score (simple average)
    for iso3, scores in all_data.items():
        vals = [
            scores.get("political_stability"),
            scores.get("rule_of_law"),
            scores.get("govt_effectiveness"),
            scores.get("control_corruption"),
        ]
        valid = [v for v in vals if v is not None]
        if valid:
            scores["governance_score"] = round(sum(valid) / len(valid), 1)
        else:
            scores["governance_score"] = None

    return all_data


def store_wgi(data):
    """Stores WGI data in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    stored = 0
    for iso3, scores in data.items():
        try:
            conn.execute("""
                INSERT OR REPLACE INTO wgi_governance
                (iso_code, political_stability, rule_of_law,
                 govt_effectiveness, control_corruption,
                 governance_score, data_year, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                iso3,
                scores.get("political_stability"),
                scores.get("rule_of_law"),
                scores.get("govt_effectiveness"),
                scores.get("control_corruption"),
                scores.get("governance_score"),
                scores.get("data_year"),
                time.time(),
            ))
            stored += 1
        except Exception:
            pass
    conn.commit()
    conn.close()
    return stored


# ============================================================
# QUERY FUNCTIONS (used by dashboard)
# ============================================================

def get_governance(iso_code):
    """
    Returns governance data for a single country.
    Returns dict or None.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT political_stability, rule_of_law, "
            "govt_effectiveness, control_corruption, "
            "governance_score, data_year "
            "FROM wgi_governance WHERE iso_code = ?",
            (iso_code,)
        ).fetchone()
        conn.close()

        if not row:
            return None

        return {
            "political_stability" : row[0],
            "rule_of_law"         : row[1],
            "govt_effectiveness"  : row[2],
            "control_corruption"  : row[3],
            "governance_score"    : row[4],
            "data_year"           : row[5],
        }
    except Exception:
        return None


def get_governance_score(iso_code):
    """Returns just the composite governance score (0-100)."""
    gov = get_governance(iso_code)
    if gov:
        return gov.get("governance_score")
    return None


def get_all_governance_scores():
    """Returns dict: ISO3 -> governance_score for all countries."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT iso_code, governance_score FROM wgi_governance "
            "WHERE governance_score IS NOT NULL"
        ).fetchall()
        conn.close()
        return {r[0]: r[1] for r in rows}
    except Exception:
        return {}


def wgi_stats():
    """Returns count of countries with WGI data."""
    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute(
            "SELECT COUNT(*) FROM wgi_governance"
        ).fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


# ============================================================
# MAIN
# ============================================================

def run_wgi_fetch():
    """Full fetch cycle: pull all indicators, store in DB."""
    logging.info("Starting WGI fetch...")
    data = fetch_all_wgi()
    stored = store_wgi(data)
    logging.info(f"WGI complete: {stored} countries stored")
    return stored


if __name__ == "__main__":
    import sys
    if "--fetch" in sys.argv:
        count = run_wgi_fetch()
        print(f"\nStored {count} countries")
    else:
        count = wgi_stats()
        print(f"WGI module loaded")
        print(f"  Countries in DB: {count}")
        print(f"  Indicators: {len(WGI_CODES)}")
        print(f"  Run with --fetch to pull data")
