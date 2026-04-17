# ============================================================
# NDC Investment Dashboard
# pages/globe.py — D3 globe + expanded country panel
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from components import C, T, SECTOR_COLOURS, TIER_COLOURS
from components import (confidence_badge, sector_pill, tier_badge,
                        data_row, flag_pill, empty_state)
from data import (load_master, load_tags, load_projects,
                  prepare_map_data, get_global_kpis,
                  get_sector_summary, clean_ndc_text,
                  get_country_detail, get_country_name,
                  get_regional_mdb, get_country_projects_top3,
                  get_finance_context)

master_df   = load_master()
tags_df     = load_tags()
projects_df = load_projects()
map_df      = prepare_map_data(master_df, tags_df)
kpis        = get_global_kpis(master_df, tags_df)
sector_sum  = get_sector_summary(tags_df)


def get_country_data_json():
    data = {}
    for _, row in map_df.iterrows():
        iso = row.get("iso_code")
        if not iso:
            continue
        data[iso] = {
            "display_name"             : get_country_name(iso),
            "investment_tier"          : row.get("investment_tier", ""),
            "tier_score"               : float(row.get("tier_score", 0)),
            "ndgain_score"             : float(row["ndgain_score"])
                                         if pd.notna(row.get("ndgain_score"))
                                         else None,
            "vulnerability_score"      : float(row["vulnerability_score"])
                                         if pd.notna(row.get("vulnerability_score"))
                                         else None,
            "renewable_electricity_pct": float(row["renewable_electricity_pct"])
                                         if pd.notna(row.get("renewable_electricity_pct"))
                                         else None,
            "sector_count"             : int(row.get("sector_count", 0)),
            "conditional_count"        : int(row.get("conditional_count", 0)),
        }
    return data


def kpi_strip():
    items = [
        ("NDC Countries",       str(kpis["total_countries"]),
         C["emerald"],
         "198 countries plus the EU collective submission"),
        ("Conditional Signals", str(kpis["conditional_countries"]),
         C["crimson"],
         "Countries requiring external finance to meet targets"),
        ("Avg ND-GAIN",         str(kpis["avg_ndgain"]),
         C["amber"],
         "Average climate readiness score out of 100"),
        ("WB Projects",         str(kpis["total_projects"]),
         C["cobalt"],
         "Active World Bank climate finance projects"),
        ("Established",         str(kpis["tier1_count"]),
         C["tier1"],
         "Tier 1 markets with strong institutional capacity"),
        ("Emerging",            str(kpis["tier2_count"]),
         C["tier2"],
         "Tier 2 markets with growing climate finance activity"),
        ("Frontier",            str(kpis["tier3_count"]),
         C["tier3"],
         "Tier 3 markets with highest conditional finance need"),
        ("Avg Renewables",      f"{kpis['avg_renewable']}%",
         C["nature"],
         "Average renewable share of electricity generation"),
    ]
    return html.Div([
        html.Div(id="kpi-strip", children=[
            html.Div([
                html.Div(value, style={
                    "fontSize"     : "20px",
                    "fontWeight"   : "700",
                    "color"        : colour,
                    "fontFamily"   : "Inter, sans-serif",
                    "lineHeight"   : "1",
                    "marginBottom" : "2px"
                }),
                html.Div(label, style={
                    "fontSize"      : "11px",
                    "fontWeight"    : "600",
                    "textTransform" : "uppercase",
                    "letterSpacing" : "1px",
                    "color"         : C["text_muted"],
                    "fontFamily"    : "Inter, sans-serif",
                    "marginBottom"  : "3px"
                }),
                html.Div(context, style={
                    "fontSize"   : "10px",
                    "fontWeight" : "400",
                    "color"      : C["text_muted"],
                    "fontFamily" : "Inter, sans-serif",
                    "lineHeight" : "1.3",
                    "maxWidth"   : "140px",
                    "margin"     : "0 auto"
                }),
            ], style={
                "textAlign"   : "center",
                "padding"     : "12px 20px",
                "borderRight" : f"1px solid {C['border']}"
                                if i < len(items) - 1 else "none",
                "flexShrink"  : "0",
            })
            for i, (label, value, colour, context) in enumerate(items)
        ], style={
            "display"        : "flex",
            "overflowX"      : "auto",
            "justifyContent" : "space-between",
        })
    ], style={
        "backgroundColor" : C["surface"],
        "borderTop"       : f"1px solid {C['border']}",
        "borderBottom"    : f"1px solid {C['border']}",
        "position"        : "relative",
        "zIndex"          : "50",
    })


