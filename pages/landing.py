# ============================================================
# NDC Investment Dashboard
# pages/landing.py: Introductory landing page
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import html, dcc
import dash_bootstrap_components as dbc
from components import C, T

# ============================================================
# CONTENT DEFINITIONS
# ============================================================

USE_CASES = [
    {
        "icon"  : "◈",
        "title" : "Investment & Finance",
        "text"  : (
            "Identify conditional finance signals and sector-level "
            "investment opportunities across 198 countries."
        ),
        "colour": C["emerald"],
    },
    {
        "icon"  : "◉",
        "title" : "Policy Research",
        "text"  : (
            "Analyse NDC commitments, track ambition levels and "
            "compare mitigation targets across jurisdictions."
        ),
        "colour": C["cobalt"],
    },
    {
        "icon"  : "◎",
        "title" : "Climate Intelligence",
        "text"  : (
            "Cross-reference vulnerability scores, renewable energy "
            "data and MDB project pipelines in one view."
        ),
        "colour": C["amber"],
    },
    {
        "icon"  : "◐",
        "title" : "Education & Training",
        "text"  : (
            "Explore how countries are responding to climate "
            "commitments with structured, sourced data."
        ),
        "colour": C["industry"],
    },
]

STATS = [
    {"value": "198",  "label": "Countries"},
    {"value": "671",  "label": "NDC Indicators"},
    {"value": "7",    "label": "Investment Sectors"},
    {"value": "500+", "label": "MDB Projects"},
]

SOURCES = [
    "UNFCCC", "Climate Watch", "World Bank",
    "ND-GAIN", "IRENA", "Our World in Data"
]

