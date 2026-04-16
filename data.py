# ============================================================
# NDC Investment Dashboard
# data.py — Database queries and data preparation
# ============================================================

import sqlite3
import pandas as pd
import os
import json

DB_PATH = os.path.join(
    os.path.expanduser("~"),
    "Documents", "ndc_dashboard",
    "data", "database", "ndc_dashboard.db"
)

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
    df = master_df.copy()

    tier_score = {
        "Tier 1 — Established markets" : 3,
        "Tier 2 — Emerging markets"    : 2,
        "Tier 3 — Frontier markets"    : 1,
        "Insufficient data"            : 0,
    }
    df["tier_score"] = df["investment_tier"].map(tier_score).fillna(0)

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
    df["conditional_count"] = df["conditional_count"].fillna(0).astype(int)

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
        ndgain = (f"{r['ndgain_score']:.1f}"
                  if pd.notna(r.get("ndgain_score")) else "N/A")
        renewable = (f"{r['renewable_electricity_pct']:.0f}%"
                     if pd.notna(r.get("renewable_electricity_pct"))
                     else "N/A")
        return (
            f"<b>{r['iso_code']}</b><br>"
            f"─────────────────<br>"
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
# ============================================================

def get_country_detail(iso_code, master_df, tags_df):
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
    return {
        "total_countries"       : len(master_df),
        "conditional_countries" : int(tags_df[
            tags_df["commitment_type"] == "Conditional"
        ]["iso_code"].nunique()),
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
        "tier1_count"           : int((
            master_df["investment_tier"] ==
            "Tier 1 — Established markets"
        ).sum()),
        "tier2_count"           : int((
            master_df["investment_tier"] ==
            "Tier 2 — Emerging markets"
        ).sum()),
        "tier3_count"           : int((
            master_df["investment_tier"] ==
            "Tier 3 — Frontier markets"
        ).sum()),
    }

# ============================================================
# SECTOR ANALYTICS
# ============================================================

def get_sector_summary(tags_df):
    return (
        tags_df.groupby("sector")
        .agg(
            country_count = ("iso_code", "nunique"),
            high_conf     = ("confidence",
                             lambda x: (x == "High").sum()),
            conditional   = ("commitment_type",
                             lambda x: (x == "Conditional").sum()),
        )
        .reset_index()
        .sort_values("country_count", ascending=True)
    )

def get_country_sectors(iso_code, tags_df):
    return tags_df[tags_df["iso_code"] == iso_code].copy()

def get_country_projects(iso_code, projects_df):
    def extract_iso(val):
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
            return pycountry.countries.search_fuzzy(name)[0].alpha_3
        except Exception:
            return None

    projects_df         = projects_df.copy()
    projects_df["country_clean"] = projects_df["country_name"].apply(extract_iso)
    projects_df["iso_code"]      = projects_df["country_clean"].apply(to_iso)

    return projects_df[projects_df["iso_code"] == iso_code].copy()

# ============================================================
# VERIFY ON IMPORT
# ============================================================

if __name__ == "__main__":
    master   = load_master()
    tags     = load_tags()
    projects = load_projects()
    kpis     = get_global_kpis(master, tags)

    print("✅ data.py verification:")
    print(f"   Countries : {len(master)}")
    print(f"   Tags      : {len(tags)}")
    print(f"   Projects  : {len(projects)}")
    print(f"   KPIs      : {kpis}")