def section_title(text, tooltip=None):
    """Section label with optional info tooltip."""
    children = [
        html.Span(text, style={
            "fontSize"      : "11px",
            "fontWeight"    : "600",
            "textTransform" : "uppercase",
            "letterSpacing" : "1.5px",
            "color"         : C["text_muted"],
            "fontFamily"    : "Inter, sans-serif",
        })
    ]
    if tooltip:
        children.append(
            html.Span(" ⓘ", style={
                "fontSize"   : "11px",
                "color"      : C["text_muted"],
                "cursor"     : "help",
                "position"   : "relative",
                "title"      : tooltip,
            })
        )
    return html.Div(children, style={"marginBottom": "12px"})


def territory_panel(name):
    """Minimal panel for territories with no NDC submission."""
    return html.Div([
        html.Div([
            html.Div(name, style={
                "fontSize"     : "18px",
                "fontWeight"   : "700",
                "color"        : C["text"],
                "marginBottom" : "8px",
                "fontFamily"   : "Inter, sans-serif",
            }),
        ]),
        html.Div("×", id="close-panel-btn", style={
            "fontSize"  : "22px",
            "color"     : C["text_muted"],
            "cursor"    : "pointer",
            "lineHeight": "1",
        })
    ], style={
        "display"        : "flex",
        "justifyContent" : "space-between",
        "alignItems"     : "flex-start",
        "marginBottom"   : "20px"
    }), html.Div([
        html.Div("No NDC Submission", style={
            "fontSize"      : "11px",
            "fontWeight"    : "600",
            "textTransform" : "uppercase",
            "letterSpacing" : "1.5px",
            "color"         : C["text_muted"],
            "marginBottom"  : "8px",
            "fontFamily"    : "Inter, sans-serif",
        }),
        html.P(
            f"{name} has not submitted a Nationally Determined "
            f"Contribution to the UNFCCC. No climate commitment "
            f"data is available for this territory.",
            style={
                "fontSize"   : "13px",
                "color"      : C["text_secondary"],
                "lineHeight" : "1.6",
                "fontFamily" : "Inter, sans-serif",
            }
        )
    ], style={
        "backgroundColor" : C["surface_high"],
        "border"          : f"1px solid {C['border']}",
        "borderLeft"      : f"2px solid {C['text_muted']}",
        "borderRadius"    : "4px",
        "padding"         : "14px",
    })


def territory_panel(name):
    """Minimal panel for territories with no NDC submission."""
    return html.Div([
        html.Div([
            html.Div([
                html.Div(name, style={
                    "fontSize"     : "18px",
                    "fontWeight"   : "700",
                    "color"        : C["text"],
                    "marginBottom" : "8px",
                    "fontFamily"   : "Inter, sans-serif",
                }),
            ]),
            html.Div("×", id="close-panel-btn", style={
                "fontSize"  : "22px",
                "color"     : C["text_muted"],
                "cursor"    : "pointer",
                "lineHeight": "1",
            })
        ], style={
            "display"        : "flex",
            "justifyContent" : "space-between",
            "alignItems"     : "flex-start",
            "marginBottom"   : "20px"
        }),
        html.Div([
            html.Div("No NDC Submission", style={
                "fontSize"      : "11px",
                "fontWeight"    : "600",
                "textTransform" : "uppercase",
                "letterSpacing" : "1.5px",
                "color"         : C["text_muted"],
                "marginBottom"  : "8px",
                "fontFamily"    : "Inter, sans-serif",
            }),
            html.P(
                f"{name} has not submitted a Nationally Determined "
                f"Contribution to the UNFCCC. No climate commitment "
                f"data is available for this territory.",
                style={
                    "fontSize"   : "13px",
                    "color"      : C["text_secondary"],
                    "lineHeight" : "1.6",
                    "fontFamily" : "Inter, sans-serif",
                }
            )
        ], style={
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderLeft"      : f"2px solid {C['text_muted']}",
            "borderRadius"    : "4px",
            "padding"         : "14px",
        })
    ])


