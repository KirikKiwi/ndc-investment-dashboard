# ============================================================
# NDC Investment Dashboard
# data.py — Database queries and data preparation
# ============================================================

import sqlite3
import pandas as pd
import os
import json
import re

DB_PATH = os.path.join(
    os.path.expanduser("~"),
    "Documents", "ndc_dashboard",
    "data", "database", "ndc_dashboard.db"
)

# ============================================================
# COUNTRY NAME LOOKUP
# Simplified display names overriding verbose UN official names
# ============================================================

COUNTRY_NAMES = {
    "ARE": "United Arab Emirates",
    "BOL": "Bolivia",
    "CAF": "Central African Republic",
    "COD": "DR Congo",
    "DOM": "Dominican Republic",
    "FSM": "Micronesia",
    "GBR": "United Kingdom",
    "IRN": "Iran",
    "KOR": "South Korea",
    "LAO": "Laos",
    "MDA": "Moldova",
    "PRK": "North Korea",
    "PSE": "Palestine",
    "RUS": "Russia",
    "SYR": "Syria",
    "TZA": "Tanzania",
    "USA": "United States",
    "VCT": "Saint Vincent and the Grenadines",
    "VEN": "Venezuela",
}


def get_country_name(iso_code):
    """
    Returns a clean display name for a country ISO code.
    Uses simplified names where official UN names are verbose.
    Falls back to pycountry then raw ISO code.
    """
    if iso_code in COUNTRY_NAMES:
        return COUNTRY_NAMES[iso_code]
    try:
        import pycountry
        return pycountry.countries.get(alpha_3=iso_code).name
    except Exception:
        return iso_code


# ============================================================
# NDC TEXT CLEANER
# Applied to all country summaries before display
# Covers 59 countries with HTML, email and entity issues
# ============================================================

def clean_ndc_text(text, max_length=500):
    """
    Cleans NDC summary text for dashboard display.
    Removes HTML tags, WRI disclaimers, email addresses,
    HTML entities and normalises whitespace.
    """
    if not isinstance(text, str) or not text.strip():
        return "No summary available."

    # Handle Libya no-submission case
    if text.strip().lower() in [
        "no document submitted",
        "no document submitted.",
        "no ndc submitted",
    ]:
        return "No NDC document has been submitted for this country."

    # Remove WRI translation disclaimers
    disclaimer_patterns = [
        r'Please note that the NDC was submitted only in [^\.]+\.\s*',
        r'Please note that the INDC was submitted only in [^\.]+\.\s*',
        r'WRI did its best to translate the NDC language\.\s*',
        r'WRI did its best to translate the INDC language\.\s*',
        r'If any errors are identified,?\s*please contact\s*'
        r'us?\s*at\s*\S+\.\s*',
        r'If any errors are identified[^\.]+\.\s*',
        r'please contact\s+us\s+at\s+\S+@\S+\s*',
    ]
    for pattern in disclaimer_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', '', text)

    # Remove URLs and domain fragments
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)

    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', ' ', text)

    # Decode named HTML entities
    entities = {
        '&nbsp;'   : ' ',   '&amp;'    : '&',
        '&lt;'     : '<',   '&gt;'     : '>',
        '&quot;'   : '"',   '&#39;'    : "'",
        '&rsquo;'  : "'",   '&lsquo;'  : "'",
        '&rdquo;'  : '"',   '&ldquo;'  : '"',
        '&ndash;'  : '-',   '&mdash;'  : '-',
        '&hellip;' : '...',  '\u00a0'  : ' ',
        '&eacute;' : 'e',   '&agrave;' : 'a',
        '&egrave;' : 'e',   '&ccedil;' : 'c',
        '&ocirc;'  : 'o',   '&acirc;'  : 'a',
        '&icirc;'  : 'i',   '&ucirc;'  : 'u',
        '&laquo;'  : '"',   '&raquo;'  : '"',
    }
    for entity, replacement in entities.items():
        clean = clean.replace(entity, replacement)

    # Remove any remaining HTML entity patterns
    clean = re.sub(r'&[a-zA-Z]+;', ' ', clean)
    clean = re.sub(r'&#\d+;', ' ', clean)

    # Normalise whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()

    # Remove leading punctuation and quote marks
    clean = clean.lstrip('"\'.,; ')

    # Trim to max length at a sentence boundary
    if len(clean) > max_length:
        trimmed   = clean[:max_length]
        last_stop = trimmed.rfind('.')
        if last_stop > max_length * 0.6:
            clean = trimmed[:last_stop + 1]
        else:
            clean = trimmed.rstrip()

    return clean.strip()


