# ============================================================
# NDC Investment Dashboard
# classifier.py — Country and sector tagging for news articles
# Sprint 3
# ============================================================

import os
import re
import sqlite3
import logging
import pycountry

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "database", "ndc_dashboard.db"
)


# ============================================================
# COUNTRY NAME VARIANTS
# Maps ISO alpha-3 to a list of name strings to search for.
# Includes official name, common name, and known variants.
# ============================================================

def _build_country_lookup():
    """
    Builds a dict: ISO3 -> list of searchable name variants.
    Uses pycountry plus manual additions for common variants.
    """
    lookup = {}

    for c in pycountry.countries:
        iso3  = c.alpha_3
        names = set()

        names.add(c.name)
        if hasattr(c, "common_name"):
            names.add(c.common_name)
        if hasattr(c, "official_name"):
            names.add(c.official_name)

        lookup[iso3] = names

    # ── Manual variants for countries with common alternate names
    variants = {
        "USA": ["United States", "US", "U.S.", "America"],
        "GBR": ["United Kingdom", "UK", "U.K.", "Britain"],
        "ARE": ["UAE", "U.A.E.", "United Arab Emirates"],
        "KOR": ["South Korea"],
        "PRK": ["North Korea"],
        "CIV": ["Ivory Coast", "Côte d'Ivoire", "Cote d'Ivoire"],
        "COD": ["DRC", "DR Congo", "Democratic Republic of Congo",
                 "Congo-Kinshasa"],
        "COG": ["Republic of Congo", "Congo-Brazzaville"],
        "TZA": ["Tanzania"],
        "VNM": ["Vietnam", "Viet Nam"],
        "IRN": ["Iran"],
        "SYR": ["Syria"],
        "LAO": ["Laos"],
        "RUS": ["Russia"],
        "VEN": ["Venezuela"],
        "BOL": ["Bolivia"],
        "MDA": ["Moldova"],
        "PSE": ["Palestine", "Palestinian"],
        "TWN": ["Taiwan"],
        "HKG": ["Hong Kong"],
        "MAC": ["Macau", "Macao"],
        "BRN": ["Brunei"],
        "FSM": ["Micronesia"],
        "STP": ["São Tomé", "Sao Tome"],
        "TLS": ["Timor-Leste", "East Timor"],
        "SWZ": ["Eswatini", "Swaziland"],
        "MKD": ["North Macedonia", "Macedonia"],
        "CZE": ["Czech Republic", "Czechia"],
        "MMR": ["Myanmar", "Burma"],
        "CPV": ["Cape Verde", "Cabo Verde"],
    }

    for iso3, names_list in variants.items():
        if iso3 in lookup:
            lookup[iso3].update(names_list)
        else:
            lookup[iso3] = set(names_list)

    # Convert sets to sorted lists (longest first for greedy matching)
    for iso3 in lookup:
        lookup[iso3] = sorted(lookup[iso3], key=len, reverse=True)

    return lookup

COUNTRY_LOOKUP = _build_country_lookup()

# Short names that could cause false positives — require word boundaries
SHORT_NAMES = {"US", "UK", "EU", "UAE", "DRC", "CAR"}


# ============================================================
# SECTOR KEYWORDS
# Aligned with the dashboard's 7-sector taxonomy.
# Keywords grouped by sector for matching against article text.
# ============================================================

