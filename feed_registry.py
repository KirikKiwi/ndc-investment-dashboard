# ============================================================
# NDC Investment Dashboard
# feed_registry.py — Source registry for news aggregator
# Maps all 50 curated domains to feed method, tier, metadata
# Sprint 3
# ============================================================

# ============================================================
# SOURCE REGISTRY
# Each entry: domain, method, feed_url/scrape_path, tier, label
#
# method: "rss" = standard RSS/Atom feed
#         "scrape" = HTML page scraper
#
# tier: 1 = Wire services, specialist press
#       2 = Institutional, MDB, multilateral
#       3 = Regional press
#       4 = Niche / low frequency
# ============================================================

SOURCES = [

    # ── TIER 1 — Wire Services / Major Press ─────────────

    {
        "domain"     : "www.reuters.com",
        "label"      : "Reuters",
        "tier"       : 1,
        "method"     : "scrape",
        "scrape_url" : "https://www.reuters.com/business/energy/",
        "category"   : "news",
    },
    {
        "domain"     : "www.reuters.com",
        "label"      : "Reuters Environment",
        "tier"       : 1,
        "method"     : "scrape",
        "scrape_url" : "https://www.reuters.com/business/environment/",
        "category"   : "news",
    },
    {
        "domain"     : "www.bloomberg.com",
        "label"      : "Bloomberg",
        "tier"       : 1,
        "method"     : "scrape",
        "scrape_url" : "https://www.bloomberg.com/green",
        "category"   : "news",
    },
    {
        "domain"     : "about.bnef.com",
        "label"      : "Bloomberg NEF",
        "tier"       : 1,
        "method"     : "scrape",
        "scrape_url" : "https://about.bnef.com/blog/",
        "category"   : "news",
    },
    {
        "domain"     : "www.ft.com",
        "label"      : "Financial Times",
        "tier"       : 1,
        "method"     : "scrape",
        "scrape_url" : "https://www.ft.com/climate-capital",
        "category"   : "news",
    },
    {
        "domain"     : "www.theguardian.com",
        "label"      : "The Guardian",
        "tier"       : 1,
        "method"     : "rss",
        "feed_url"   : "https://www.theguardian.com/environment/rss",
        "category"   : "news",
    },

    # ── TIER 1 — Specialist Climate Press ────────────────

    {
        "domain"     : "www.carbonbrief.org",
        "label"      : "Carbon Brief",
        "tier"       : 1,
        "method"     : "rss",
        "feed_url"   : "https://www.carbonbrief.org/feed",
        "category"   : "news",
    },
    {
        "domain"     : "www.climatechangenews.com",
        "label"      : "Climate Home News",
        "tier"       : 1,
        "method"     : "rss",
        "feed_url"   : "https://www.climatechangenews.com/feed/",
        "category"   : "news",
    },
    {
        "domain"     : "www.businessgreen.com",
        "label"      : "BusinessGreen",
        "tier"       : 1,
        "method"     : "scrape",
        "scrape_url" : "https://www.businessgreen.com/news",
        "category"   : "news",
    },
    {
        "domain"     : "www.devex.com",
        "label"      : "Devex",
        "tier"       : 1,
        "method"     : "scrape",
        "scrape_url" : "https://www.devex.com/news",
        "category"   : "news",
    },

    # ── TIER 1 — Specialist Energy Press ─────────────────

    {
        "domain"     : "www.pv-magazine.com",
        "label"      : "PV Magazine",
        "tier"       : 1,
        "method"     : "rss",
        "feed_url"   : "https://www.pv-magazine.com/feed/",
        "category"   : "news",
    },
    {
        "domain"     : "www.cleanenergywire.org",
        "label"      : "Clean Energy Wire",
        "tier"       : 1,
        "method"     : "rss",
        "feed_url"   : "https://www.cleanenergywire.org/rss.xml",
        "category"   : "news",
    },
    {
        "domain"     : "www.energymonitor.ai",
        "label"      : "Energy Monitor",
        "tier"       : 1,
        "method"     : "scrape",
        "scrape_url" : "https://www.energymonitor.ai/news/",
        "category"   : "news",
    },

    # ── TIER 2 — MDBs ───────────────────────────────────

    {
        "domain"     : "www.worldbank.org",
        "label"      : "World Bank",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.worldbank.org/en/topic/climatechange/news",
        "category"   : "institutional",
    },
    {
        "domain"     : "www.ifc.org",
        "label"      : "IFC",
        "tier"       : 2,
        "method"     : "playwright",
        "scrape_url" : "https://www.ifc.org/en/stories",
        "category"   : "institutional",
    },
    {
        "domain"     : "www.afdb.org",
        "label"      : "African Development Bank",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.afdb.org/en/news-and-events/press-releases",
        "category"   : "institutional",
    },
    {
        "domain"     : "www.adb.org",
        "label"      : "Asian Development Bank",
        "tier"       : 2,
        "method"     : "playwright",
        "scrape_url" : "https://www.adb.org/news",
        "category"   : "institutional",
    },
    {
        "domain"     : "www.iadb.org",
        "label"      : "Inter-American Dev Bank",
        "tier"       : 2,
        "method"     : "playwright",
        "scrape_url" : "https://www.iadb.org/en/news",
        "category"   : "institutional",
    },
    {
        "domain"     : "www.ebrd.com",
        "label"      : "EBRD",
        "tier"       : 2,
        "method"     : "playwright",
        "scrape_url" : "https://www.ebrd.com/news/news.html",
        "category"   : "institutional",
    },
    {
        "domain"     : "www.greenclimate.fund",
        "label"      : "Green Climate Fund",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.greenclimate.fund/news",
        "category"   : "institutional",
    },

    # ── TIER 2 — Climate Funds ───────────────────────────

    {
        "domain"     : "www.thegef.org",
        "label"      : "Global Environment Facility",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.thegef.org/newsroom/news",
        "category"   : "institutional",
    },
    {
        "domain"     : "www.adaptation-fund.org",
        "label"      : "Adaptation Fund",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.adaptation-fund.org/news/",
        "category"   : "institutional",
    },

    # ── TIER 2 — Multilateral Policy ─────────────────────

    {
        "domain"     : "www.iea.org",
        "label"      : "IEA",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.iea.org/news",
        "category"   : "policy",
    },
    {
        "domain"     : "www.irena.org",
        "label"      : "IRENA",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.irena.org/news",
        "category"   : "policy",
    },
    {
        "domain"     : "www.oecd.org",
        "label"      : "OECD",
        "tier"       : 2,
        "method"     : "playwright",
        "scrape_url" : "https://www.oecd.org/en/topics/sub-issues/climate-change-and-environment.html",
        "category"   : "policy",
    },
    {
        "domain"     : "www.undp.org",
        "label"      : "UNDP",
        "tier"       : 2,
        "method"     : "playwright",
        "scrape_url" : "https://www.undp.org/press-releases",
        "category"   : "policy",
    },
    {
        "domain"     : "www.unep.org",
        "label"      : "UNEP",
        "tier"       : 2,
        "method"     : "rss",
        "feed_url"   : "https://www.unep.org/rss.xml",
        "category"   : "policy",
    },
    {
        "domain"     : "www.imf.org",
        "label"      : "IMF",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.imf.org/en/News",
        "category"   : "policy",
    },
    {
        "domain"     : "www.trade.gov",
        "label"      : "US Trade.gov",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.trade.gov/news",
        "category"   : "subsidies",
    },

    # ── TIER 2 — Data / Registry Platforms ───────────────

    {
        "domain"     : "*.unfccc.int",
        "label"      : "UNFCCC",
        "tier"       : 2,
        "method"     : "playwright",
        "scrape_url" : "https://unfccc.int/news",
        "category"   : "policy",
    },
    {
        "domain"     : "*.climatewatchdata.org",
        "label"      : "Climate Watch",
        "tier"       : 2,
        "method"     : "playwright",
        "scrape_url" : "https://www.climatewatchdata.org/blog",
        "category"   : "policy",
    },
    {
        "domain"     : "*.ndcpartnership.org",
        "label"      : "NDC Partnership",
        "tier"       : 2,
        "method"     : "playwright",
        "scrape_url" : "https://ndcpartnership.org/news",
        "category"   : "policy",
    },
    {
        "domain"     : "*.reliefweb.int",
        "label"      : "ReliefWeb",
        "tier"       : 2,
        "method"     : "rss",
        "feed_url"   : "https://reliefweb.int/updates/rss.xml",
        "category"   : "news",
    },
    {
        "domain"     : "*.climatepolicydatabase.org",
        "label"      : "Climate Policy Database",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://climatepolicydatabase.org/policies",
        "category"   : "subsidies",
    },
    {
        "domain"     : "www.climatebonds.net",
        "label"      : "Climate Bonds Initiative",
        "tier"       : 2,
        "method"     : "scrape",
        "scrape_url" : "https://www.climatebonds.net/resources/press-releases",
        "category"   : "news",
    },

    # ── TIER 3 — Sub-Saharan Africa ──────────────────────

    {
        "domain"     : "www.theafricareport.com",
        "label"      : "The Africa Report",
        "tier"       : 3,
        "method"     : "rss",
        "feed_url"   : "https://www.theafricareport.com/feed/",
        "category"   : "news",
    },
    {
        "domain"     : "www.african-business.com",
        "label"      : "African Business",
        "tier"       : 3,
        "method"     : "playwright",
        "scrape_url" : "https://african-business.com/sectors/energy",
        "category"   : "news",
    },
    {
        "domain"     : "www.esi-africa.com",
        "label"      : "ESI Africa",
        "tier"       : 3,
        "method"     : "playwright",
        "scrape_url" : "https://www.esi-africa.com/news/",
        "category"   : "news",
    },

    # ── TIER 3 — North Africa / Middle East ──────────────

    {
        "domain"     : "www.thenationalnews.com",
        "label"      : "The National",
        "tier"       : 3,
        "method"     : "playwright",
        "scrape_url" : "https://www.thenationalnews.com/climate/",
        "category"   : "news",
    },
    {
        "domain"     : "www.zawya.com",
        "label"      : "Zawya",
        "tier"       : 3,
        "method"     : "scrape",
        "scrape_url" : "https://www.zawya.com/en/business/energy",
        "category"   : "news",
    },

    # ── TIER 3 — Latin America / Caribbean ───────────────

    {
        "domain"     : "www.bnamericas.com",
        "label"      : "BNamericas",
        "tier"       : 3,
        "method"     : "scrape",
        "scrape_url" : "https://www.bnamericas.com/en/news/electric-power",
        "category"   : "news",
    },
    {
        "domain"     : "www.dialogochino.net",
        "label"      : "Diálogo Chino",
        "tier"       : 3,
        "method"     : "rss",
        "feed_url"   : "https://dialogochino.net/en/feed/",
        "category"   : "news",
    },
    {
        "domain"     : "www.caribbeanclimate.bz",
        "label"      : "Caribbean Climate",
        "tier"       : 3,
        "method"     : "playwright",
        "scrape_url" : "https://www.caribbeanclimate.bz/blog/",
        "category"   : "policy",
    },

    # ── TIER 3 — South Asia ──────────────────────────────

    {
        "domain"     : "www.livemint.com",
        "label"      : "Livemint",
        "tier"       : 3,
        "method"     : "rss",
        "feed_url"   : "https://www.livemint.com/rss/industry",
        "category"   : "news",
    },
    {
        "domain"     : "www.thethirdpole.net",
        "label"      : "The Third Pole",
        "tier"       : 3,
        "method"     : "rss",
        "feed_url"   : "https://www.thethirdpole.net/feed/",
        "category"   : "news",
    },

    # ── TIER 3 — Southeast / East Asia ───────────────────

    {
        "domain"     : "asia.nikkei.com",
        "label"      : "Nikkei Asia",
        "tier"       : 3,
        "method"     : "scrape",
        "scrape_url" : "https://asia.nikkei.com/Spotlight/Environment",
        "category"   : "news",
    },
    {
        "domain"     : "www.eco-business.com",
        "label"      : "Eco-Business",
        "tier"       : 3,
        "method"     : "scrape",
        "scrape_url" : "https://www.eco-business.com/news/",
        "category"   : "news",
    },
    {
        "domain"     : "www.chinadialogue.net",
        "label"      : "China Dialogue",
        "tier"       : 3,
        "method"     : "rss",
        "feed_url"   : "https://www.chinadialogue.net/feed/",
        "category"   : "news",
    },

    # ── TIER 3 — Central Asia / Caucasus ─────────────────

    {
        "domain"     : "eurasianet.org",
        "label"      : "Eurasianet",
        "tier"       : 3,
        "method"     : "playwright",
        "scrape_url" : "https://eurasianet.org/region/central-asia",
        "category"   : "news",
    },

    # ── TIER 3 — Eastern Europe / Balkans ────────────────

    {
        "domain"     : "balkangreenenergynews.com",
        "label"      : "Balkan Green Energy News",
        "tier"       : 3,
        "method"     : "scrape",
        "scrape_url" : "https://balkangreenenergynews.com/",
        "category"   : "news",
    },

    # ── TIER 3 — Pacific Islands ─────────────────────────

    {
        "domain"     : "www.pina.com.fj",
        "label"      : "Pacific Islands News",
        "tier"       : 3,
        "method"     : "playwright",
        "scrape_url" : "https://www.pina.com.fj/",
        "category"   : "news",
    },
]