# ============================================================
# CORE QUERY FUNCTION
# ============================================================

def query(sql, params=None):
    """Runs a SQL query and returns a pandas dataframe."""
    conn   = sqlite3.connect(DB_PATH)
    result = pd.read_sql(sql, conn, params=params)
    conn.close()
    return result


# ============================================================
# MASTER DATA LOADS
# Called once at app startup
# ============================================================

def load_master():
    return query("SELECT * FROM master_countries")


def load_tags():
    return query("SELECT * FROM ndc_sector_tags")


def load_projects():
    return query("SELECT * FROM mdb_projects")


# ============================================================
# MAP DATA PREPARATION
# ============================================================

def prepare_map_data(master_df, tags_df):
    """
    Enriches master dataframe for map rendering.
    Adds tier scores, sector counts and hover text.
    """
    df = master_df.copy()

    tier_score = {
        "Tier 1 — Established markets" : 3,
        "Tier 2 — Emerging markets"    : 2,
        "Tier 3 — Frontier markets"    : 1,
        "Insufficient data"            : 0,
    }
    df["tier_score"] = df["investment_tier"].map(
        tier_score
    ).fillna(0)

    sector_counts = (
        tags_df.groupby("iso_code")["sector"]
        .nunique()
        .reset_index()
        .rename(columns={"sector": "sector_count"})
    )
    df = df.merge(sector_counts, on="iso_code", how="left")
    df["sector_count"] = df["sector_count"].fillna(0).astype(int)

    conditional_counts = (
        tags_df[tags_df["commitment_type"] == "Conditional"]
        .groupby("iso_code").size()
        .reset_index()
        .rename(columns={0: "conditional_count"})
    )
    df = df.merge(conditional_counts, on="iso_code", how="left")
    df["conditional_count"] = (
        df["conditional_count"].fillna(0).astype(int)
    )

    def fmt_gdp(v):
        if pd.isna(v): return "N/A"
        if v >= 1e12:  return f"${v/1e12:.1f}T"
        if v >= 1e9:   return f"${v/1e9:.1f}B"
        return f"${v/1e6:.0f}M"

    def fmt_pop(v):
        if pd.isna(v): return "N/A"
        if v >= 1e9:   return f"{v/1e9:.2f}B"
        if v >= 1e6:   return f"{v/1e6:.1f}M"
        return f"{v/1e3:.0f}K"

    df["gdp_display"] = df["gdp_usd"].apply(fmt_gdp)
    df["pop_display"] = df["population"].apply(fmt_pop)

    def make_hover(r):
        ndgain    = (
            f"{r['ndgain_score']:.1f}"
            if pd.notna(r.get("ndgain_score")) else "N/A"
        )
        renewable = (
            f"{r['renewable_electricity_pct']:.0f}%"
            if pd.notna(r.get("renewable_electricity_pct"))
            else "N/A"
        )
        name = get_country_name(r["iso_code"])
        return (
            f"<b>{name}</b><br>"
            f"Tier: {r['investment_tier']}<br>"
            f"Sectors: {r['sector_count']} identified<br>"
            f"Conditional signals: {r['conditional_count']}<br>"
            f"GDP: {r['gdp_display']}<br>"
            f"Population: {r['pop_display']}<br>"
            f"ND-GAIN: {ndgain}<br>"
            f"Renewables: {renewable}"
        )

    df["hover_text"] = df.apply(make_hover, axis=1)
    return df