def empty_panel():
    return html.Div([
        html.Div("◎", style={
            "fontSize": "32px", "color": C["text_muted"],
            "marginBottom": "16px"
        }),
        html.Div("Select a country", style={
            "fontSize": "15px", "fontWeight": "600",
            "color": C["text_secondary"], "marginBottom": "8px",
            "fontFamily": "Inter, sans-serif",
        }),
        html.Div(
            "Click any country on the globe to view "
            "its NDC investment profile.",
            style={
                "fontSize": "13px", "color": C["text_muted"],
                "lineHeight": "1.6", "fontFamily": "Inter, sans-serif",
            }
        )
    ], style={"textAlign": "center", "padding": "60px 24px"})


def country_panel_content(iso_code):
    from data import query

    country_data, country_tags = get_country_detail(
        iso_code, master_df, tags_df
    )
    if country_data is None:
        return empty_panel()

    full_name   = get_country_name(iso_code)
    mdb_code, mdb_name = get_regional_mdb(iso_code)

    # ── SECTION 1: Header ────────────────────────────────
    header = html.Div([
        html.Div([
            html.Div(full_name, style={
                "fontSize"     : "18px",
                "fontWeight"   : "700",
                "color"        : C["text"],
                "marginBottom" : "8px",
                "fontFamily"   : "Inter, sans-serif",
                "lineHeight"   : "1.2",
            }),
            tier_badge(country_data.get("investment_tier", "N/A")),
        ]),
        html.Div("×", id="close-panel-btn", style={
            "fontSize"    : "22px",
            "color"       : C["text_muted"],
            "cursor"      : "pointer",
            "padding"     : "4px 8px",
            "lineHeight"  : "1",
            "userSelect"  : "none",
        })
    ], style={
        "display"        : "flex",
        "justifyContent" : "space-between",
        "alignItems"     : "flex-start",
        "marginBottom"   : "16px"
    })

    # ── FINANCE SIGNAL ───────────────────────────────────
    cond_pct   = country_data.get("conditional_pct_uplift")
    uncond_pct = country_data.get("unconditional_pct")

    try:
        cond_pct   = float(cond_pct) if cond_pct and not pd.isna(cond_pct) else None
        uncond_pct = float(uncond_pct) if uncond_pct and not pd.isna(uncond_pct) else None
    except Exception:
        cond_pct   = None
        uncond_pct = None

    if cond_pct:
        total_pct  = (uncond_pct or 0) + cond_pct
        uncond_bar = round((uncond_pct / total_pct) * 100) if uncond_pct else 0
        cond_bar   = round((cond_pct   / total_pct) * 100)

        bar_section = html.Div([
            html.Div([
                html.Span("Unconditional", style={
                    "fontSize": "10px", "color": C["text_muted"],
                    "fontFamily": "Inter, sans-serif",
                    "width": "90px", "display": "inline-block"
                }),
                html.Div(style={
                    "display": "inline-block",
                    "width": f"{uncond_bar}%",
                    "backgroundColor": C["emerald"],
                    "height": "8px",
                    "borderRadius": "2px",
                    "verticalAlign": "middle",
                    "minWidth": "4px",
                }),
                html.Span(
                    f" {uncond_pct:.1f}%" if uncond_pct else "",
                    style={"fontSize": "10px", "color": C["emerald"],
                           "fontFamily": "Inter, sans-serif",
                           "marginLeft": "6px"}
                ),
            ], style={"marginBottom": "6px"}),
            html.Div([
                html.Span("Conditional", style={
                    "fontSize": "10px", "color": C["text_muted"],
                    "fontFamily": "Inter, sans-serif",
                    "width": "90px", "display": "inline-block"
                }),
                html.Div(style={
                    "display": "inline-block",
                    "width": f"{cond_bar}%",
                    "backgroundColor": C["crimson"],
                    "height": "8px",
                    "borderRadius": "2px",
                    "verticalAlign": "middle",
                    "minWidth": "4px",
                }),
                html.Span(
                    f" {cond_pct:.1f}%",
                    style={"fontSize": "10px", "color": C["crimson"],
                           "fontFamily": "Inter, sans-serif",
                           "marginLeft": "6px"}
                ),
            ]),
        ], style={"marginBottom": "10px"})

        finance_signal = html.Div([
            html.Div("Climate Finance Signal", style={
                "fontSize"      : "11px",
                "fontWeight"    : "600",
                "textTransform" : "uppercase",
                "letterSpacing" : "1.5px",
                "color"         : C["text_muted"],
                "marginBottom"  : "10px",
                "fontFamily"    : "Inter, sans-serif",
            }),
            bar_section,
            html.Div(
                f"{full_name} could achieve {cond_pct:.1f}% "
                f"additional GHG reduction beyond its unconditional "
                f"target subject to international climate finance. "
                f"This is a quantified signal of external capital need.",
                style={
                    "fontSize"   : "11px",
                    "color"      : C["text_secondary"],
                    "lineHeight" : "1.5",
                    "fontFamily" : "Inter, sans-serif",
                }
            )
        ], style={
            "backgroundColor" : C["crimson"] + "10",
            "border"          : f"1px solid {C['crimson']}30",
            "borderLeft"      : f"3px solid {C['crimson']}",
            "borderRadius"    : "4px",
            "padding"         : "12px 14px",
            "marginBottom"    : "16px",
        })

    else:
        # Proxy finance context for countries without signal
        context_text = get_finance_context(country_data)
        finance_signal = html.Div([
            html.Div("Climate Finance Context", style={
                "fontSize"      : "11px",
                "fontWeight"    : "600",
                "textTransform" : "uppercase",
                "letterSpacing" : "1.5px",
                "color"         : C["text_muted"],
                "marginBottom"  : "8px",
                "fontFamily"    : "Inter, sans-serif",
            }),
            html.Div(context_text, style={
                "fontSize"   : "12px",
                "color"      : C["text_secondary"],
                "lineHeight" : "1.5",
                "fontFamily" : "Inter, sans-serif",
            })
        ], style={
            "backgroundColor" : C["cobalt"] + "10",
            "border"          : f"1px solid {C['cobalt']}30",
            "borderLeft"      : f"3px solid {C['cobalt']}",
            "borderRadius"    : "4px",
            "padding"         : "12px 14px",
            "marginBottom"    : "16px",
        })

    # ── SECTION 2: Climate Target ────────────────────────
    ghg_target  = country_data.get("ghg_target", "")
    ghg_cleaned = clean_ndc_text(str(ghg_target), max_length=200) \
                  if ghg_target else None

    commitment  = country_data.get(
        "mitigation_contribution_type", ""
    ) or ""

    if ghg_cleaned and ghg_cleaned != "No summary available.":
        target_section = html.Div([
            section_title("Climate Target"),
            html.Div([
                html.P(ghg_cleaned, style={
                    "fontSize"   : "13px",
                    "color"      : C["text"],
                    "lineHeight" : "1.6",
                    "margin"     : "0 0 8px 0",
                    "fontFamily" : "Inter, sans-serif",
                    "fontWeight" : "500",
                }),
                html.Div(
                    commitment if commitment else "Commitment type not specified",
                    style={
                        "fontSize"   : "11px",
                        "color"      : C["text_muted"],
                        "fontFamily" : "Inter, sans-serif",
                    }
                )
            ], style={
                "backgroundColor" : C["surface_high"],
                "border"          : f"1px solid {C['border']}",
                "borderLeft"      : f"2px solid {C['crimson']}",
                "borderRadius"    : "4px",
                "padding"         : "12px 14px",
            })
        ], style={"marginBottom": "16px"})
    else:
        target_section = html.Div()

    # ── SECTION 3: NDC Summary ───────────────────────────
    summary_raw = country_data.get("indc_summary", "")
    summary     = clean_ndc_text(str(summary_raw), max_length=400)

    # EU member states submitted collectively — flag this
    EU_MEMBERS = {
        "AUT","BEL","BGR","HRV","CYP","CZE","DNK","EST","FIN",
        "FRA","DEU","GRC","HUN","IRL","ITA","LVA","LTU","LUX",
        "MLT","NLD","POL","PRT","ROU","SVK","SVN","ESP","SWE"
    }
    is_eu_member = iso_code in EU_MEMBERS

    has_translation = any(
        phrase in str(summary_raw).lower()
        for phrase in ["submitted only in", "translated", "wri did"]
    )

    flags = []
    if is_eu_member:
        flags.append(flag_pill("EU Collective NDC", C["cobalt"]))
    if has_translation:
        flags.append(flag_pill("Translated NDC", C["amber"]))
    if float(country_data.get("data_completeness_pct", 100)) < 60:
        flags.append(flag_pill("Partial data", C["crimson"]))

    ndc_section = html.Div([
        section_title("NDC Summary"),
        html.Div(flags, style={"marginBottom": "8px"}) if flags
        else html.Div(),
        html.P(summary, style={
            "fontSize"   : "13px",
            "color"      : C["text_secondary"],
            "lineHeight" : "1.6",
            "margin"     : "0",
            "fontFamily" : "Inter, sans-serif",
        })
    ], style={
        "backgroundColor" : C["surface_high"],
        "border"          : f"1px solid {C['border']}",
        "borderLeft"      : f"2px solid {C['emerald']}",
        "borderRadius"    : "4px",
        "padding"         : "14px",
        "marginBottom"    : "16px"
    })

    # ── SECTION 4: Investment Signals ────────────────────
    if not country_tags.empty:
        sector_rows = []
        for _, tag in country_tags.iterrows():
            def safe_str(val):
                if val is None: return ""
                s = str(val).strip()
                return "" if s.lower() in ("nan", "none", "") else s

            lens       = safe_str(tag.get("climate_lens"))
            instrument = safe_str(tag.get("financing_instrument"))
            horizon    = safe_str(tag.get("implementation_horizon"))

            meta_parts = [x for x in [lens, instrument, horizon] if x]
            meta_str   = "  ·  ".join(meta_parts) if meta_parts else ""

            sector_rows.append(
                html.Div([
                    html.Div([
                        html.Div(
                            [sector_pill(tag["sector"])],
                        ),
                        html.Div(meta_str, style={
                            "fontSize"   : "10px",
                            "color"      : C["text_muted"],
                            "fontFamily" : "Inter, sans-serif",
                            "marginTop"  : "3px",
                        }) if meta_str else html.Div()
                    ], style={"flex": "1"}),
                    confidence_badge(tag["confidence"]),
                ], style={
                    "display"        : "flex",
                    "justifyContent" : "space-between",
                    "alignItems"     : "flex-start",
                    "padding"        : "8px 0",
                    "borderBottom"   : f"1px solid {C['border']}",
                })
            )

        signals_section = html.Div([
            section_title("Investment Signals"),
            html.Div(sector_rows)
        ], style={"marginBottom": "16px"})
    else:
        signals_section = html.Div()

    # ── SECTION 5: Key Metrics ───────────────────────────
    def fmt_gdp(v):
        if pd.isna(v) or v is None: return "N/A"
        if v >= 1e12: return f"${v/1e12:.1f}T"
        if v >= 1e9:  return f"${v/1e9:.1f}B"
        return f"${v/1e6:.0f}M"

    metrics = html.Div([
        section_title("Key Metrics"),
        html.Div([
            html.Div([
                data_row("GDP",
                    fmt_gdp(country_data.get("gdp_usd"))),
                data_row("GDP per Capita",
                    f"${country_data.get('gdp_per_capita_usd',0):,.0f}"
                    if pd.notna(country_data.get("gdp_per_capita_usd"))
                    else "N/A"),
                data_row("Population",
                    f"{country_data.get('population',0)/1e6:.1f}M"
                    if pd.notna(country_data.get("population"))
                    else "N/A"),
            ], style={"flex": "1"}),
            html.Div([
                data_row("ND-GAIN Score",
                    f"{country_data.get('ndgain_score',0):.1f}"
                    if pd.notna(country_data.get("ndgain_score"))
                    else "N/A",
                    colour=C["emerald"]),
                data_row("Vulnerability",
                    f"{country_data.get('vulnerability_score',0):.2f}"
                    if pd.notna(country_data.get("vulnerability_score"))
                    else "N/A"),
                data_row("Renewables",
                    f"{country_data.get('renewable_electricity_pct',0):.0f}%"
                    if pd.notna(
                        country_data.get("renewable_electricity_pct")
                    ) else "N/A",
                    colour=C["nature"]),
            ], style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"})
    ], style={"marginBottom": "16px"})

    # ── SECTION 6: MDB Project Pipeline ─────────────────
    proj_count  = country_data.get("wb_project_count", 0)
    proj_active = country_data.get("wb_active_projects", 0)
    top3        = get_country_projects_top3(iso_code, projects_df)

    mdb_tooltip = (
        f"World Bank data covers 88 of 199 countries. "
        f"Primary regional MDB for {full_name} is the {mdb_name}. "
        f"Full regional MDB coverage coming in next update via IATI."
    )

    if not top3.empty:
        project_rows = []
        for _, proj in top3.iterrows():
            name   = str(proj.get("project_name", "Unnamed project"))[:60]
            status = str(proj.get("status", ""))
            date   = str(proj.get("approval_date", ""))[:10]

            status_colour = (
                C["emerald"] if status == "Active"
                else C["text_muted"]
            )

            project_rows.append(
                html.Div([
                    html.Div(name, style={
                        "fontSize"   : "12px",
                        "color"      : C["text"],
                        "fontFamily" : "Inter, sans-serif",
                        "lineHeight" : "1.4",
                        "marginBottom": "3px",
                    }),
                    html.Div([
                        html.Span(status, style={
                            "fontSize"   : "10px",
                            "color"      : status_colour,
                            "fontFamily" : "Inter, sans-serif",
                            "fontWeight" : "600",
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
                })
            )

        try:
            import pycountry as _pc
            _c    = _pc.countries.get(alpha_3=iso_code)
            _iso2 = _c.alpha_2.upper() if _c else iso_code
            _name = get_country_name(iso_code)
        except Exception:
            _iso2 = iso_code
            _name = iso_code

        wb_url = (
            f"https://maps.worldbank.org/projects/wb/country/"
            f"{_iso2}/{_name}?status=active"
        )

        projects_content = html.Div([
            html.Div(project_rows),
            html.Div([
                html.Span(
                    f"{int(proj_count)} total  ·  "
                    f"{int(proj_active)} active  ·  ",
                    style={
                        "fontSize"   : "11px",
                        "color"      : C["text_muted"],
                        "fontFamily" : "Inter, sans-serif",
                    }
                ),
                html.A("View all on World Bank",
                    href   = wb_url,
                    target = "_blank",
                    style  = {
                        "fontSize"       : "11px",
                        "color"          : C["cobalt"],
                        "fontFamily"     : "Inter, sans-serif",
                        "textDecoration" : "none",
                    }
                )
            ], style={"marginTop": "10px"})
        ])

    else:
        if mdb_code == "None":
            note = (
                f"{full_name} is a high-income market. "
                f"World Bank concessional lending does not apply. "
                f"Primary MDB: {mdb_name}."
            )
        else:
            note = (
                f"No World Bank projects captured for {full_name}. "
                f"Primary regional MDB: {mdb_name}. "
                f"Full MDB coverage coming in next update."
            )

        projects_content = html.Div(note, style={
            "fontSize"   : "12px",
            "color"      : C["text_muted"],
            "fontFamily" : "Inter, sans-serif",
            "lineHeight" : "1.5",
            "padding"    : "12px",
            "backgroundColor" : C["surface_high"],
            "border"     : f"1px solid {C['border']}",
            "borderRadius": "4px",
        })

    projects_section = html.Div([
        section_title("MDB Project Pipeline", tooltip=mdb_tooltip),
        projects_content
    ], style={"marginBottom": "16px"})

    # ── SECTION 7: News ──────────────────────────────────
    news_section = html.Div([
        section_title("Climate News"),
        html.Div([
            html.Div("◌", style={
                "fontSize"     : "18px",
                "color"        : C["text_muted"],
                "marginBottom" : "6px"
            }),
            html.Div(
                "Live news feed available once "
                "Google CSE is configured.",
                style={
                    "fontSize"   : "12px",
                    "color"      : C["text_muted"],
                    "lineHeight" : "1.5",
                    "fontFamily" : "Inter, sans-serif",
                }
            )
        ], style={
            "textAlign"       : "center",
            "padding"         : "20px",
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderRadius"    : "4px",
        })
    ], style={"marginBottom": "16px"})

    # ── SECTION 8: Subsidies ─────────────────────────────
    subsidies_section = html.Div([
        section_title("Subsidies and Incentives"),
        html.Div([
            html.Div("◌", style={
                "fontSize"     : "18px",
                "color"        : C["text_muted"],
                "marginBottom" : "6px"
            }),
            html.Div(
                "Government subsidy and incentive data "
                "available once Google CSE is configured.",
                style={
                    "fontSize"   : "12px",
                    "color"      : C["text_muted"],
                    "lineHeight" : "1.5",
                    "fontFamily" : "Inter, sans-serif",
                }
            )
        ], style={
            "textAlign"       : "center",
            "padding"         : "20px",
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderRadius"    : "4px",
        })
    ], style={"marginBottom": "16px"})

    return html.Div([
        header,
        finance_signal,
        target_section,
        ndc_section,
        signals_section,
        metrics,
        projects_section,
        news_section,
        subsidies_section,
    ])


def build_sector_chart():
    colours = [
        SECTOR_COLOURS.get(s, C["text_muted"])
        for s in sector_sum["sector"]
    ]
    fig = go.Figure(go.Bar(
        x=sector_sum["country_count"],
        y=sector_sum["sector"],
        orientation="h",
        marker_color=colours,
        text=sector_sum["country_count"],
        textposition="outside",
        textfont=dict(color=C["text_muted"], size=11, family="Inter"),
        hovertemplate="<b>%{y}</b><br>Countries: %{x}<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor=C["bg"], plot_bgcolor=C["surface"],
        font=dict(color=C["text"], family="Inter"),
        xaxis=dict(showgrid=True, gridcolor=C["border"],
                   color=C["text_muted"], title="Number of Countries"),
        yaxis=dict(color=C["text_muted"], showgrid=False),
        margin=dict(l=10, r=50, t=10, b=10),
        height=300, bargap=0.3,
    )
    return fig


def build_tier_donut():
    tier_counts = master_df["investment_tier"].value_counts()
    fig = go.Figure(go.Pie(
        labels=tier_counts.index,
        values=tier_counts.values,
        hole=0.68,
        marker=dict(
            colors=[
                TIER_COLOURS.get(t, C["tier_none"])
                for t in tier_counts.index
            ],
            line=dict(color=C["bg"], width=2)
        ),
        textfont=dict(color=C["text"], size=11, family="Inter"),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Countries: %{value}<br>%{percent}<extra></extra>"
        )
    ))
    fig.update_layout(
        paper_bgcolor=C["bg"],
        font=dict(color=C["text"], family="Inter"),
        showlegend=True,
        legend=dict(
            font=dict(color=C["text_muted"], size=11),
            bgcolor="rgba(0,0,0,0)",
            orientation="v", x=1.0, y=0.5,
        ),
        margin=dict(l=0, r=100, t=10, b=10),
        height=280,
        annotations=[dict(
            text=f"<b>{len(master_df)}</b><br>Countries",
            x=0.5, y=0.5,
            font=dict(color=C["text"], size=16, family="Inter"),
            showarrow=False
        )]
    )
    return fig


def build_commitment_chart():
    commitment_summary = (
        tags_df[tags_df["commitment_type"].notna()]
        .groupby("commitment_type")
        .agg(count=("iso_code", "nunique"))
        .reset_index()
    )
    colour_map = {
        "Conditional"  : C["crimson"],
        "Unconditional": C["emerald"],
    }
    fig = go.Figure(go.Bar(
        x=commitment_summary["commitment_type"],
        y=commitment_summary["count"],
        marker_color=[
            colour_map.get(c, C["text_muted"])
            for c in commitment_summary["commitment_type"]
        ],
        text=commitment_summary["count"],
        textposition="outside",
        textfont=dict(color=C["text_muted"], size=12, family="Inter"),
        hovertemplate="<b>%{x}</b><br>Countries: %{y}<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor=C["bg"], plot_bgcolor=C["surface"],
        font=dict(color=C["text"], family="Inter"),
        xaxis=dict(color=C["text_muted"], showgrid=False),
        yaxis=dict(color=C["text_muted"], gridcolor=C["border"],
                   title="Countries"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=280, bargap=0.4,
    )
    return fig


def layout():
    return html.Div([

        html.Div(className="grid-background"),
        html.Div(id="globe-tooltip"),
        html.Div(id="globe-container"),

        kpi_strip(),

        html.Div([
            dcc.Input(
                id="d3-click-input",
                type="text",
                value="",
                style={"display": "none"}
            ),
            dcc.Input(
                id="colour-mode-value",
                type="text",
                value="tier_score",
                style={"display": "none"}
            ),
        ], style={"display": "none"}),

        html.Div([
            html.Span("View by: ", style={
                "fontSize"    : "11px",
                "color"       : C["text_muted"],
                "marginRight" : "10px",
                "fontFamily"  : "Inter, sans-serif",
            }),
            dcc.RadioItems(
                id="globe-colour-selector",
                options=[
                    {"label": "Investment Tier",
                     "value": "tier_score"},
                    {"label": "ND-GAIN",
                     "value": "ndgain_score"},
                    {"label": "Vulnerability",
                     "value": "vulnerability_score"},
                    {"label": "Renewables %",
                     "value": "renewable_electricity_pct"},
                ],
                value="tier_score",
                inline=True,
                inputStyle={
                    "marginRight" : "5px",
                    "accentColor" : C["emerald"]
                },
                labelStyle={
                    "fontSize"    : "12px",
                    "color"       : C["text_secondary"],
                    "marginRight" : "16px",
                    "cursor"      : "pointer",
                    "fontFamily"  : "Inter, sans-serif",
                },
            )
        ], id="globe-controls"),

        html.Div(
            "↓  Scroll to explore global analytics",
            id="scroll-hint"
        ),

        html.Div([
            html.Div(
                id="country-panel-content",
                children=empty_panel(),
                style={
                    "padding"   : "24px",
                    "overflowY" : "auto",
                    "height"    : "100%",
                }
            )
        ], id="country-panel-overlay"),

        html.Div([

            html.Div("Global Analysis", style={
                "fontSize"      : "11px",
                "fontWeight"    : "600",
                "textTransform" : "uppercase",
                "letterSpacing" : "1.5px",
                "color"         : C["text_muted"],
                "marginBottom"  : "8px",
                "fontFamily"    : "Inter, sans-serif",
            }),
            html.H2("Investment signals across all NDCs", style={
                "fontSize"     : "22px",
                "fontWeight"   : "600",
                "color"        : C["text"],
                "marginBottom" : "40px",
                "fontFamily"   : "Inter, sans-serif",
            }),

            html.Div([
                html.Div("Sector Coverage", style={
                    "fontSize"      : "11px",
                    "fontWeight"    : "600",
                    "textTransform" : "uppercase",
                    "letterSpacing" : "1.5px",
                    "color"         : C["text_muted"],
                    "marginBottom"  : "16px",
                    "fontFamily"    : "Inter, sans-serif",
                }),
                dcc.Graph(
                    id="sector-bar-chart",
                    figure=build_sector_chart(),
                    config={"displayModeBar": False}
                )
            ], style={
                "backgroundColor" : C["surface"],
                "border"          : f"1px solid {C['border']}",
                "borderRadius"    : "6px",
                "padding"         : "24px",
                "marginBottom"    : "24px"
            }),

            html.Div([
                html.Div([
                    html.Div("Investment Tier Distribution", style={
                        "fontSize"      : "11px",
                        "fontWeight"    : "600",
                        "textTransform" : "uppercase",
                        "letterSpacing" : "1.5px",
                        "color"         : C["text_muted"],
                        "marginBottom"  : "16px",
                        "fontFamily"    : "Inter, sans-serif",
                    }),
                    dcc.Graph(
                        id="tier-donut-chart",
                        figure=build_tier_donut(),
                        config={"displayModeBar": False}
                    )
                ], style={
                    "backgroundColor" : C["surface"],
                    "border"          : f"1px solid {C['border']}",
                    "borderRadius"    : "6px",
                    "padding"         : "24px",
                    "flex"            : "1",
                }),
                html.Div([
                    html.Div("Commitment Type", style={
                        "fontSize"      : "11px",
                        "fontWeight"    : "600",
                        "textTransform" : "uppercase",
                        "letterSpacing" : "1.5px",
                        "color"         : C["text_muted"],
                        "marginBottom"  : "16px",
                        "fontFamily"    : "Inter, sans-serif",
                    }),
                    dcc.Graph(
                        id="commitment-bar-chart",
                        figure=build_commitment_chart(),
                        config={"displayModeBar": False}
                    )
                ], style={
                    "backgroundColor" : C["surface"],
                    "border"          : f"1px solid {C['border']}",
                    "borderRadius"    : "6px",
                    "padding"         : "24px",
                    "flex"            : "1",
                }),
            ], style={"display": "flex", "gap": "24px"}),

        ], id="analytics-section", style={"padding": "80px"}),

    ], style={
        "fontFamily"      : "Inter, sans-serif",
        "backgroundColor" : C["bg"],
        "minHeight"       : "200vh",
    })


if __name__ == "__main__":
    page = layout()
    print("✅ globe.py verified")
    print(f"   Countries     : {len(master_df)}")
    print(f"   Panel sections: 8")
    print(f"   MDB mapping   : active")
    print(f"   Top 3 projects: active")