TERMINOLOGY = [
    {
        "term"      : "NDC",
        "full"      : "Nationally Determined Contribution",
        "definition": (
            "A country's formal climate commitment submitted to the UN "
            "under the Paris Agreement. NDCs outline what each country "
            "intends to do to reduce emissions and adapt to climate "
            "change. This tool analyses the investment signals embedded "
            "within those commitments."
        ),
        "colour"    : C["emerald"],
    },
    {
        "term"      : "Conditional vs Unconditional",
        "full"      : "Commitment Type",
        "definition": (
            "An unconditional commitment is what a country will deliver "
            "using its own resources. A conditional commitment is what "
            "it could additionally achieve with international finance or "
            "technology support. Conditional commitments are the primary "
            "signal of external capital need."
        ),
        "colour"    : C["crimson"],
    },
    {
        "term"      : "Investment Tier",
        "full"      : "Market Classification",
        "definition": (
            "A screening classification derived from ND-GAIN readiness "
            "and GDP per capita. Tier 1 indicates established markets. "
            "Tier 2 indicates emerging markets with growing climate "
            "finance activity. Tier 3 indicates frontier markets with "
            "high conditional finance need and elevated risk profiles."
        ),
        "calc"      : (
            "Tier 1: ND-GAIN readiness above 0.5 and GDP per capita "
            "above $5,000. Tier 2: readiness above 0.35. "
            "Tier 3: all remaining markets."
        ),
        "colour"    : C["amber"],
    },
    {
        "term"      : "Composite Benchmark",
        "full"      : "Country Investment Score",
        "definition": (
            "A weighted composite score that aggregates six "
            "country-level indicators into a single 0-100 investment "
            "readiness metric, used to rank countries within their "
            "tier and identify relative opportunities."
        ),
        "calc"      : (
            "Weights: ND-GAIN Readiness 30%, GDP per capita 25%, "
            "Renewables Share 20%, Climate Vulnerability 15%, "
            "World Bank Project Count 5%, Conditional Finance Uplift 5%. "
            "Each component is normalised before weighting."
        ),
        "colour"    : C["emerald"],
    },
    {
        "term"      : "ND-GAIN Score",
        "full"      : "Notre Dame Global Adaptation Initiative",
        "definition": (
            "Scores countries from 0 to 100 across two dimensions: "
            "vulnerability to climate change and readiness to leverage "
            "investment for adaptation. Higher scores indicate greater "
            "resilience and institutional capacity."
        ),
        "calc"      : (
            "Published annually by the University of Notre Dame. "
            "Vulnerability covers six life-supporting sectors; readiness "
            "covers economic, governance and social components. "
            "This tool uses the combined readiness sub-index."
        ),
        "colour"    : C["cobalt"],
    },
    {
        "term"      : "Governance Score",
        "full"      : "World Bank WGI Composite",
        "definition": (
            "A composite of four World Bank Worldwide Governance "
            "Indicators measuring the quality of institutions and "
            "policy environment. Higher scores reflect stronger "
            "institutional capacity for delivering climate investments."
        ),
        "calc"      : (
            "Average of: Political Stability, Rule of Law, Government "
            "Effectiveness, and Control of Corruption. Native WGI scores "
            "(-2.5 to +2.5) are rescaled to a 0-100 range."
        ),
        "colour"    : C["cobalt"],
    },
    {
        "term"      : "Climate Finance",
        "full"      : "OECD Rio Markers",
        "definition": (
            "Bilateral official development assistance flows tracked "
            "by the OECD and tagged as climate mitigation or adaptation "
            "using the Rio Marker system. Values are the most recent "
            "available year, in USD millions."
        ),
        "calc"      : (
            "Source: OECD DAC Creditor Reporting System, Rio Marker "
            "codes 20 (mitigation) and 30 (adaptation). "
            "Includes both principal and significant marker scores."
        ),
        "colour"    : C["amber"],
    },
    {
        "term"      : "Confidence Score",
        "full"      : "Sector Identification Confidence",
        "definition": (
            "Each sector tag carries a confidence rating. High indicates "
            "two or more direct keyword matches. Medium indicates one "
            "direct or multiple contextual matches. Low indicates the "
            "sector was inferred from surrounding context. Weight "
            "high-confidence tags more heavily in origination decisions."
        ),
        "colour"    : C["industry"],
    },
    {
        "term"      : "Sector Tag",
        "full"      : "Investment Sector Classification",
        "definition": (
            "When an NDC references a specific investment sector such as "
            "Energy, Transport, Land and Agriculture, Water, Built "
            "Environment, Industry or Nature-Based Solutions, the tool "
            "assigns a sector tag. Each tag carries dimension flags "
            "indicating mitigation or adaptation focus and the implied "
            "financing instrument."
        ),
        "colour"    : C["nature"],
    },
    {
        "term"      : "Credibility Tier",
        "full"      : "News Source Classification",
        "definition": (
            "News sources are assigned a credibility tier that "
            "determines how prominently articles are surfaced in "
            "country profiles. Articles from higher-tier sources "
            "are ranked above lower-tier sources of equal recency."
        ),
        "calc"      : (
            "T1: wire services and specialist climate press. "
            "T2: institutional and multilateral publishers. "
            "T3: regional and general press. "
            "Final article score combines source tier and recency."
        ),
        "colour"    : C["crimson"],
    },
]

# ============================================================
# LAYOUT
# ============================================================

