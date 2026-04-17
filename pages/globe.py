# ============================================================
# NDC Investment Dashboard
# pages/globe.py — D3 globe integration + country panel
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
                  get_country_detail, get_country_name)

master_df   = load_master()
tags_df     = load_tags()
projects_df = load_projects()
map_df      = prepare_map_data(master_df, tags_df)
kpis        = get_global_kpis(master_df, tags_df)
sector_sum  = get_sector_summary(tags_df)


def get_country_data_json():
    """
    Builds a JSON-serialisable dict of all country data.
    Served to D3 globe via /country-data endpoint.
    """
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
        ("NDC Countries",       str(kpis["total_countries"]),       C["emerald"]),
        ("Conditional Signals", str(kpis["conditional_countries"]), C["crimson"]),
        ("Avg ND-GAIN",         str(kpis["avg_ndgain"]),            C["amber"]),
        ("WB Projects",         str(kpis["total_projects"]),        C["cobalt"]),
        ("Established",         str(kpis["tier1_count"]),           C["tier1"]),
        ("Emerging",            str(kpis["tier2_count"]),           C["tier2"]),
        ("Frontier",            str(kpis["tier3_count"]),           C["tier3"]),
        ("Avg Renewables",      f"{kpis['avg_renewable']}%",        C["nature"]),
    ]
    return html.Div([
        html.Div(id="kpi-strip", children=[
            html.Div([
                html.Div(value, style={
                    "fontSize": "20px", "fontWeight": "700",
                    "color": colour, "fontFamily": "Inter, sans-serif",
                    "lineHeight": "1", "marginBottom": "4px"
                }),
                html.Div(label, style={
                    "fontSize": "11px", "fontWeight": "600",
                    "textTransform": "uppercase", "letterSpacing": "1px",
                    "color": C["text_muted"], "fontFamily": "Inter, sans-serif",
                })
            ], style={
                "textAlign": "center",
                "padding": "12px 20px",
                "borderRight": f"1px solid {C['border']}"
                               if i < len(items) - 1 else "none",
                "flexShrink": "0",
            })
            for i, (label, value, colour) in enumerate(items)
        ], style={
            "display": "flex",
            "overflowX": "auto",
            "justifyContent": "space-between",
        })
    ], style={
        "backgroundColor": C["surface"],
        "borderTop": f"1px solid {C['border']}",
        "borderBottom": f"1px solid {C['border']}",
        "position": "relative",
        "zIndex": "50",
    })


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
    country_data, country_tags = get_country_detail(
        iso_code, master_df, tags_df
    )
    if country_data is None:
        return empty_panel()

    full_name = get_country_name(iso_code)

    header = html.Div([
        html.Div([
            html.Div(full_name, style={
                "fontSize": "18px", "fontWeight": "700",
                "color": C["text"], "marginBottom": "8px",
                "fontFamily": "Inter, sans-serif", "lineHeight": "1.2",
            }),
            tier_badge(country_data.get("investment_tier", "N/A")),
        ]),
        html.Div("×", id="close-panel-btn", style={
            "fontSize": "22px", "color": C["text_muted"],
            "cursor": "pointer", "padding": "4px 8px",
            "lineHeight": "1", "userSelect": "none",
        })
    ], style={
        "display": "flex", "justifyContent": "space-between",
        "alignItems": "flex-start", "marginBottom": "20px"
    })

    summary_raw = country_data.get("indc_summary", "")
    summary     = clean_ndc_text(str(summary_raw), max_length=400)

    has_translation = any(
        phrase in str(summary_raw).lower()
        for phrase in ["submitted only in", "translated", "wri did"]
    )

    ndc_section = html.Div([
        html.Div("NDC Summary", style={
            "fontSize": "11px", "fontWeight": "600",
            "textTransform": "uppercase", "letterSpacing": "1.5px",
            "color": C["text_muted"], "marginBottom": "8px",
            "fontFamily": "Inter, sans-serif",
        }),
        html.P(summary, style={
            "fontSize": "13px", "color": C["text_secondary"],
            "lineHeight": "1.6", "margin": "0",
            "fontFamily": "Inter, sans-serif",
        })
    ], style={
        "backgroundColor": C["surface_high"],
        "border": f"1px solid {C['border']}",
        "borderLeft": f"2px solid {C['emerald']}",
        "borderRadius": "4px", "padding": "14px", "marginBottom": "16px"
    })

    flags = []
    if has_translation:
        flags.append(flag_pill("Translated NDC", C["amber"]))
    if float(country_data.get("data_completeness_pct", 100)) < 60:
        flags.append(flag_pill("Partial data", C["crimson"]))
    flags_row = html.Div(
        flags, style={"marginBottom": "16px"}
    ) if flags else html.Div()

    def fmt_gdp(v):
        if pd.isna(v) or v is None: return "N/A"
        if v >= 1e12: return f"${v/1e12:.1f}T"
        if v >= 1e9:  return f"${v/1e9:.1f}B"
        return f"${v/1e6:.0f}M"

    metrics = html.Div([
        html.Div("Key Metrics", style={
            "fontSize": "11px", "fontWeight": "600",
            "textTransform": "uppercase", "letterSpacing": "1.5px",
            "color": C["text_muted"], "marginBottom": "12px",
            "fontFamily": "Inter, sans-serif",
        }),
        html.Div([
            html.Div([
                data_row("GDP", fmt_gdp(country_data.get("gdp_usd"))),
                data_row("GDP per Capita",
                    f"${country_data.get('gdp_per_capita_usd', 0):,.0f}"
                    if pd.notna(country_data.get("gdp_per_capita_usd"))
                    else "N/A"),
                data_row("Population",
                    f"{country_data.get('population', 0)/1e6:.1f}M"
                    if pd.notna(country_data.get("population"))
                    else "N/A"),
            ], style={"flex": "1"}),
            html.Div([
                data_row("ND-GAIN Score",
                    f"{country_data.get('ndgain_score', 0):.1f}"
                    if pd.notna(country_data.get("ndgain_score"))
                    else "N/A",
                    colour=C["emerald"]),
                data_row("Vulnerability",
                    f"{country_data.get('vulnerability_score', 0):.2f}"
                    if pd.notna(country_data.get("vulnerability_score"))
                    else "N/A"),
                data_row("Renewables",
                    f"{country_data.get('renewable_electricity_pct', 0):.0f}%"
                    if pd.notna(
                        country_data.get("renewable_electricity_pct")
                    ) else "N/A",
                    colour=C["nature"]),
            ], style={"flex": "1"}),
        ], style={"display": "flex", "gap": "16px"})
    ], style={"marginBottom": "20px"})

    if not country_tags.empty:
        sector_rows = []
        for _, tag in country_tags.iterrows():
            sector_rows.append(
                html.Div([
                    html.Div(
                        [sector_pill(tag["sector"])],
                        style={"flex": "1"}
                    ),
                    confidence_badge(tag["confidence"]),
                ], style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "padding": "8px 0",
                    "borderBottom": f"1px solid {C['border']}",
                })
            )
        sectors_section = html.Div([
            html.Div("Identified Sectors", style={
                "fontSize": "11px", "fontWeight": "600",
                "textTransform": "uppercase", "letterSpacing": "1.5px",
                "color": C["text_muted"], "marginBottom": "12px",
                "fontFamily": "Inter, sans-serif",
            }),
            html.Div(sector_rows)
        ], style={"marginBottom": "20px"})
    else:
        sectors_section = html.Div()

    proj_count  = country_data.get("wb_project_count", 0)
    proj_active = country_data.get("wb_active_projects", 0)

    projects_section = html.Div([
        html.Div("World Bank Pipeline", style={
            "fontSize": "11px", "fontWeight": "600",
            "textTransform": "uppercase", "letterSpacing": "1.5px",
            "color": C["text_muted"], "marginBottom": "12px",
            "fontFamily": "Inter, sans-serif",
        }),
        html.Div([
            html.Div([
                html.Div(
                    str(int(proj_count))
                    if pd.notna(proj_count) else "0",
                    style={
                        "fontSize": "24px", "fontWeight": "700",
                        "color": C["cobalt"],
                        "fontFamily": "Inter, sans-serif"
                    }
                ),
                html.Div("Total Projects", style={
                    "fontSize": "11px", "color": C["text_muted"],
                    "fontFamily": "Inter, sans-serif",
                })
            ], style={"textAlign": "center", "flex": "1"}),
            html.Div([
                html.Div(
                    str(int(proj_active))
                    if pd.notna(proj_active) else "0",
                    style={
                        "fontSize": "24px", "fontWeight": "700",
                        "color": C["emerald"],
                        "fontFamily": "Inter, sans-serif"
                    }
                ),
                html.Div("Active", style={
                    "fontSize": "11px", "color": C["text_muted"],
                    "fontFamily": "Inter, sans-serif",
                })
            ], style={"textAlign": "center", "flex": "1"}),
        ], style={
            "display": "flex",
            "backgroundColor": C["surface_high"],
            "border": f"1px solid {C['border']}",
            "borderRadius": "4px", "padding": "16px",
        })
    ], style={"marginBottom": "20px"})

    news_section = html.Div([
        html.Div("Latest News and Subsidies", style={
            "fontSize": "11px", "fontWeight": "600",
            "textTransform": "uppercase", "letterSpacing": "1.5px",
            "color": C["text_muted"], "marginBottom": "12px",
            "fontFamily": "Inter, sans-serif",
        }),
        html.Div([
            html.Div("◌", style={
                "fontSize": "20px", "color": C["text_muted"],
                "marginBottom": "8px"
            }),
            html.Div(
                "News and subsidy search will be available "
                "once Google CSE is configured.",
                style={
                    "fontSize": "13px", "color": C["text_muted"],
                    "lineHeight": "1.5", "fontFamily": "Inter, sans-serif",
                }
            )
        ], style={
            "textAlign": "center", "padding": "24px",
            "backgroundColor": C["surface_high"],
            "border": f"1px solid {C['border']}",
            "borderRadius": "4px",
        })
    ])

    return html.Div([
        header, flags_row, ndc_section,
        metrics, sectors_section,
        projects_section, news_section,
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

        # Grid background
        html.Div(className="grid-background"),

        # Tooltip
        html.Div(id="globe-tooltip"),

        # Globe container — full viewport background
        html.Div(id="globe-container"),

        # KPI strip — fixed top below navbar
        kpi_strip(),

        # Hidden inputs for D3 to Dash communication
        html.Div([
            dcc.Input(
                id    = "d3-click-input",
                type  = "text",
                value = "",
                style = {"display": "none"}
            ),
            dcc.Input(
                id    = "colour-mode-value",
                type  = "text",
                value = "tier_score",
                style = {"display": "none"}
            ),
        ], id="d3-click-input-wrapper",
           style={"display": "none"}),

        # Colour mode selector — floating pill bar
        html.Div([
            html.Span("View by: ", style={
                "fontSize": "11px", "color": C["text_muted"],
                "marginRight": "10px", "fontFamily": "Inter, sans-serif",
            }),
            dcc.RadioItems(
                id         = "globe-colour-selector",
                options    = [
                    {"label": "Investment Tier",
                     "value": "tier_score"},
                    {"label": "ND-GAIN",
                     "value": "ndgain_score"},
                    {"label": "Vulnerability",
                     "value": "vulnerability_score"},
                    {"label": "Renewables %",
                     "value": "renewable_electricity_pct"},
                ],
                value      = "tier_score",
                inline     = True,
                inputStyle = {
                    "marginRight": "5px",
                    "accentColor": C["emerald"]
                },
                labelStyle = {
                    "fontSize": "12px",
                    "color": C["text_secondary"],
                    "marginRight": "16px",
                    "cursor": "pointer",
                    "fontFamily": "Inter, sans-serif",
                },
            )
        ], id="globe-controls"),

        # Scroll hint
        html.Div(
            "↓  Scroll to explore global analytics",
            id="scroll-hint"
        ),

        # Country panel overlay — slides in from right
        html.Div([
            html.Div(
                id       = "country-panel-content",
                children = empty_panel(),
                style    = {
                    "padding"   : "24px",
                    "overflowY" : "auto",
                    "height"    : "100%",
                }
            )
        ], id="country-panel-overlay"),

        # Analytics section — scrolls into view below globe
        html.Div([

            html.Div("Global Analysis", style={
                "fontSize": "11px", "fontWeight": "600",
                "textTransform": "uppercase", "letterSpacing": "1.5px",
                "color": C["text_muted"], "marginBottom": "8px",
                "fontFamily": "Inter, sans-serif",
            }),
            html.H2("Investment signals across all NDCs", style={
                "fontSize": "22px", "fontWeight": "600",
                "color": C["text"], "marginBottom": "40px",
                "fontFamily": "Inter, sans-serif",
            }),

            html.Div([
                html.Div("Sector Coverage", style={
                    "fontSize": "11px", "fontWeight": "600",
                    "textTransform": "uppercase", "letterSpacing": "1.5px",
                    "color": C["text_muted"], "marginBottom": "16px",
                    "fontFamily": "Inter, sans-serif",
                }),
                dcc.Graph(
                    id="sector-bar-chart",
                    figure=build_sector_chart(),
                    config={"displayModeBar": False}
                )
            ], style={
                "backgroundColor": C["surface"],
                "border": f"1px solid {C['border']}",
                "borderRadius": "6px",
                "padding": "24px",
                "marginBottom": "24px"
            }),

            html.Div([
                html.Div([
                    html.Div("Investment Tier Distribution", style={
                        "fontSize": "11px", "fontWeight": "600",
                        "textTransform": "uppercase",
                        "letterSpacing": "1.5px",
                        "color": C["text_muted"], "marginBottom": "16px",
                        "fontFamily": "Inter, sans-serif",
                    }),
                    dcc.Graph(
                        id="tier-donut-chart",
                        figure=build_tier_donut(),
                        config={"displayModeBar": False}
                    )
                ], style={
                    "backgroundColor": C["surface"],
                    "border": f"1px solid {C['border']}",
                    "borderRadius": "6px",
                    "padding": "24px", "flex": "1",
                }),
                html.Div([
                    html.Div("Commitment Type", style={
                        "fontSize": "11px", "fontWeight": "600",
                        "textTransform": "uppercase",
                        "letterSpacing": "1.5px",
                        "color": C["text_muted"], "marginBottom": "16px",
                        "fontFamily": "Inter, sans-serif",
                    }),
                    dcc.Graph(
                        id="commitment-bar-chart",
                        figure=build_commitment_chart(),
                        config={"displayModeBar": False}
                    )
                ], style={
                    "backgroundColor": C["surface"],
                    "border": f"1px solid {C['border']}",
                    "borderRadius": "6px",
                    "padding": "24px", "flex": "1",
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
    print(f"   D3 globe      : full viewport background")
    print(f"   Country panel : slide-in overlay")
    print(f"   Analytics     : scrolls below globe")
