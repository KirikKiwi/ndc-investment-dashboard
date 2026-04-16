# ============================================================
# NDC Investment Dashboard
# pages/globe.py — Interactive 3D globe + country panel
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from components import C, T, SECTOR_COLOURS, TIER_COLOURS
from components import (confidence_badge, sector_pill, tier_badge,
                        data_row, divider, flag_pill, empty_state)
from data import (load_master, load_tags, load_projects,
                  prepare_map_data, get_global_kpis,
                  get_sector_summary)

# ============================================================
# LOAD DATA
# ============================================================

master_df   = load_master()
tags_df     = load_tags()
projects_df = load_projects()
map_df      = prepare_map_data(master_df, tags_df)
kpis        = get_global_kpis(master_df, tags_df)
sector_sum  = get_sector_summary(tags_df)

# ============================================================
# GLOBE FIGURE
# ============================================================

COLOUR_OPTIONS = {
    "tier_score": {
        "label"     : "Investment Tier",
        "colorscale": [
            [0.00, "#1a1a1a"],
            [0.33, C["crimson"]],
            [0.66, C["amber"]],
            [1.00, C["emerald"]],
        ],
        "range"     : [0, 3],
        "tickvals"  : [0, 1, 2, 3],
        "ticktext"  : ["No data", "Frontier",
                       "Emerging", "Established"],
    },
    "ndgain_score": {
        "label"     : "ND-GAIN Score",
        "colorscale": "RdYlGn",
        "range"     : [20, 75],
        "tickvals"  : None,
        "ticktext"  : None,
    },
    "vulnerability_score": {
        "label"     : "Climate Vulnerability",
        "colorscale": "RdYlGn_r",
        "range"     : [0.2, 0.7],
        "tickvals"  : None,
        "ticktext"  : None,
    },
    "renewable_electricity_pct": {
        "label"     : "Renewable Electricity %",
        "colorscale": [
            [0.0, "#1a1a1a"],
            [0.5, C["cobalt"]],
            [1.0, C["emerald"]],
        ],
        "range"     : [0, 100],
        "tickvals"  : None,
        "ticktext"  : None,
    },
}


def build_globe(colour_by="tier_score", projection="orthographic"):
    cfg = COLOUR_OPTIONS.get(colour_by, COLOUR_OPTIONS["tier_score"])

    colorbar_config = dict(
        title=dict(
            text=cfg["label"],
            font=dict(color=C["text_muted"], size=11,
                      family="Inter, sans-serif")
        ),
        tickfont=dict(color=C["text_muted"], size=10,
                      family="Inter, sans-serif"),
        bgcolor=C["surface"],
        bordercolor=C["border"],
        borderwidth=1,
        thickness=10,
        len=0.5,
        x=0.98,
    )

    if cfg["tickvals"]:
        colorbar_config["tickvals"] = cfg["tickvals"]
        colorbar_config["ticktext"] = cfg["ticktext"]

    fig = go.Figure(go.Choropleth(
        locations         = map_df["iso_code"],
        z                 = map_df[colour_by],
        text              = map_df["hover_text"],
        hovertemplate     = "%{text}<extra></extra>",
        colorscale        = cfg["colorscale"],
        zmin              = cfg["range"][0],
        zmax              = cfg["range"][1],
        marker_line_color = "#000000",
        marker_line_width = 0.3,
        colorbar          = colorbar_config,
    ))

    fig.update_layout(
        geo=dict(
            showframe       = False,
            showcoastlines  = True,
            coastlinecolor  = "#333333",
            showland        = True,
            landcolor       = C["surface_high"],
            showocean       = True,
            oceancolor      = "#0a0a0a",
            showlakes       = False,
            showcountries   = True,
            countrycolor    = "#1a1a1a",
            bgcolor         = C["bg"],
            projection_type = projection,
            projection_rotation = dict(lon=0, lat=20, roll=0),
            lataxis         = dict(showgrid=True,
                                   gridcolor="#1a1a1a"),
            lonaxis         = dict(showgrid=True,
                                   gridcolor="#1a1a1a"),
        ),
        paper_bgcolor = C["bg"],
        plot_bgcolor  = C["bg"],
        margin        = dict(l=0, r=0, t=0, b=0),
        height        = 620,
        dragmode      = "orbit" if projection == "orthographic"
                        else "pan",
        font          = dict(family="Inter, sans-serif"),
    )

    return fig