def layout():
    return html.Div([

        # ── HERO ─────────────────────────────────────────────
        html.Div([

            # Grid background
            html.Div(style={
                "position"        : "absolute",
                "inset"           : "0",
                "backgroundImage" : (
                    f"linear-gradient(to right, "
                    f"{C['border']}44 1px, transparent 1px), "
                    f"linear-gradient(to bottom, "
                    f"{C['border']}44 1px, transparent 1px)"
                ),
                "backgroundSize"  : "60px 60px",
                "pointerEvents"   : "none",
            }),

            # Hero content
            html.Div([

                # Eyebrow
                html.Div([
                    html.Span("◆ ", style={"color": C["emerald"]}),
                    html.Span(
                        "Green-Gott's Vault · Climate Investment Intelligence",
                        style={
                            **T["label"],
                            "color"        : C["text_muted"],
                            "letterSpacing": "2px"
                        }
                    )
                ], style={"marginBottom": "28px"}),

                # Headline
                html.H1([
                    "Climate Finance",
                    html.Br(),
                    html.Span("Decoded.", style={
                        "color": C["emerald"]
                    })
                ], style={
                    "fontSize"     : "52px",
                    "fontWeight"   : "700",
                    "letterSpacing": "-1px",
                    "lineHeight"   : "1.1",
                    "color"        : C["text"],
                    "fontFamily"   : "Inter, sans-serif",
                    "marginBottom" : "24px",
                }),

                # Subheadline
                html.P(
                    "Every nation has made its climate commitments. "
                    "The real treasure lies in knowing where those "
                    "commitments translate into investable opportunities. "
                    "Green-Gott's Vault maps 198 country profiles, "
                    "connecting NDC policy language to investment signals, "
                    "governance scores and climate finance flows across "
                    "every major economy on earth.",
                    style={
                        "fontSize"     : "15px",
                        "color"        : C["text_secondary"],
                        "maxWidth"     : "520px",
                        "marginBottom" : "40px",
                        "lineHeight"   : "1.7",
                        "fontFamily"   : "Inter, sans-serif",
                    }
                ),

                # CTA
                dcc.Link([
                    html.Button(
                        "Explore the Dashboard  →",
                        style={
                            "backgroundColor" : C["emerald"],
                            "color"           : C["bg"],
                            "border"          : "none",
                            "borderRadius"    : "4px",
                            "padding"         : "14px 32px",
                            "fontSize"        : "14px",
                            "fontWeight"      : "600",
                            "fontFamily"      : "Inter, sans-serif",
                            "cursor"          : "pointer",
                            "letterSpacing"   : "0.3px",
                        }
                    )
                ], href="/dashboard", refresh=False),

                html.Div([
                    html.Span("↓ ", style={"color": C["emerald"]}),
                    html.Span(
                        "or scroll to learn more",
                        style={
                            "fontSize" : "11px",
                            "color"    : C["text_muted"],
                            "fontFamily": "Inter, sans-serif",
                        }
                    )
                ], style={"marginTop": "20px"})

            ], style={
                "position" : "relative",
                "zIndex"   : "1",
                "maxWidth" : "640px",
            })

        ], style={
            "position"        : "relative",
            "backgroundColor" : C["bg"],
            "minHeight"       : "100vh",
            "display"         : "flex",
            "alignItems"      : "center",
            "padding"         : "80px 80px",
            "overflow"        : "hidden",
        }),

        # ── STAT STRIP ───────────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Div(s["value"], style={
                        "fontSize"     : "36px",
                        "fontWeight"   : "700",
                        "color"        : C["emerald"],
                        "fontFamily"   : "Inter, sans-serif",
                        "lineHeight"   : "1",
                        "marginBottom" : "6px"
                    }),
                    html.Div(s["label"], style={
                        "fontSize"      : "11px",
                        "fontWeight"    : "600",
                        "textTransform" : "uppercase",
                        "letterSpacing" : "1.5px",
                        "color"         : C["text_muted"],
                        "fontFamily"    : "Inter, sans-serif",
                    })
                ], style={
                    "textAlign"   : "center",
                    "padding"     : "0 40px",
                    "borderRight" : (
                        f"1px solid {C['border']}"
                        if i < len(STATS) - 1 else "none"
                    )
                })
                for i, s in enumerate(STATS)
            ], style={
                "display"        : "flex",
                "justifyContent" : "center",
                "alignItems"     : "center",
            })
        ], style={
            "backgroundColor" : C["surface"],
            "borderTop"       : f"1px solid {C['border']}",
            "borderBottom"    : f"1px solid {C['border']}",
            "padding"         : "40px 80px",
        }),

        # ── USE CASES ────────────────────────────────────────
        html.Div([

            html.Div(
                "Built for multiple disciplines",
                style={
                    "fontSize"      : "11px",
                    "fontWeight"    : "600",
                    "textTransform" : "uppercase",
                    "letterSpacing" : "1.5px",
                    "color"         : C["text_muted"],
                    "marginBottom"  : "8px",
                    "fontFamily"    : "Inter, sans-serif",
                }
            ),
            html.H2(
                "One tool, many applications",
                style={
                    "fontSize"     : "22px",
                    "fontWeight"   : "600",
                    "color"        : C["text"],
                    "marginBottom" : "40px",
                    "fontFamily"   : "Inter, sans-serif",
                }
            ),

            html.Div([
                html.Div([
                    html.Div(uc["icon"], style={
                        "fontSize"     : "24px",
                        "color"        : uc["colour"],
                        "marginBottom" : "16px"
                    }),
                    html.Div(uc["title"], style={
                        "fontSize"     : "15px",
                        "fontWeight"   : "600",
                        "color"        : C["text"],
                        "marginBottom" : "10px",
                        "fontFamily"   : "Inter, sans-serif",
                    }),
                    html.Div(uc["text"], style={
                        "fontSize"   : "13px",
                        "color"      : C["text_secondary"],
                        "lineHeight" : "1.6",
                        "fontFamily" : "Inter, sans-serif",
                    })
                ], style={
                    "backgroundColor" : C["surface"],
                    "border"          : f"1px solid {C['border']}",
                    "borderTop"       : f"2px solid {uc['colour']}",
                    "borderRadius"    : "6px",
                    "padding"         : "24px",
                    "flex"            : "1",
                    "minWidth"        : "200px",
                })
                for uc in USE_CASES
            ], style={
                "display"  : "flex",
                "gap"      : "16px",
                "flexWrap" : "wrap",
            })

        ], style={
            "backgroundColor" : C["bg"],
            "padding"         : "80px 80px",
        }),

        # ── METHODOLOGY ──────────────────────────────────────
        html.Div([

            html.Div(
                "How this tool works",
                style={
                    "fontSize"      : "11px",
                    "fontWeight"    : "600",
                    "textTransform" : "uppercase",
                    "letterSpacing" : "1.5px",
                    "color"         : C["text_muted"],
                    "marginBottom"  : "8px",
                    "fontFamily"    : "Inter, sans-serif",
                }
            ),
            html.H2(
                "Methodology at a glance",
                style={
                    "fontSize"     : "22px",
                    "fontWeight"   : "600",
                    "color"        : C["text"],
                    "marginBottom" : "40px",
                    "fontFamily"   : "Inter, sans-serif",
                }
            ),

            # Three steps
            html.Div([
                html.Div([
                    html.Div("01", style={
                        "fontSize"     : "11px",
                        "fontWeight"   : "700",
                        "color"        : C["emerald"],
                        "fontFamily"   : "Inter, sans-serif",
                        "marginBottom" : "12px"
                    }),
                    html.Div("NDC Ingestion", style={
                        "fontSize"     : "15px",
                        "fontWeight"   : "600",
                        "color"        : C["text"],
                        "marginBottom" : "8px",
                        "fontFamily"   : "Inter, sans-serif",
                    }),
                    html.Div(
                        "NDC documents from 198 countries are ingested "
                        "via the Climate Watch API, covering 671 "
                        "structured indicators per submission including "
                        "mitigation targets, adaptation measures and "
                        "finance signals.",
                        style={
                            "fontSize"   : "13px",
                            "color"      : C["text_secondary"],
                            "lineHeight" : "1.6",
                            "fontFamily" : "Inter, sans-serif",
                        }
                    )
                ], style={
                    "flex"        : "1",
                    "paddingRight": "40px",
                    "borderRight" : f"1px solid {C['border']}",
                }),

                html.Div([
                    html.Div("02", style={
                        "fontSize"     : "11px",
                        "fontWeight"   : "700",
                        "color"        : C["emerald"],
                        "fontFamily"   : "Inter, sans-serif",
                        "marginBottom" : "12px"
                    }),
                    html.Div("Sector Classification", style={
                        "fontSize"     : "15px",
                        "fontWeight"   : "600",
                        "color"        : C["text"],
                        "marginBottom" : "8px",
                        "fontFamily"   : "Inter, sans-serif",
                    }),
                    html.Div(
                        "A 357-keyword taxonomy maps NDC text to seven "
                        "investment sectors. Each tag carries a "
                        "confidence score based on keyword evidence "
                        "strength. Dimension flags capture mitigation "
                        "vs adaptation, commitment type and financing "
                        "instrument signals.",
                        style={
                            "fontSize"   : "13px",
                            "color"      : C["text_secondary"],
                            "lineHeight" : "1.6",
                            "fontFamily" : "Inter, sans-serif",
                        }
                    )
                ], style={
                    "flex"        : "1",
                    "padding"     : "0 40px",
                    "borderRight" : f"1px solid {C['border']}",
                }),

                html.Div([
                    html.Div("03", style={
                        "fontSize"     : "11px",
                        "fontWeight"   : "700",
                        "color"        : C["emerald"],
                        "fontFamily"   : "Inter, sans-serif",
                        "marginBottom" : "12px"
                    }),
                    html.Div("Data Enrichment", style={
                        "fontSize"     : "15px",
                        "fontWeight"   : "600",
                        "color"        : C["text"],
                        "marginBottom" : "8px",
                        "fontFamily"   : "Inter, sans-serif",
                    }),
                    html.Div(
                        "Country profiles are enriched with World Bank "
                        "economic indicators, ND-GAIN climate "
                        "vulnerability scores, World Bank MDB project "
                        "pipelines and renewable energy policy data "
                        "from Our World in Data.",
                        style={
                            "fontSize"   : "13px",
                            "color"      : C["text_secondary"],
                            "lineHeight" : "1.6",
                            "fontFamily" : "Inter, sans-serif",
                        }
                    )
                ], style={
                    "flex"       : "1",
                    "paddingLeft": "40px",
                }),

            ], style={
                "display"      : "flex",
                "marginBottom" : "60px",
            }),

            # How to use
            html.Div(
                "Using this tool",
                style={
                    "fontSize"      : "11px",
                    "fontWeight"    : "600",
                    "textTransform" : "uppercase",
                    "letterSpacing" : "1.5px",
                    "color"         : C["text_muted"],
                    "marginBottom"  : "8px",
                    "fontFamily"    : "Inter, sans-serif",
                }
            ),
            html.H3(
                "A guide for first-time users",
                style={
                    "fontSize"     : "16px",
                    "fontWeight"   : "600",
                    "color"        : C["text"],
                    "marginBottom" : "20px",
                    "fontFamily"   : "Inter, sans-serif",
                }
            ),

            html.Div([
                html.Div([
                    html.Span(f"{n}  ", style={
                        "color"      : C["emerald"],
                        "fontWeight" : "700",
                        "fontFamily" : "Inter, sans-serif",
                        "fontSize"   : "13px",
                        "flexShrink" : "0",
                    }),
                    html.Span(step, style={
                        "fontSize"   : "13px",
                        "color"      : C["text_secondary"],
                        "lineHeight" : "1.6",
                        "fontFamily" : "Inter, sans-serif",
                    })
                ], style={
                    "display"      : "flex",
                    "alignItems"   : "flex-start",
                    "marginBottom" : "14px" if n < 6 else "0",
                })
for n, step in [
                    (1, "Open the Dashboard and explore the interactive "
                        "globe. Countries are colour-coded by investment "
                        "tier by default. Drag to spin, scroll to zoom."),
                    (2, "Use the View By selector on the left panel to "
                        "switch between Investment Tier, ND-GAIN Score, "
                        "Climate Vulnerability, and Renewables Share "
                        "colour modes."),
                    (3, "Click any country to open its detailed climate "
                        "investment profile. The card shows governance "
                        "scores, climate finance flows, NDC commitments, "
                        "identified sectors and live policy news."),
                    (4, "Inside a country card, click any sector pill to "
                        "open the Sector Deep-Dive panel. This shows "
                        "sector-specific NDC signals, matched World Bank "
                        "projects and recent sector news."),
                    (5, "Scroll below the globe to access the Analytics "
                        "section. Filter by region or country group for "
                        "cross-country comparisons of tier distribution, "
                        "sector coverage and commitment types."),
                    (6, "Use the download tools in the filter bar to "
                        "export filtered country and indicator data "
                        "for offline analysis."),
                ]            ], style={
                "backgroundColor" : C["surface_high"],
                "border"          : f"1px solid {C['border']}",
                "borderLeft"      : f"2px solid {C['emerald']}",
                "borderRadius"    : "4px",
                "padding"         : "20px 24px",
            }),

        ], style={
            "backgroundColor" : C["surface"],
            "borderTop"       : f"1px solid {C['border']}",
            "borderBottom"    : f"1px solid {C['border']}",
            "padding"         : "80px 80px",
        }),

        # ── TERMINOLOGY ──────────────────────────────────────
        html.Div([

            html.Div(
                "Key concepts",
                style={
                    "fontSize"      : "11px",
                    "fontWeight"    : "600",
                    "textTransform" : "uppercase",
                    "letterSpacing" : "1.5px",
                    "color"         : C["text_muted"],
                    "marginBottom"  : "8px",
                    "fontFamily"    : "Inter, sans-serif",
                }
            ),
            html.H2(
                "Terminology guide",
                style={
                    "fontSize"     : "22px",
                    "fontWeight"   : "600",
                    "color"        : C["text"],
                    "marginBottom" : "8px",
                    "fontFamily"   : "Inter, sans-serif",
                }
            ),
            html.P(
                "Familiarise yourself with these terms before "
                "exploring the dashboard.",
                style={
                    "fontSize"     : "13px",
                    "color"        : C["text_secondary"],
                    "marginBottom" : "40px",
                    "fontFamily"   : "Inter, sans-serif",
                }
            ),

            # 2-column grid
            html.Div([
                html.Div([
                    html.Div([
                        html.Span(term["term"], style={
                            "fontSize"   : "13px",
                            "fontWeight" : "600",
                            "color"      : term["colour"],
                            "fontFamily" : "Inter, sans-serif",
                        }),
                        html.Span(
                            f"  ·  {term['full']}",
                            style={
                                "fontSize"   : "11px",
                                "color"      : C["text_muted"],
                                "fontFamily" : "Inter, sans-serif",
                            }
                        ),
                    ], style={"marginBottom": "8px"}),
                    html.P(
                        term["definition"],
                        style={
                            "fontSize"   : "13px",
                            "color"      : C["text_secondary"],
                            "lineHeight" : "1.6",
                            "margin"     : "0",
                            "fontFamily" : "Inter, sans-serif",
                        }
                    ),
                    *([html.P(
                        term["calc"],
                        style={
                            "fontSize"   : "11px",
                            "color"      : C["text_muted"],
                            "lineHeight" : "1.5",
                            "margin"     : "8px 0 0 0",
                            "fontFamily" : "Inter, sans-serif",
                            "borderTop"  : f"1px solid {C['border']}",
                            "paddingTop" : "8px",
                        }
                    )] if term.get("calc") else [])
                ], style={
                    "backgroundColor" : C["surface_high"],
                    "border"          : f"1px solid {C['border']}",
                    "borderTop"       : f"2px solid {term['colour']}",
                    "borderRadius"    : "6px",
                    "padding"         : "18px 20px",
                })
                for term in TERMINOLOGY
            ], style={
                "display"             : "grid",
                "gridTemplateColumns" : "1fr 1fr",
                "gap"                 : "16px",
            }),

        ], style={
            "backgroundColor" : C["bg"],
            "padding"         : "80px 80px",
        }),

        # ── FINAL CTA ────────────────────────────────────────
        html.Div([
            html.Div([
                html.H2([
                    "Ready to explore?  ",
                    html.Span("◆", style={"color": C["emerald"]})
                ], style={
                    "fontSize"     : "22px",
                    "fontWeight"   : "600",
                    "color"        : C["text"],
                    "marginBottom" : "16px",
                    "fontFamily"   : "Inter, sans-serif",
                }),
                html.P(
                    "Open the interactive dashboard to explore NDC "
                    "investment signals across 198 countries.",
                    style={
                        "fontSize"     : "14px",
                        "color"        : C["text_secondary"],
                        "marginBottom" : "32px",
                        "fontFamily"   : "Inter, sans-serif",
                    }
                ),
                dcc.Link([
                    html.Button(
                        "Open Dashboard  →",
                        style={
                            "backgroundColor" : C["emerald"],
                            "color"           : C["bg"],
                            "border"          : "none",
                            "borderRadius"    : "4px",
                            "padding"         : "14px 32px",
                            "fontSize"        : "14px",
                            "fontWeight"      : "600",
                            "fontFamily"      : "Inter, sans-serif",
                            "cursor"          : "pointer",
                        }
                    )
                ], href="/dashboard", refresh=False),
                html.P(
                    "⚠️  For research purposes only. "
                    "Not investment advice.",
                    style={
                        "fontSize"  : "11px",
                        "color"     : C["text_muted"],
                        "marginTop" : "24px",
                        "fontFamily": "Inter, sans-serif",
                    }
                )
            ], style={"textAlign": "center"})
        ], style={
            "backgroundColor" : C["surface"],
            "borderTop"       : f"1px solid {C['border']}",
            "padding"         : "100px 80px",
        }),

        # ── FOOTER ───────────────────────────────────────────
        html.Div([
            html.Div([

                # Data sources row
                html.Div([
                    html.Span("Data sources: ", style={
                        "fontSize"   : "11px",
                        "color"      : C["text_muted"],
                        "fontFamily" : "Inter, sans-serif",
                        "fontWeight" : "600",
                    }),
                    *[
                        html.A(name, href=url, target="_blank", style={
                            "fontSize"       : "11px",
                            "color"          : C["text_muted"],
                            "fontFamily"     : "Inter, sans-serif",
                            "textDecoration" : "none",
                            "marginRight"    : "12px",
                        })
                        for name, url in [
                            ("Climate Watch", "https://www.climatewatchdata.org"),
                            ("World Bank",    "https://data.worldbank.org"),
                            ("ND-GAIN",       "https://gain.nd.edu"),
                            ("OWID",          "https://ourworldindata.org"),
                            ("OECD",          "https://stats.oecd.org"),
                            ("UNFCCC",        "https://unfccc.int"),
                        ]
                    ]
                ], style={
                    "marginBottom"   : "12px",
                    "display"        : "flex",
                    "flexWrap"       : "wrap",
                    "justifyContent" : "center",
                    "gap"            : "0",
                }),

                # Divider
                html.Hr(style={
                    "border"        : "none",
                    "borderTop"     : f"1px solid {C['border']}",
                    "margin"        : "12px 0",
                }),

                # Creator and social row
                html.Div([
                    html.Span("Built by Pranav R Girimaji", style={
                        "fontSize"   : "11px",
                        "color"      : C["text_muted"],
                        "fontFamily" : "Inter, sans-serif",
                    }),
                    html.A("in", href="https://www.linkedin.com/in/prg99",
                           target="_blank", style={
                        "fontSize"        : "10px",
                        "color"           : C["emerald"],
                        "fontFamily"      : "Inter, sans-serif",
                        "textDecoration"  : "none",
                        "fontWeight"      : "700",
                        "backgroundColor" : C["emerald"] + "18",
                        "border"          : f"1px solid {C['emerald']}40",
                        "borderRadius"    : "3px",
                        "padding"         : "2px 7px",
                        "letterSpacing"   : "0.5px",
                    }),
                    html.A("GH", href="https://github.com/KirikKiwi/ndc-investment-dashboard",
                           target="_blank", style={
                        "fontSize"        : "10px",
                        "color"           : C["emerald"],
                        "fontFamily"      : "Inter, sans-serif",
                        "textDecoration"  : "none",
                        "fontWeight"      : "700",
                        "backgroundColor" : C["emerald"] + "18",
                        "border"          : f"1px solid {C['emerald']}40",
                        "borderRadius"    : "3px",
                        "padding"         : "2px 7px",
                        "letterSpacing"   : "0.5px",
                    }),
                    html.Span("  ·  Green-Gott's Vault · Beta 2.0", style={
                        "fontSize"   : "11px",
                        "color"      : C["text_muted"],
                        "fontFamily" : "Inter, sans-serif",
                    }),
                ], style={
                    "display"        : "flex",
                    "alignItems"     : "center",
                    "justifyContent" : "center",
                    "flexWrap"       : "wrap",
                    "gap"            : "8px",
                }),

            ], style={"maxWidth": "960px", "width": "100%"}),
        ], style={
            "backgroundColor" : C["surface"],
            "borderTop"       : f"1px solid {C['border']}",
            "padding"         : "32px 80px",
            "textAlign"       : "center",
            "display"         : "flex",
            "justifyContent"  : "center",
        }),

    ], style={
        "fontFamily"      : "Inter, sans-serif",
        "backgroundColor" : C["bg"],
    })


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    page = layout()
    print("✅ landing.py verified")
    print(f"   Sections    : Hero, Stats, Use Cases, "
          f"Methodology, How-To, Terminology, Sources, CTA")
    print(f"   Use cases   : {len(USE_CASES)}")
    print(f"   Terms       : {len(TERMINOLOGY)}")
    print(f"   Sources     : {len(SOURCES)}")