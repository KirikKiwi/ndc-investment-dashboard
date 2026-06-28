# ============================================================
# NDC Investment Dashboard
# oecd_rio.py: OECD Rio Markers climate finance data
# Sprint 3: Investment Landscape section
# ============================================================

import os
import json
import sqlite3
import time
import logging
from urllib.request import urlopen, Request

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "database", "ndc_dashboard.db"
)

API_BASE = "https://sdmx.oecd.org/dcd-public/rest/data/OECD.DCD.FSD,DSD_RIOMRKR@DF_RIOMARKERS,1.6"
API_TIMEOUT = 30

MARKERS = {
    "20": "mitigation",
    "30": "adaptation",
}


# ============================================================
# DATABASE
# ============================================================

def _ensure_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS oecd_rio_markers (
            iso_code    TEXT NOT NULL,
            country     TEXT,
            marker      TEXT NOT NULL,
            score       TEXT NOT NULL,
            year        INTEGER NOT NULL,
            value_usd   REAL,
            fetched_at  REAL,
            PRIMARY KEY (iso_code, marker, score, year)
        )
    """)
    conn.commit()
    conn.close()

_ensure_table()


# ============================================================
# API FETCHER
# ============================================================

def _fetch_marker(marker_code):
    """
    Fetches Rio Marker data for a single marker.
    Returns list of dicts: iso_code, country, marker, score, year, value
    """
    url = (
        f"{API_BASE}/DAC_EC..1000..2.{marker_code}.1+2..Q._T.."
        f"?startPeriod=2019&dimensionAtObservation=AllDimensions"
    )

    req = Request(url, headers={
        "User-Agent": "NDC-Dashboard/1.0",
        "Accept": "application/vnd.sdmx.data+json"
    })

    with urlopen(req, timeout=API_TIMEOUT) as resp:
        data = json.loads(resp.read())

    datasets = data.get("data", {}).get("dataSets", [])
    structure = data.get("data", {}).get("structures", [])

    if not datasets or not structure:
        return []

    # Build dimension lookup
    dims = structure[0].get("dimensions", {}).get("observation", [])
    dim_lookup = {}
    for d in dims:
        dim_id = d.get("id", "")
        values = d.get("values", [])
        dim_lookup[dim_id] = {
            "position": d.get("position", 0),
            "values": {i: v for i, v in enumerate(values)}
        }

    # Find dimension positions
    recipient_dim = None
    time_dim = None
    score_dim = None
    marker_dim = None

    for i, d in enumerate(dims):
        did = d.get("id", "")
        if did == "RECIPIENT":
            recipient_dim = i
        elif did == "TIME_PERIOD":
            time_dim = i
        elif did == "SCORE":
            score_dim = i
        elif did == "MARKER":
            marker_dim = i

    observations = datasets[0].get("observations", {})
    results = []

    for key, values in observations.items():
        indices = [int(x) for x in key.split(":")]
        value = values[0] if values else None

        if value is None or value == 0:
            continue

        # Extract dimension values
        recipient_info = dim_lookup["RECIPIENT"]["values"].get(
            indices[recipient_dim], {}
        )
        time_info = dim_lookup["TIME_PERIOD"]["values"].get(
            indices[time_dim], {}
        )
        score_info = dim_lookup["SCORE"]["values"].get(
            indices[score_dim], {}
        )

        iso_code = recipient_info.get("id", "")
        country_name = recipient_info.get("name", "")
        year = time_info.get("id", "")
        score_label = score_info.get("name", "")
        marker_label = MARKERS.get(marker_code, marker_code)

        # Skip aggregate regions (non 3-letter codes)
        if len(iso_code) != 3:
            continue

        results.append({
            "iso_code": iso_code,
            "country": country_name,
            "marker": marker_label,
            "score": score_label,
            "year": int(year) if year.isdigit() else 0,
            "value_usd": round(value, 2),
        })

    return results


def store_results(results):
    """Stores results in SQLite."""
    conn = sqlite3.connect(DB_PATH)
    stored = 0
    for r in results:
        try:
            conn.execute("""
                INSERT OR REPLACE INTO oecd_rio_markers
                (iso_code, country, marker, score, year, value_usd, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                r["iso_code"], r["country"], r["marker"],
                r["score"], r["year"], r["value_usd"], time.time()
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

def get_climate_finance(iso_code):
    """
    Returns climate finance summary for a country.
    Aggregates mitigation + adaptation, principal + significant.
    Returns dict with totals and yearly breakdown.
    """
    try:
        conn = sqlite3.connect(DB_PATH)

        # Most recent year totals
        latest = conn.execute("""
            SELECT marker, SUM(value_usd) as total
            FROM oecd_rio_markers
            WHERE iso_code = ?
            AND year = (SELECT MAX(year) FROM oecd_rio_markers WHERE iso_code = ?)
            GROUP BY marker
        """, (iso_code, iso_code)).fetchall()

        # Yearly trend
        yearly = conn.execute("""
            SELECT year, marker, SUM(value_usd) as total
            FROM oecd_rio_markers
            WHERE iso_code = ?
            GROUP BY year, marker
            ORDER BY year
        """, (iso_code,)).fetchall()

        # Latest year
        max_year = conn.execute(
            "SELECT MAX(year) FROM oecd_rio_markers WHERE iso_code = ?",
            (iso_code,)
        ).fetchone()[0]

        # Total across all years
        grand_total = conn.execute(
            "SELECT SUM(value_usd) FROM oecd_rio_markers WHERE iso_code = ?",
            (iso_code,)
        ).fetchone()[0]

        conn.close()

        if not latest:
            return None

        result = {
            "latest_year": max_year,
            "mitigation": 0,
            "adaptation": 0,
            "total_latest": 0,
            "grand_total": grand_total or 0,
            "yearly": {},
        }

        for marker, total in latest:
            if marker == "mitigation":
                result["mitigation"] = total
            elif marker == "adaptation":
                result["adaptation"] = total
        result["total_latest"] = result["mitigation"] + result["adaptation"]

        for year, marker, total in yearly:
            if year not in result["yearly"]:
                result["yearly"][year] = {"mitigation": 0, "adaptation": 0}
            result["yearly"][year][marker] = total

        return result

    except Exception:
        return None


def get_all_climate_finance():
    """Returns dict: ISO3 -> total climate finance (latest year)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("""
            SELECT iso_code, SUM(value_usd) as total
            FROM oecd_rio_markers
            WHERE year = (SELECT MAX(year) FROM oecd_rio_markers)
            GROUP BY iso_code
        """).fetchall()
        conn.close()
        return {r[0]: r[1] for r in rows}
    except Exception:
        return {}


def rio_stats():
    """Summary statistics."""
    try:
        conn = sqlite3.connect(DB_PATH)
        countries = conn.execute(
            "SELECT COUNT(DISTINCT iso_code) FROM oecd_rio_markers"
        ).fetchone()[0]
        years = conn.execute(
            "SELECT COUNT(DISTINCT year) FROM oecd_rio_markers"
        ).fetchone()[0]
        total_rows = conn.execute(
            "SELECT COUNT(*) FROM oecd_rio_markers"
        ).fetchone()[0]
        conn.close()
        return {"countries": countries, "years": years, "rows": total_rows}
    except Exception:
        return {}


# ============================================================
# MAIN
# ============================================================

def run_fetch():
    """Full fetch cycle: both markers."""
    logging.info("Fetching OECD Rio Markers...")
    total_stored = 0

    for code, label in MARKERS.items():
        logging.info(f"  Fetching {label} (marker {code})...")
        try:
            results = _fetch_marker(code)
            stored = store_results(results)
            total_stored += stored
            logging.info(f"  {label}: {len(results)} records, {stored} stored")
        except Exception as e:
            logging.error(f"  {label}: ERROR: {e}")

        time.sleep(1)

    logging.info(f"Total stored: {total_stored}")
    return total_stored


if __name__ == "__main__":
    import sys
    if "--fetch" in sys.argv:
        count = run_fetch()
        print(f"\nStored {count} records")
        stats = rio_stats()
        print(f"Countries: {stats.get('countries', 0)}")
        print(f"Years: {stats.get('years', 0)}")
    else:
        stats = rio_stats()
        print(f"OECD Rio Markers module loaded")
        print(f"  Countries: {stats.get('countries', 0)}")
        print(f"  Years: {stats.get('years', 0)}")
        print(f"  Rows: {stats.get('rows', 0)}")
        print(f"  Run with --fetch to pull data")