# ============================================================
# HELPER LOOKUPS
# ============================================================

def get_source_by_domain(domain):
    """Returns source entry for a domain."""
    for s in SOURCES:
        if s["domain"] == domain:
            return s
    return None

def get_rss_sources():
    """Returns all sources using RSS method."""
    return [s for s in SOURCES if s["method"] == "rss"]

def get_scrape_sources():
    """Returns all sources using scrape method."""
    return [s for s in SOURCES if s["method"] == "scrape"]

def get_sources_by_tier(tier):
    """Returns all sources at a given tier."""
    return [s for s in SOURCES if s["tier"] == tier]


# ============================================================
# CREDIBILITY SCORING
# ============================================================

TIER_BASE_SCORES = {1: 95, 2: 85, 3: 75, 4: 65}

def credibility_score(tier, days_old):
    """
    Computes credibility score from source tier and article age.
    Range: roughly 55-100.
    """
    base = TIER_BASE_SCORES.get(tier, 65)

    if days_old < 30:
        bonus = 5
    elif days_old < 90:
        bonus = 3
    elif days_old < 180:
        bonus = 0
    elif days_old < 365:
        bonus = -3
    else:
        bonus = -10

    return max(0, min(100, base + bonus))


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    rss     = get_rss_sources()
    scrape  = get_scrape_sources()
    t1      = get_sources_by_tier(1)
    t2      = get_sources_by_tier(2)
    t3      = get_sources_by_tier(3)

    print("Feed Registry loaded")
    print(f"  Total sources : {len(SOURCES)}")
    print(f"  RSS feeds     : {len(rss)}")
    print(f"  Scrape targets: {len(scrape)}")
    print(f"  Tier 1        : {len(t1)}")
    print(f"  Tier 2        : {len(t2)}")
    print(f"  Tier 3        : {len(t3)}")
    print()
    print("  Scoring examples:")
    print(f"    Tier 1, 7 days old  : {credibility_score(1, 7)}")
    print(f"    Tier 2, 45 days old : {credibility_score(2, 45)}")
    print(f"    Tier 3, 200 days old: {credibility_score(3, 200)}")
    print(f"    Tier 1, 400 days old: {credibility_score(1, 400)}")