# ============================================================
# KPI STRIP
# ============================================================

def kpi_strip():
    """Compact KPI row above the globe."""
    items = [
        ("NDC Countries",     str(kpis["total_countries"]),
         C["emerald"]),
        ("Conditional Signals",
         str(kpis["conditional_countries"]),     C["crimson"]),
        ("Avg ND-GAIN",       str(kpis["avg_ndgain"]),
         C["amber"]),
        ("WB Projects",       str(kpis["total_projects"]),
         C["cobalt"]),
        ("Established",       str(kpis["tier1_count"]),
         C["tier1"]),
        ("Emerging",          str(kpis["tier2_count"]),
         C["tier2"]),
        ("Frontier",          str(kpis["tier3_count"]),
         C["tier3"]),
        ("Avg Renewables",    f"{kpis['avg_renewable']}%",
         C["nature"]),
    ]

    return html.Div([
        html.Div([
            html.Div([
                html.Div(value, style={
                    "fontSize"     : "20px",
                    "fontWeight"   : "700",
                    "color"        : colour,
                    "fontFamily"   : "Inter, sans-serif",
                    "lineHeight"   : "1",
                    "marginBottom" : "4px"
                }),
                html.Div(label, style={
                    **T["micro"],
                    "color" : C["text_muted"]
                })
            ], style={
                "textAlign"   : "center",
                "padding"     : "12px 20px",
                "borderRight" : (
                    f"1px solid {C['border']}"
                    if i < len(items) - 1 else "none"
                ),
                "flexShrink"  : "0",
            })
            for i, (label, value, colour) in enumerate(items)
        ], style={
            "display"        : "flex",
            "overflowX"      : "auto",
            "justifyContent" : "space-between",
        })
    ], style={
        "backgroundColor" : C["surface"],
        "borderTop"       : f"1px solid {C['border']}",
        "borderBottom"    : f"1px solid {C['border']}",
    })


# ============================================================
# COLOUR SELECTOR PILLS
# ============================================================

def colour_selector():
    """Pill buttons to switch globe colour mode."""
    return html.Div([
        html.Span("View by: ", style={
            **T["micro"],
            "color"       : C["text_muted"],
            "marginRight" : "10px",
            "lineHeight"  : "28px"
        }),
        dcc.RadioItems(
            id      = "globe-colour-selector",
            options = [
                {"label": "Investment Tier",
                 "value": "tier_score"},
                {"label": "ND-GAIN Score",
                 "value": "ndgain_score"},
                {"label": "Vulnerability",
                 "value": "vulnerability_score"},
                {"label": "Renewables %",
                 "value": "renewable_electricity_pct"},
            ],
            value          = "tier_score",
            inline         = True,
            inputStyle     = {"marginRight": "5px",
                              "accentColor": C["emerald"]},
            labelStyle     = {
                **T["small"],
                "color"       : C["text_secondary"],
                "marginRight" : "16px",
                "cursor"      : "pointer",
            },
        )
    ], style={
        "display"     : "flex",
        "alignItems"  : "center",
        "padding"     : "10px 0",
    })


# ============================================================
# PROJECTION TOGGLE
# ============================================================

def projection_toggle():
    """Switch between 3D globe and flat map."""
    return html.Div([
        html.Span("View: ", style={
            **T["micro"],
            "color"       : C["text_muted"],
            "marginRight" : "8px",
            "lineHeight"  : "28px"
        }),
        dcc.RadioItems(
            id      = "projection-selector",
            options = [
                {"label": "🌐 Globe",
                 "value": "orthographic"},
                {"label": "🗺 Flat Map",
                 "value": "natural earth"},
            ],
            value      = "orthographic",
            inline     = True,
            inputStyle = {"marginRight": "4px",
                          "accentColor": C["emerald"]},
            labelStyle = {
                **T["small"],
                "color"       : C["text_secondary"],
                "marginRight" : "16px",
                "cursor"      : "pointer",
            },
        )
    ], style={
        "display"    : "flex",
        "alignItems" : "center",
        "padding"    : "10px 0",
    })


# ============================================================
# COUNTRY PANEL (shown on country click)
# ============================================================

