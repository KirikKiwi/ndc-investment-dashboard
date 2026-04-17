# ============================================================
# NDC Investment Dashboard
# pages/tier3.py — Sector deep-dive panel (Tier 3)
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import html
import pandas as pd
from components import C, SECTOR_COLOURS
from components import (confidence_badge, sector_pill,
                        data_row, flag_pill)
from data import (load_master, load_tags, load_projects,
                  get_country_name, clean_ndc_text,
                  get_country_projects_top3,
                  get_comparable_markets_benchmark,
                  get_benchmark_score)

master_df   = load_master()
tags_df     = load_tags()
projects_df = load_projects()

# ============================================================
# SECTOR KEYWORD MAPPING
# Maps sector names to project search terms
# ============================================================

SECTOR_KEYWORDS = {
    "Energy": [
        "solar","wind","hydropower","renewable","energy",
        "electricity","power","grid","clean energy","biomass",
    ],
    "Transport": [
        "transport","electric vehicle","rail","bus","mobility",
        "road","aviation","shipping","fleet",
    ],
    "Land, Agriculture & Forestry": [
        "agriculture","forest","land","redd","agroforestry",
        "crop","livestock","soil","deforestation",
    ],
    "Water & Blue Economy": [
        "water","ocean","coastal","flood","marine","fisheries",
        "watershed","drought","sanitation",
    ],
    "Built Environment & Waste": [
        "building","construction","waste","urban","housing",
        "retrofit","landfill","recycling","city",
    ],
    "Industry & Heavy Sector": [
        "industry","manufacturing","steel","cement","hydrogen",
        "industrial","process","emissions",
    ],
    "Nature-Based Solutions": [
        "nature","ecosystem","biodiversity","restoration",
        "conservation","habitat","green infrastructure",
    ],
}

SECTOR_DESCRIPTIONS = {
    "Energy": (
        "Energy sector commitments cover renewable energy "
        "deployment, grid modernisation, energy efficiency and "
        "fossil fuel transition. This is the largest investment "
        "opportunity in most NDCs."
    ),
    "Transport": (
        "Transport commitments span electric vehicle adoption, "
        "public transit expansion, rail investment and aviation "
        "decarbonisation. Often the second largest emissions "
        "source after energy."
    ),
    "Land, Agriculture & Forestry": (
        "Land sector commitments cover deforestation reduction, "
        "sustainable agriculture, reforestation and soil carbon. "
        "Critical for both mitigation and food security."
    ),
    "Water & Blue Economy": (
        "Water commitments address supply infrastructure, flood "
        "resilience, coastal protection and marine conservation. "
        "Predominantly adaptation-focused."
    ),
    "Built Environment & Waste": (
        "Built environment commitments cover green buildings, "
        "urban planning, waste management and circular economy "
        "measures. Strong link to municipal finance."
    ),
    "Industry & Heavy Sector": (
        "Industrial commitments address hard-to-abate sectors "
        "including steel, cement and chemicals. Green hydrogen "
        "and carbon capture are key enabling technologies."
    ),
    "Nature-Based Solutions": (
        "Nature-based commitments cover ecosystem restoration, "
        "biodiversity protection and natural carbon sinks. "
        "Growing intersection with voluntary carbon markets."
    ),
}

# ============================================================
# COMPARABLE MARKETS
# ============================================================


def get_sector_projects(iso_code, sector_name):
    """
    Filters World Bank projects for this country
    by sector keyword matching.
    """
    country_projs = get_country_projects_top3(
        iso_code, projects_df
    )
    if country_projs.empty:
        return pd.DataFrame()

    keywords = SECTOR_KEYWORDS.get(sector_name, [])
    if not keywords:
        return country_projs

    def matches_sector(row):
        text = (
            str(row.get("project_name", "")) + " " +
            str(row.get("project_abstract", ""))
        ).lower()
        return any(kw.lower() in text for kw in keywords)

    filtered = country_projs[
        country_projs.apply(matches_sector, axis=1)
    ]
    return filtered if not filtered.empty else country_projs


# ============================================================
# TIER 3 PANEL CONTENT
# ============================================================