SECTOR_KEYWORDS = {
    "Energy": [
        "solar", "wind power", "wind energy", "wind farm",
        "renewable energy", "renewables", "clean energy",
        "hydropower", "geothermal", "biomass energy",
        "energy transition", "power generation", "electricity",
        "grid", "energy storage", "battery", "hydrogen",
        "photovoltaic", "offshore wind", "onshore wind",
        "energy access", "mini-grid", "microgrid",
        "power plant", "energy efficiency", "decarbonisation",
        "decarbonization", "fossil fuel", "coal phase",
        "natural gas", "LNG", "energy security",
        "power purchase agreement", "PPA", "feed-in tariff",
        "net metering", "IPP", "independent power producer",
    ],
    "Transport": [
        "electric vehicle", "EV", "e-mobility",
        "public transport", "transportation", "railway",
        "rail transport", "bus rapid transit",
        "BRT", "urban mobility", "sustainable transport",
        "aviation", "shipping", "maritime", "seaport",
        "electric bus", "charging infrastructure",
        "low-carbon transport", "freight", "logistics",
        "vehicle emission", "fuel efficiency",
        "road transport", "highway", "expressway",
    ],
    "Land, Agriculture & Forestry": [
        "agriculture", "farming", "crop", "livestock",
        "forestry", "deforestation", "reforestation",
        "agroforestry", "land use", "REDD",
        "food security", "soil", "irrigation",
        "sustainable agriculture", "climate-smart agriculture",
        "afforestation", "land degradation",
        "palm oil", "cocoa", "coffee", "rice",
        "smallholder", "pastoral", "rangeland",
    ],
    "Water & Blue Economy": [
        "water supply", "water management", "sanitation",
        "water scarcity", "desalination", "flood",
        "drought", "water infrastructure", "WASH",
        "ocean", "marine", "coastal", "fisheries",
        "blue economy", "blue carbon", "mangrove",
        "coral reef", "sea level", "tidal",
        "watershed", "river basin", "aquifer",
    ],
    "Built Environment & Waste": [
        "building", "construction", "green building",
        "waste management", "recycling", "circular economy",
        "urban planning", "smart city", "housing",
        "cooling", "heating", "HVAC", "insulation",
        "cement", "steel", "waste-to-energy",
        "landfill", "plastic", "municipal waste",
    ],
    "Industry & Heavy Sector": [
        "industrial", "manufacturing", "heavy industry",
        "mining", "smelting", "refining",
        "petrochemical", "chemical", "aluminium",
        "steel production", "iron", "copper",
        "industrial decarbonisation", "carbon capture",
        "CCS", "CCUS", "process emission",
    ],
    "Nature-Based Solutions": [
        "nature-based", "NbS", "biodiversity",
        "conservation", "ecosystem", "wetland",
        "protected area", "wildlife", "habitat",
        "natural capital", "carbon sink",
        "peatland", "grassland", "savanna",
        "environmental protection", "restoration",
    ],
}


# ============================================================
# MATCHING ENGINE
# ============================================================

def _match_countries(text):
    """
    Returns list of ISO3 codes found in text.
    Uses word boundary matching for short names to avoid
    false positives (e.g. "US" inside "industrial").
    """
    if not text:
        return []

    found = set()
    text_lower = text.lower()
    text_original = text  # preserve case for short-name matching

    for iso3, names in COUNTRY_LOOKUP.items():
        for name in names:
            if len(name) <= 3 and name.upper() in SHORT_NAMES:
                # Word boundary match for short names
                pattern = r'\b' + re.escape(name) + r'\b'
                if re.search(pattern, text_original):
                    found.add(iso3)
                    break
            else:
                if name.lower() in text_lower:
                    found.add(iso3)
                    break

    return sorted(found)


def _match_sectors(text):
    """
    Returns list of sector names found in text.
    Matches any keyword from the sector keyword list.
    """
    if not text:
        return []

    found = set()
    text_lower = text.lower()

    for sector, keywords in SECTOR_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                found.add(sector)
                break

    return sorted(found)


def classify_article(title, summary=""):
    """
    Returns (countries, sectors) for a single article.
    Both are lists of strings.
    """
    text = f"{title} {summary}"
    countries = _match_countries(text)
    sectors   = _match_sectors(text)
    return countries, sectors


# ============================================================
# BATCH CLASSIFIER
# ============================================================