def empty_panel():
    """Shown before any country is selected."""
    return html.Div([
        html.Div("◎", style={
            "fontSize"     : "32px",
            "color"        : C["text_muted"],
            "marginBottom" : "16px"
        }),
        html.Div("Select a country", style={
            **T["h3"],
            "color"        : C["text_secondary"],
            "marginBottom" : "8px"
        }),
        html.Div(
            "Click any country on the globe to view "
            "its NDC investment profile.",
            style={
                **T["small"],
                "color"      : C["text_muted"],
                "lineHeight" : "1.6"
            }
        )
    ], style={
        "textAlign" : "center",
        "padding"   : "60px 24px"
    })


def country_panel_content(iso_code):
    """
    Populated panel for a selected country.
    Queries all data for that ISO code.
    """
    from data import get_country_detail, get_country_sectors

    country_data, country_tags = get_country_detail(
        iso_code, master_df, tags_df
    )

    if country_data is None:
        return empty_state("Country not found")

    # ── Header ──
    header = html.Div([
        html.Div([
            html.Div(iso_code, style={
                **T["h1"],
                "color"        : C["text"],
                "marginBottom" : "4px"
            }),
            tier_badge(
                country_data.get("investment_tier", "N/A")
            ),
        ]),
        html.Div("×", id="close-panel-btn", style={
            "fontSize"  : "24px",
            "color"     : C["text_muted"],
            "cursor"    : "pointer",
            "padding"   : "4px 8px",
            "lineHeight": "1"
        })
    ], style={
        "display"        : "flex",
        "justifyContent" : "space-between",
        "alignItems"     : "flex-start",
        "marginBottom"   : "20px"
    })

    # ── NDC Summary ──
    summary = country_data.get("indc_summary", "")
    if summary and len(str(summary)) > 10:
        # Clean HTML tags if present
        import re
        clean = re.sub(r'<[^>]+>', '', str(summary))
        clean = clean[:400] + "..." if len(clean) > 400 else clean
        ndc_section = html.Div([
            html.Div("NDC Summary", style={
                **T["label"],
                "color"        : C["text_muted"],
                "marginBottom" : "8px"
            }),
            html.P(clean, style={
                **T["small"],
                "color"        : C["text_secondary"],
                "lineHeight"   : "1.6",
                "marginBottom" : "0"
            })
        ], style={
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderLeft"      : f"2px solid {C['emerald']}",
            "borderRadius"    : "4px",
            "padding"         : "14px",
            "marginBottom"    : "20px"
        })
    else:
        ndc_section = html.Div()

    # ── Flags ──
    flags = []
    if country_data.get("translation_flag"):
        flags.append(flag_pill("⚠ Translated NDC", C["amber"]))
    if float(country_data.get("data_completeness_pct", 100)) < 60:
        flags.append(flag_pill("⚠ Partial data", C["crimson"]))

    flags_row = html.Div(flags,
                         style={"marginBottom": "16px"}) if flags \
        else html.Div()

    # ── Key Metrics ──
    def fmt_gdp(v):
        if pd.isna(v) or v is None: return "N/A"
        if v >= 1e12: return f"${v/1e12:.1f}T"
        if v >= 1e9:  return f"${v/1e9:.1f}B"
        return f"${v/1e6:.0f}M"

    metrics = html.Div([
        html.Div("Key Metrics", style={
            **T["label"],
            "color"        : C["text_muted"],
            "marginBottom" : "12px"
        }),
        html.Div([
            html.Div([
                data_row("GDP",
                         fmt_gdp(country_data.get("gdp_usd"))),
                data_row("GDP per Capita",
                         f"${country_data.get('gdp_per_capita_usd', 0):,.0f}"
                         if pd.notna(
                             country_data.get("gdp_per_capita_usd")
                         ) else "N/A"),
                data_row("Population",
                         f"{country_data.get('population', 0)/1e6:.1f}M"
                         if pd.notna(country_data.get("population"))
                         else "N/A"),
            ], style={"flex": "1"}),
            html.Div([
                data_row("ND-GAIN Score",
                         f"{country_data.get('ndgain_score', 0):.1f}"
                         if pd.notna(
                             country_data.get("ndgain_score")
                         ) else "N/A",
                         colour=C["emerald"]),
                data_row("Vulnerability",
                         f"{country_data.get('vulnerability_score', 0):.2f}"
                         if pd.notna(
                             country_data.get("vulnerability_score")
                         ) else "N/A"),
                data_row("Renewables",
                         f"{country_data.get('renewable_electricity_pct', 0):.0f}%"
                         if pd.notna(
                             country_data.get(
                                 "renewable_electricity_pct")
                         ) else "N/A",
                         colour=C["nature"]),
            ], style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"})
    ], style={"marginBottom": "20px"})

    # ── Sectors ──
    if not country_tags.empty:
        sector_rows = []
        for _, tag in country_tags.iterrows():
            sector_rows.append(
                html.Div([
                    html.Div([
                        sector_pill(tag["sector"]),
                    ], style={"flex": "1"}),
                    html.Div([
                        confidence_badge(tag["confidence"])
                    ]),
                ], style={
                    "display"       : "flex",
                    "justifyContent": "space-between",
                    "alignItems"    : "center",
                    "padding"       : "8px 0",
                    "borderBottom"  : f"1px solid {C['border']}",
                })
            )

        sectors_section = html.Div([
            html.Div("Identified Sectors", style={
                **T["label"],
                "color"        : C["text_muted"],
                "marginBottom" : "12px"
            }),
            html.Div(sector_rows)
        ], style={"marginBottom": "20px"})
    else:
        sectors_section = html.Div()

    # ── WB Projects ──
    proj_count  = country_data.get("wb_project_count", 0)
    proj_total  = country_data.get("wb_total_commitment_usd", 0)
    proj_active = country_data.get("wb_active_projects", 0)

    projects_section = html.Div([
        html.Div("World Bank Pipeline", style={
            **T["label"],
            "color"        : C["text_muted"],
            "marginBottom" : "12px"
        }),
        html.Div([
            html.Div([
                html.Div(str(int(proj_count)) if pd.notna(proj_count)
                         else "0", style={
                    "fontSize"     : "24px",
                    "fontWeight"   : "700",
                    "color"        : C["cobalt"],
                    "fontFamily"   : "Inter, sans-serif"
                }),
                html.Div("Total Projects", style={
                    **T["micro"],
                    "color": C["text_muted"]
                })
            ], style={"textAlign": "center", "flex": "1"}),
            html.Div([
                html.Div(str(int(proj_active))
                         if pd.notna(proj_active) else "0", style={
                    "fontSize"     : "24px",
                    "fontWeight"   : "700",
                    "color"        : C["emerald"],
                    "fontFamily"   : "Inter, sans-serif"
                }),
                html.Div("Active", style={
                    **T["micro"],
                    "color": C["text_muted"]
                })
            ], style={"textAlign": "center", "flex": "1"}),
        ], style={
            "display"         : "flex",
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderRadius"    : "4px",
            "padding"         : "16px",
        })
    ], style={"marginBottom": "20px"})

    # ── News placeholder ──
    news_section = html.Div([
        html.Div("Latest News & Subsidies", style={
            **T["label"],
            "color"        : C["text_muted"],
            "marginBottom" : "12px"
        }),
        html.Div([
            html.Div("◌", style={
                "fontSize"     : "20px",
                "color"        : C["text_muted"],
                "marginBottom" : "8px"
            }),
            html.Div(
                "News and subsidy search will be available "
                "once Google CSE is configured.",
                style={
                    **T["small"],
                    "color"      : C["text_muted"],
                    "lineHeight" : "1.5"
                }
            )
        ], style={
            "textAlign"       : "center",
            "padding"         : "24px",
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderRadius"    : "4px",
            "borderStyle"     : "dashed",
        })
    ])

    return html.Div([
        header,
        flags_row,
        ndc_section,
        metrics,
        sectors_section,
        projects_section,
        news_section,
    ])


# ============================================================
# FULL PAGE LAYOUT
# ============================================================

def layout():
    return html.Div([

        # ── KPI Strip ────────────────────────────────────────
        kpi_strip(),

        # ── Globe + Panel Row ─────────────────────────────────
        html.Div([

            # Left — Globe
            html.Div([

                # Controls bar
                html.Div([
                    colour_selector(),
                    projection_toggle(),
                ], style={
                    "display"        : "flex",
                    "justifyContent" : "space-between",
                    "alignItems"     : "center",
                    "padding"        : "0 16px",
                    "borderBottom"   : f"1px solid {C['border']}",
                    "backgroundColor": C["surface"],
                }),

                # Globe
                dcc.Graph(
                    id     = "globe-map",
                    figure = build_globe(),
                    config = {
                        "displayModeBar"  : True,
                        "displaylogo"     : False,
                        "modeBarButtonsToRemove": [
                            "select2d", "lasso2d",
                            "toggleSpikelines"
                        ],
                        "scrollZoom"      : True,
                    },
                    style  = {
                        "cursor"     : "pointer",
                        "flex"       : "1",
                    }
                ),

                # Instructions
                html.Div(
                    "🖱  Drag to rotate · Scroll to zoom · "
                    "Click a country to open its profile",
                    style={
                        **T["micro"],
                        "color"     : C["text_muted"],
                        "textAlign" : "center",
                        "padding"   : "10px",
                        "borderTop" : f"1px solid {C['border']}",
                    }
                )

            ], style={
                "flex"            : "1",
                "display"         : "flex",
                "flexDirection"   : "column",
                "backgroundColor" : C["bg"],
                "borderRight"     : f"1px solid {C['border']}",
                "minWidth"        : "0",
            }),

            # Right — Country Panel
            html.Div([
                html.Div(
                    id    = "country-panel-content",
                    children = empty_panel(),
                    style = {
                        "overflowY" : "auto",
                        "height"    : "100%",
                        "padding"   : "24px",
                    }
                )
            ], style={
                "width"           : "360px",
                "flexShrink"      : "0",
                "backgroundColor" : C["surface"],
                "borderLeft"      : f"1px solid {C['border']}",
                "height"          : "calc(100vh - 120px)",
                "overflowY"       : "auto",
                "position"        : "sticky",
                "top"             : "60px",
            }),

        ], style={
            "display"    : "flex",
            "minHeight"  : "calc(100vh - 60px)",
        }),

        # ── Analytics Section (scrolls into view) ─────────────
        html.Div([

            # Section header
            html.Div([
                html.Div("Global Analysis", style={
                    **T["label"],
                    "color"        : C["text_muted"],
                    "marginBottom" : "8px"
                }),
                html.H2("Investment signals across all NDCs", style={
                    **T["h2"],
                    "color"        : C["text"],
                    "marginBottom" : "40px"
                })
            ]),

            # Sector coverage chart
            html.Div([
                html.Div("Sector Coverage", style={
                    **T["label"],
                    "color"        : C["text_muted"],
                    "marginBottom" : "16px"
                }),
                dcc.Graph(
                    id     = "sector-bar-chart",
                    figure = build_sector_chart(),
                    config = {"displayModeBar": False}
                )
            ], style={
                "backgroundColor" : C["surface"],
                "border"          : f"1px solid {C['border']}",
                "borderRadius"    : "6px",
                "padding"         : "24px",
                "marginBottom"    : "24px"
            }),

            # Two column charts
            html.Div([

                # Tier distribution
                html.Div([
                    html.Div("Investment Tier Distribution", style={
                        **T["label"],
                        "color"        : C["text_muted"],
                        "marginBottom" : "16px"
                    }),
                    dcc.Graph(
                        id     = "tier-donut-chart",
                        figure = build_tier_donut(),
                        config = {"displayModeBar": False}
                    )
                ], style={
                    "backgroundColor" : C["surface"],
                    "border"          : f"1px solid {C['border']}",
                    "borderRadius"    : "6px",
                    "padding"         : "24px",
                    "flex"            : "1",
                }),

                # Commitment type
                html.Div([
                    html.Div("Commitment Type", style={
                        **T["label"],
                        "color"        : C["text_muted"],
                        "marginBottom" : "16px"
                    }),
                    dcc.Graph(
                        id     = "commitment-bar-chart",
                        figure = build_commitment_chart(),
                        config = {"displayModeBar": False}
                    )
                ], style={
                    "backgroundColor" : C["surface"],
                    "border"          : f"1px solid {C['border']}",
                    "borderRadius"    : "6px",
                    "padding"         : "24px",
                    "flex"            : "1",
                }),

            ], style={
                "display" : "flex",
                "gap"     : "24px",
            }),

        ], style={
            "padding"         : "80px",
            "backgroundColor" : C["bg"],
            "borderTop"       : f"1px solid {C['border']}",
        }),

    ], style={
        "fontFamily"      : "Inter, sans-serif",
        "backgroundColor" : C["bg"],
    })


# ============================================================
# CHART BUILDERS
# ============================================================

def build_sector_chart():
    import plotly.graph_objects as go

    colours = [SECTOR_COLOURS.get(s, C["text_muted"])
               for s in sector_sum["sector"]]

    fig = go.Figure(go.Bar(
        x            = sector_sum["country_count"],
        y            = sector_sum["sector"],
        orientation  = "h",
        marker_color = colours,
        text         = sector_sum["country_count"],
        textposition = "outside",
        textfont     = dict(color=C["text_muted"], size=11,
                            family="Inter"),
        hovertemplate = (
            "<b>%{y}</b><br>"
            "Countries: %{x}<extra></extra>"
        )
    ))

    fig.update_layout(
        paper_bgcolor = C["bg"],
        plot_bgcolor  = C["surface"],
        font          = dict(color=C["text"], family="Inter"),
        xaxis         = dict(
            showgrid    = True,
            gridcolor   = C["border"],
            color       = C["text_muted"],
            title       = "Number of Countries",
        ),
        yaxis         = dict(
            color    = C["text_muted"],
            showgrid = False,
        ),
        margin  = dict(l=10, r=50, t=10, b=10),
        height  = 300,
        bargap  = 0.3,
    )
    return fig


def build_tier_donut():
    import plotly.graph_objects as go

    tier_counts = master_df["investment_tier"].value_counts()

    fig = go.Figure(go.Pie(
        labels    = tier_counts.index,
        values    = tier_counts.values,
        hole      = 0.68,
        marker    = dict(
            colors = [TIER_COLOURS.get(t, C["tier_none"])
                      for t in tier_counts.index],
            line   = dict(color=C["bg"], width=2)
        ),
        textfont  = dict(color=C["text"], size=11,
                         family="Inter"),
        hovertemplate = (
            "<b>%{label}</b><br>"
            "Countries: %{value}<br>"
            "%{percent}<extra></extra>"
        )
    ))

    fig.update_layout(
        paper_bgcolor = C["bg"],
        font          = dict(color=C["text"], family="Inter"),
        showlegend    = True,
        legend        = dict(
            font        = dict(color=C["text_muted"], size=11),
            bgcolor     = "rgba(0,0,0,0)",
            orientation = "v",
            x=1.0, y=0.5,
        ),
        margin      = dict(l=0, r=100, t=10, b=10),
        height      = 280,
        annotations = [dict(
            text      = (f"<b>{len(master_df)}</b><br>"
                         f"<span style='font-size:11px'>"
                         f"Countries</span>"),
            x=0.5, y=0.5,
            font      = dict(color=C["text"], size=16,
                             family="Inter"),
            showarrow = False
        )]
    )
    return fig


def build_commitment_chart():
    import plotly.graph_objects as go

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
        x            = commitment_summary["commitment_type"],
        y            = commitment_summary["count"],
        marker_color = [
            colour_map.get(c, C["text_muted"])
            for c in commitment_summary["commitment_type"]
        ],
        text         = commitment_summary["count"],
        textposition = "outside",
        textfont     = dict(color=C["text_muted"], size=12,
                            family="Inter"),
        hovertemplate = (
            "<b>%{x}</b><br>Countries: %{y}<extra></extra>"
        )
    ))

    fig.update_layout(
        paper_bgcolor = C["bg"],
        plot_bgcolor  = C["surface"],
        font          = dict(color=C["text"], family="Inter"),
        xaxis         = dict(color=C["text_muted"],
                             showgrid=False),
        yaxis         = dict(color=C["text_muted"],
                             gridcolor=C["border"],
                             title="Countries"),
        margin  = dict(l=10, r=10, t=10, b=10),
        height  = 280,
        bargap  = 0.4,
    )
    return fig


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    fig = build_globe()
    page = layout()
    print("✅ globe.py verified")
    print(f"   Countries on globe : {len(map_df)}")
    print(f"   Colour options     : {len(COLOUR_OPTIONS)}")
    print(f"   Panel components   : header, metrics, "
          f"sectors, projects, news")
    print(f"   Analytics charts   : sector, tier, commitment")