def tier3_content(iso_code, sector_name):
    """
    Builds the full Tier 3 sector deep-dive panel.
    """
    country_name = get_country_name(iso_code)
    sector_colour = SECTOR_COLOURS.get(sector_name, C["emerald"])

    # Get sector tag for this country
    country_tag = tags_df[
        (tags_df["iso_code"] == iso_code) &
        (tags_df["sector"] == sector_name)
    ]

    tag = country_tag.iloc[0] if not country_tag.empty else None

    def safe_str(val):
        if val is None: return ""
        s = str(val).strip()
        return "" if s.lower() in ("nan","none","") else s

    # ── Header ──────────────────────────────────────────────
    header = html.Div([
        # Sticky close button at very top
        html.Div([
            html.Div([
                html.Span(country_name, style={
                    "fontSize"   : "13px",
                    "color"      : C["text_muted"],
                    "fontFamily" : "Inter, sans-serif",
                }),
                html.Span(" / ", style={
                    "color": C["text_muted"], "margin": "0 4px"
                }),
                html.Span(sector_name, style={
                    "fontSize"   : "13px",
                    "fontWeight" : "600",
                    "color"      : sector_colour,
                    "fontFamily" : "Inter, sans-serif",
                }),
            ]),
            html.Div("× Close", id="close-tier3-btn", style={
                "fontSize"        : "12px",
                "color"           : "#ffffff",
                "cursor"          : "pointer",
                "lineHeight"      : "1",
                "userSelect"      : "none",
                "padding"         : "6px 14px",
                "backgroundColor" : "#c0392b",
                "borderRadius"    : "4px",
                "fontWeight"      : "700",
                "fontFamily"      : "Inter, sans-serif",
            })
        ], style={
            "display"         : "flex",
            "justifyContent"  : "space-between",
            "alignItems"      : "center",
            "padding"         : "12px 28px",
            "backgroundColor" : C["surface"],
            "borderBottom"    : f"1px solid {C['border']}",
            "position"        : "sticky",
            "top"             : "0",
            "zIndex"          : "10",
            "marginLeft"      : "-28px",
            "marginRight"     : "-28px",
            "marginTop"       : "-32px",
            "marginBottom"    : "24px",
        }),

        # Sector title below sticky bar
        html.Div(sector_name, style={
            "fontSize"     : "22px",
            "fontWeight"   : "700",
            "color"        : sector_colour,
            "fontFamily"   : "Inter, sans-serif",
            "marginBottom" : "8px",
        }),

    # Sector description
    html.Div(
        SECTOR_DESCRIPTIONS.get(sector_name, ""),
            style={
                "fontSize"   : "13px",
                "color"      : C["text_secondary"],
                "fontFamily" : "Inter, sans-serif",
                "lineHeight" : "1.6",
                "padding"    : "12px 14px",
                "backgroundColor": C["surface_high"],
                "border"     : f"1px solid {C['border']}",
                "borderLeft" : f"3px solid {sector_colour}",
                "borderRadius": "4px",
                "marginBottom": "20px",
            }
        ),
    ])

    # ── Section 1: NDC Commitment ────────────────────────────
    if tag is not None:
        lens       = safe_str(tag.get("climate_lens"))
        commitment = safe_str(tag.get("commitment_type"))
        instrument = safe_str(tag.get("financing_instrument"))
        horizon    = safe_str(tag.get("implementation_horizon"))
        confidence = safe_str(tag.get("confidence"))

        dim_rows = []
        for label, value, colour in [
            ("Climate Lens",    lens,       C["emerald"]),
            ("Commitment Type", commitment, C["crimson"]),
            ("Instrument",      instrument, C["cobalt"]),
            ("Horizon",         horizon,    C["amber"]),
        ]:
            if value:
                dim_rows.append(
                    html.Div([
                        html.Span(label, style={
                            "fontSize"      : "10px",
                            "fontWeight"    : "600",
                            "textTransform" : "uppercase",
                            "letterSpacing" : "1px",
                            "color"         : C["text_muted"],
                            "fontFamily"    : "Inter, sans-serif",
                            "width"         : "110px",
                            "flexShrink"    : "0",
                        }),
                        html.Span(value, style={
                            "fontSize"   : "12px",
                            "color"      : colour,
                            "fontFamily" : "Inter, sans-serif",
                            "fontWeight" : "600",
                        })
                    ], style={
                        "display"      : "flex",
                        "alignItems"   : "center",
                        "gap"          : "8px",
                        "padding"      : "6px 0",
                        "borderBottom" : f"1px solid {C['border']}",
                    })
                )

        ndc_section = html.Div([
            html.Div([
                html.Div("NDC Commitment", style={
                    "fontSize"      : "11px",
                    "fontWeight"    : "600",
                    "textTransform" : "uppercase",
                    "letterSpacing" : "1.5px",
                    "color"         : C["text_muted"],
                    "fontFamily"    : "Inter, sans-serif",
                    "marginBottom"  : "12px",
                }),
                html.Div(dim_rows),
                html.Div([
                    html.Span("Signal confidence: ", style={
                        "fontSize"   : "11px",
                        "color"      : C["text_muted"],
                        "fontFamily" : "Inter, sans-serif",
                    }),
                    confidence_badge(confidence) if confidence
                    else html.Span()
                ], style={"marginTop": "10px"})
            ], style={
                "backgroundColor" : C["surface_high"],
                "border"          : f"1px solid {C['border']}",
                "borderRadius"    : "4px",
                "padding"         : "14px",
                "marginBottom"    : "20px",
            })
        ])
    else:
        ndc_section = html.Div([
            html.Div(
                f"No specific {sector_name} tag found in NDC for "
                f"{country_name}.",
                style={
                    "fontSize"   : "12px",
                    "color"      : C["text_muted"],
                    "fontFamily" : "Inter, sans-serif",
                    "padding"    : "12px",
                    "backgroundColor": C["surface_high"],
                    "border"    : f"1px solid {C['border']}",
                    "borderRadius": "4px",
                    "marginBottom": "20px",
                }
            )
        ])

    # ── Section 2: Project Pipeline ──────────────────────────
    sector_projs = get_sector_projects(iso_code, sector_name)

    if not sector_projs.empty:
        proj_rows = []
        for _, proj in sector_projs.iterrows():
            name   = str(proj.get("project_name",""))[:70]
            status = str(proj.get("status",""))
            date   = str(proj.get("approval_date",""))[:10]
            sc     = C["emerald"] if status == "Active" else C["text_muted"]

            proj_rows.append(html.Div([
                html.Div(name, style={
                    "fontSize"    : "12px",
                    "color"       : C["text"],
                    "fontFamily"  : "Inter, sans-serif",
                    "marginBottom": "3px",
                }),
                html.Div([
                    html.Span(status, style={
                        "fontSize"   : "10px",
                        "color"      : sc,
                        "fontWeight" : "600",
                        "fontFamily" : "Inter, sans-serif",
                    }),
                    html.Span(
                        f"  ·  {date}" if date else "",
                        style={
                            "fontSize"   : "10px",
                            "color"      : C["text_muted"],
                            "fontFamily" : "Inter, sans-serif",
                        }
                    ),
                ])
            ], style={
                "padding"      : "8px 0",
                "borderBottom" : f"1px solid {C['border']}",
            }))

        pipeline_section = html.Div([
            html.Div("Project Pipeline", style={
                "fontSize"      : "11px",
                "fontWeight"    : "600",
                "textTransform" : "uppercase",
                "letterSpacing" : "1.5px",
                "color"         : C["text_muted"],
                "fontFamily"    : "Inter, sans-serif",
                "marginBottom"  : "12px",
            }),
            html.Div(proj_rows),
            html.Div(
                "World Bank projects matched to this sector. "
                "IATI coverage coming in Sprint 3.",
                style={
                    "fontSize"  : "10px",
                    "color"     : C["text_muted"],
                    "fontFamily": "Inter, sans-serif",
                    "marginTop" : "8px",
                    "fontStyle" : "italic",
                }
            )
        ], style={
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderRadius"    : "4px",
            "padding"         : "14px",
            "marginBottom"    : "20px",
        })
    else:
        pipeline_section = html.Div([
            html.Div("Project Pipeline", style={
                "fontSize"      : "11px",
                "fontWeight"    : "600",
                "textTransform" : "uppercase",
                "letterSpacing" : "1.5px",
                "color"         : C["text_muted"],
                "fontFamily"    : "Inter, sans-serif",
                "marginBottom"  : "12px",
            }),
            html.Div(
                "No World Bank projects matched to this sector. "
                "IATI regional coverage coming in Sprint 3.",
                style={
                    "fontSize"   : "12px",
                    "color"      : C["text_muted"],
                    "fontFamily" : "Inter, sans-serif",
                    "lineHeight" : "1.5",
                }
            )
        ], style={
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderRadius"    : "4px",
            "padding"         : "14px",
            "marginBottom"    : "20px",
        })

    # ── Section 3: Investment Landscape ─────────────────────
    investment_section = html.Div([
        html.Div("Investment Landscape", style={
            "fontSize"      : "11px",
            "fontWeight"    : "600",
            "textTransform" : "uppercase",
            "letterSpacing" : "1.5px",
            "color"         : C["text_muted"],
            "fontFamily"    : "Inter, sans-serif",
            "marginBottom"  : "12px",
        }),
        html.Div([
            _placeholder_block(
                "Active Investors and Funds",
                "Institutional investors, DFIs and fund managers "
                "active in this sector and country. "
                "Available via IATI in Sprint 3."
            ),
            _placeholder_block(
                "Instrument Mix",
                "Grant, debt, equity and guarantee breakdown for "
                "this sector. Available via OECD CRS in Sprint 3."
            ),
        ], style={"display": "flex", "flexDirection": "column",
                  "gap": "12px"}),
    ], style={
        "backgroundColor" : C["surface_high"],
        "border"          : f"1px solid {C['border']}",
        "borderRadius"    : "4px",
        "padding"         : "14px",
        "marginBottom"    : "20px",
    })

    # ── Section 4: Comparable Markets ───────────────────────
    comparables = get_comparable_markets_benchmark(
        iso_code, sector_name, master_df, tags_df
    )

    # Get selected country benchmark for context
    this_score = get_benchmark_score(iso_code)

    if not comparables.empty:
        # Table header
        header_row = html.Div([
            html.Span("#", style={
                "width": "20px", "fontSize": "10px",
                "color": C["text_muted"], "fontFamily": "Inter, sans-serif",
                "flexShrink": "0",
            }),
            html.Span("Country", style={
                "flex": "1", "fontSize": "10px",
                "color": C["text_muted"], "fontFamily": "Inter, sans-serif",
                "fontWeight": "600", "textTransform": "uppercase",
                "letterSpacing": "1px",
            }),
            html.Span("Benchmark", style={
                "width": "72px", "fontSize": "10px",
                "color": C["text_muted"], "fontFamily": "Inter, sans-serif",
                "fontWeight": "600", "textTransform": "uppercase",
                "letterSpacing": "1px", "textAlign": "right",
            }),
            html.Span("Renewable", style={
                "width": "72px", "fontSize": "10px",
                "color": C["text_muted"], "fontFamily": "Inter, sans-serif",
                "fontWeight": "600", "textTransform": "uppercase",
                "letterSpacing": "1px", "textAlign": "right",
            }),
            html.Span("Readiness", style={
                "width": "72px", "fontSize": "10px",
                "color": C["text_muted"], "fontFamily": "Inter, sans-serif",
                "fontWeight": "600", "textTransform": "uppercase",
                "letterSpacing": "1px", "textAlign": "right",
            }),
        ], style={
            "display": "flex", "alignItems": "center",
            "gap": "8px", "padding": "0 0 8px 0",
            "borderBottom": f"2px solid {C['border']}",
            "marginBottom": "4px",
        })

        comp_rows = [header_row]

        # Selected country row first for context
        if this_score:
            this_row = master_df[master_df["iso_code"] == iso_code]
            if not this_row.empty:
                r = this_row.iloc[0]
                renew = (f"{r['renewable_electricity_pct']:.0f}%"
                         if pd.notna(r.get("renewable_electricity_pct"))
                         else "N/A")
                ready = (f"{r['readiness_score']:.2f}"
                         if pd.notna(r.get("readiness_score"))
                         else "N/A")
                comp_rows.append(html.Div([
                    html.Span("—", style={
                        "width": "20px", "fontSize": "11px",
                        "color": C["emerald"], "fontFamily": "Inter, sans-serif",
                        "flexShrink": "0",
                    }),
                    html.Span(
                        f"{get_country_name(iso_code)} (selected)",
                        style={
                            "flex": "1", "fontSize": "12px",
                            "color": C["emerald"], "fontFamily": "Inter, sans-serif",
                            "fontWeight": "600",
                        }
                    ),
                    html.Span(f"{this_score:.1f}", style={
                        "width": "72px", "fontSize": "12px",
                        "color": C["emerald"], "fontFamily": "Inter, sans-serif",
                        "fontWeight": "700", "textAlign": "right",
                    }),
                    html.Span(renew, style={
                        "width": "72px", "fontSize": "12px",
                        "color": C["text_secondary"], "fontFamily": "Inter, sans-serif",
                        "textAlign": "right",
                    }),
                    html.Span(ready, style={
                        "width": "72px", "fontSize": "12px",
                        "color": C["text_secondary"], "fontFamily": "Inter, sans-serif",
                        "textAlign": "right",
                    }),
                ], style={
                    "display": "flex", "alignItems": "center",
                    "gap": "8px", "padding": "7px 0",
                    "borderBottom": f"1px solid {C['border']}",
                    "backgroundColor": C["emerald"] + "08",
                }))

        # Comparable rows
        for i, (_, row) in enumerate(comparables.iterrows()):
            cname  = get_country_name(row["iso_code"])
            score  = row.get("benchmark_score")
            renew  = (f"{row['renewable_electricity_pct']:.0f}%"
                      if pd.notna(row.get("renewable_electricity_pct"))
                      else "N/A")
            ready  = (f"{row['readiness_score']:.2f}"
                      if pd.notna(row.get("readiness_score"))
                      else "N/A")
            score_str = f"{score:.1f}" if pd.notna(score) else "N/A"

            comp_rows.append(html.Div([
                html.Span(f"{i+1}", style={
                    "width": "20px", "fontSize": "11px",
                    "color": C["text_muted"], "fontFamily": "Inter, sans-serif",
                    "fontWeight": "600", "flexShrink": "0",
                }),
                html.Span(cname, style={
                    "flex": "1", "fontSize": "12px",
                    "color": C["text"], "fontFamily": "Inter, sans-serif",
                }),
                html.Span(score_str, style={
                    "width": "72px", "fontSize": "12px",
                    "color": C["amber"], "fontFamily": "Inter, sans-serif",
                    "fontWeight": "600", "textAlign": "right",
                }),
                html.Span(renew, style={
                    "width": "72px", "fontSize": "12px",
                    "color": C["text_secondary"], "fontFamily": "Inter, sans-serif",
                    "textAlign": "right",
                }),
                html.Span(ready, style={
                    "width": "72px", "fontSize": "12px",
                    "color": C["text_secondary"], "fontFamily": "Inter, sans-serif",
                    "textAlign": "right",
                }),
            ], style={
                "display": "flex", "alignItems": "center",
                "gap": "8px", "padding": "7px 0",
                "borderBottom": f"1px solid {C['border']}",
            }))

        # Benchmark explanation
        explanation = html.Div(
            "Benchmark score (0-100) is a weighted composite: "
            "Readiness 30%, GDP per capita 25%, Renewable share 20%, "
            "Vulnerability 15%, MDB engagement 5%, Finance dependency 5%. "
            "All metrics normalised. Higher score = stronger investment readiness.",
            style={
                "fontSize"  : "10px",
                "color"     : C["text_muted"],
                "fontFamily": "Inter, sans-serif",
                "lineHeight": "1.5",
                "marginTop" : "10px",
                "fontStyle" : "italic",
            }
        )

        comp_section = html.Div([
            html.Div("Comparable Markets", style={
                "fontSize"      : "11px",
                "fontWeight"    : "600",
                "textTransform" : "uppercase",
                "letterSpacing" : "1.5px",
                "color"         : C["text_muted"],
                "fontFamily"    : "Inter, sans-serif",
                "marginBottom"  : "6px",
            }),
            html.Div(
                f"Same investment tier countries with active "
                f"{sector_name} NDC signals, ranked by composite "
                f"investment readiness benchmark.",
                style={
                    "fontSize"     : "11px",
                    "color"        : C["text_muted"],
                    "fontFamily"   : "Inter, sans-serif",
                    "marginBottom" : "12px",
                    "lineHeight"   : "1.5",
                }
            ),
            html.Div(comp_rows),
            explanation,
        ], style={
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderRadius"    : "4px",
            "padding"         : "14px",
            "marginBottom"    : "20px",
        })
    else:
        comp_section = html.Div([
            html.Div("Comparable Markets", style={
                "fontSize"      : "11px",
                "fontWeight"    : "600",
                "textTransform" : "uppercase",
                "letterSpacing" : "1.5px",
                "color"         : C["text_muted"],
                "fontFamily"    : "Inter, sans-serif",
                "marginBottom"  : "8px",
            }),
            html.Div(
                "No comparable markets found in the same investment "
                "tier with this sector tag.",
                style={
                    "fontSize"  : "12px",
                    "color"     : C["text_muted"],
                    "fontFamily": "Inter, sans-serif",
                }
            )
        ], style={
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderRadius"    : "4px",
            "padding"         : "14px",
            "marginBottom"    : "20px",
        })

    # ── Section 5: News and Policy ───────────────────────────
    news_section = html.Div([
        html.Div("News and Policy", style={
            "fontSize"      : "11px",
            "fontWeight"    : "600",
            "textTransform" : "uppercase",
            "letterSpacing" : "1.5px",
            "color"         : C["text_muted"],
            "fontFamily"    : "Inter, sans-serif",
            "marginBottom"  : "12px",
        }),
        html.Div([
            _placeholder_block(
                "Recent Sector News",
                f"Latest climate investment news for {sector_name} "
                f"in {country_name}. "
                "Available via Google CSE in Sprint 3."
            ),
            _placeholder_block(
                "Government Policy and Incentives",
                f"Active subsidies, tax incentives and regulatory "
                f"frameworks for {sector_name} in {country_name}. "
                "Available via Google CSE in Sprint 3."
            ),
        ], style={"display": "flex", "flexDirection": "column",
                  "gap": "12px"}),
    ], style={
        "backgroundColor" : C["surface_high"],
        "border"          : f"1px solid {C['border']}",
        "borderRadius"    : "4px",
        "padding"         : "14px",
        "marginBottom"    : "20px",
    })

    return html.Div([
        header,
        ndc_section,
        pipeline_section,
        investment_section,
        comp_section,
        news_section,
    ])


def _placeholder_block(title, description):
    return html.Div([
        html.Div([
            html.Span("◌ ", style={
                "color"    : C["text_muted"],
                "fontSize" : "14px",
            }),
            html.Span(title, style={
                "fontSize"   : "12px",
                "fontWeight" : "600",
                "color"      : C["text_secondary"],
                "fontFamily" : "Inter, sans-serif",
            }),
        ], style={"marginBottom": "4px"}),
        html.Div(description, style={
            "fontSize"   : "11px",
            "color"      : C["text_muted"],
            "fontFamily" : "Inter, sans-serif",
            "lineHeight" : "1.5",
            "fontStyle"  : "italic",
        })
    ], style={
        "padding"         : "10px 12px",
        "backgroundColor" : C["bg"],
        "border"          : f"1px solid {C['border']}",
        "borderRadius"    : "4px",
        "borderStyle"     : "dashed",
    })


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    result = tier3_content("KEN", "Energy")
    print("✅ tier3.py verified")
    print("   Sections: Header, NDC Commitment, Pipeline,")
    print("             Investment Landscape, Comparable Markets,")
    print("             News and Policy")
    result2 = tier3_content("DEU", "Industry & Heavy Sector")
    print("   DEU Industry: OK")