def classify_all(force=False):
    """
    Classifies all articles in the news_feed table.
    By default only processes untagged articles (countries='').
    Set force=True to reclassify everything.

    Returns dict with counts.
    """
    conn = sqlite3.connect(DB_PATH)

    if force:
        rows = conn.execute(
            "SELECT article_id, title, summary FROM news_feed"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT article_id, title, summary FROM news_feed "
            "WHERE countries = '' AND sectors = ''"
        ).fetchall()

    tagged_country = 0
    tagged_sector  = 0
    total = len(rows)

    for article_id, title, summary in rows:
        countries, sectors = classify_article(title, summary or "")

        country_str = ",".join(countries)
        sector_str  = ",".join(sectors)

        if countries:
            tagged_country += 1
        if sectors:
            tagged_sector += 1

        conn.execute(
            "UPDATE news_feed SET countries = ?, sectors = ? "
            "WHERE article_id = ?",
            (country_str, sector_str, article_id)
        )

    conn.commit()
    conn.close()

    result = {
        "total_processed"  : total,
        "tagged_country"   : tagged_country,
        "tagged_sector"    : tagged_sector,
        "untagged"         : total - tagged_country,
    }

    logging.info(
        f"Classification complete: {total} articles, "
        f"{tagged_country} with country, {tagged_sector} with sector, "
        f"{total - tagged_country} untagged"
    )

    return result


# ============================================================
# DIAGNOSTICS
# ============================================================

def classification_report():
    """Returns summary stats on tagged articles."""
    try:
        conn = sqlite3.connect(DB_PATH)
        total = conn.execute(
            "SELECT COUNT(*) FROM news_feed"
        ).fetchone()[0]
        with_country = conn.execute(
            "SELECT COUNT(*) FROM news_feed WHERE countries != ''"
        ).fetchone()[0]
        with_sector = conn.execute(
            "SELECT COUNT(*) FROM news_feed WHERE sectors != ''"
        ).fetchone()[0]
        with_both = conn.execute(
            "SELECT COUNT(*) FROM news_feed "
            "WHERE countries != '' AND sectors != ''"
        ).fetchone()[0]

        # Top countries
        rows = conn.execute("""
            SELECT countries, COUNT(*) as cnt
            FROM news_feed WHERE countries != ''
            GROUP BY countries ORDER BY cnt DESC LIMIT 10
        """).fetchall()

        # Top sectors
        sector_rows = conn.execute("""
            SELECT sectors, COUNT(*) as cnt
            FROM news_feed WHERE sectors != ''
            GROUP BY sectors ORDER BY cnt DESC LIMIT 7
        """).fetchall()

        conn.close()

        return {
            "total"          : total,
            "with_country"   : with_country,
            "with_sector"    : with_sector,
            "with_both"      : with_both,
            "top_countries"  : rows,
            "top_sectors"    : sector_rows,
        }
    except Exception:
        return {}


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    print("Classifier module loaded")
    print(f"  Country variants: {len(COUNTRY_LOOKUP)}")
    print(f"  Sector categories: {len(SECTOR_KEYWORDS)}")

    # Test classification
    test_cases = [
        ("Kenya launches $1.5bn solar energy programme", ""),
        ("India wind farm expansion faces regulatory hurdles", "The Maharashtra government announced new permitting requirements"),
        ("Global deforestation rates decline", "REDD+ programme shows results in Brazil and Indonesia"),
        ("EU carbon border tax takes effect", "The CBAM regulation impacts steel and cement imports"),
    ]
    print("\n  Test cases:")
    for title, summary in test_cases:
        countries, sectors = classify_article(title, summary)
        print(f"    '{title[:50]}...'")
        print(f"      Countries: {countries}")
        print(f"      Sectors:   {sectors}")

    import sys
    if "--run" in sys.argv:
        result = classify_all()
        print(f"\n  Results: {result}")
        report = classification_report()
        print(f"\n  Report:")
        for k, v in report.items():
            print(f"    {k}: {v}")