# ============================================================
# COUNTRY DETAIL
# Called when a country is clicked on the map
# ============================================================

def get_country_detail(iso_code, master_df, tags_df):
    """
    Returns all data for a single country.
    Used to populate the country slide panel.
    """
    country = master_df[master_df["iso_code"] == iso_code]
    if country.empty:
        return None, None
    country_data = country.iloc[0].to_dict()
    country_tags = tags_df[tags_df["iso_code"] == iso_code]
    return country_data, country_tags


# ============================================================
# GLOBAL KPIs
# ============================================================

def get_global_kpis(master_df, tags_df):
    """Calculates global summary statistics for KPI strip."""
    return {
        "total_countries"       : len(master_df),
        "conditional_countries" : int(
            tags_df[
                tags_df["commitment_type"] == "Conditional"
            ]["iso_code"].nunique()
        ),
        "total_projects"        : int(
            master_df["wb_project_count"].fillna(0).sum()
        ),
        "avg_ndgain"            : round(
            float(master_df["ndgain_score"].mean()), 1
        ),
        "total_tags"            : len(tags_df),
        "avg_renewable"         : round(
            float(master_df["renewable_electricity_pct"].mean()), 1
        ),
        "tier1_count"           : int(
            (master_df["investment_tier"] ==
             "Tier 1 — Established markets").sum()
        ),
        "tier2_count"           : int(
            (master_df["investment_tier"] ==
             "Tier 2 — Emerging markets").sum()
        ),
        "tier3_count"           : int(
            (master_df["investment_tier"] ==
             "Tier 3 — Frontier markets").sum()
        ),
    }


# ============================================================
# SECTOR ANALYTICS
# ============================================================

def get_sector_summary(tags_df):
    """Returns sector coverage summary for charts."""
    return (
        tags_df.groupby("sector")
        .agg(
            country_count = ("iso_code", "nunique"),
            high_conf     = (
                "confidence",
                lambda x: (x == "High").sum()
            ),
            conditional   = (
                "commitment_type",
                lambda x: (x == "Conditional").sum()
            ),
        )
        .reset_index()
        .sort_values("country_count", ascending=True)
    )


def get_country_sectors(iso_code, tags_df):
    """Returns sector tags for a specific country."""
    return tags_df[tags_df["iso_code"] == iso_code].copy()


def get_country_projects(iso_code, projects_df):
    """Returns World Bank projects for a specific country."""

    def extract_name(val):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return parsed[0] if parsed else None
            return val
        except Exception:
            return val

    import pycountry

    def to_iso(name):
        try:
            return pycountry.countries.search_fuzzy(
                name
            )[0].alpha_3
        except Exception:
            return None

    df = projects_df.copy()
    df["country_clean"] = df["country_name"].apply(extract_name)
    df["iso_code"]      = df["country_clean"].apply(to_iso)

    return df[df["iso_code"] == iso_code].copy()


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    master   = load_master()
    tags     = load_tags()
    projects = load_projects()
    kpis     = get_global_kpis(master, tags)

    print("✅ data.py verification:")
    print(f"   Countries        : {len(master)}")
    print(f"   Tags             : {len(tags)}")
    print(f"   Projects         : {len(projects)}")
    print(f"   clean_ndc_text   : available")
    print(f"   get_country_name : available")

    print(f"\n   Name lookup test:")
    for iso in ["BOL", "VEN", "RUS", "KOR", "PRK", "GBR", "USA"]:
        print(f"   {iso}: {get_country_name(iso)}")

    print(f"\n   Cleaner test:")
    conn = sqlite3.connect(DB_PATH)
    test = pd.read_sql("""
        SELECT iso_code, value FROM ndc_indicators
        WHERE indicator_slug = 'indc_summary'
        AND iso_code IN ('DZA','BOL','CMR','LBY','GBR')
    """, conn)
    conn.close()

    for _, row in test.iterrows():
        cleaned = clean_ndc_text(row["value"])
        print(f"   {row['iso_code']}: {cleaned[:120]}")