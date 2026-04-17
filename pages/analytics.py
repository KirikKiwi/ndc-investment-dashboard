# ============================================================
# NDC Investment Dashboard
# pages/analytics.py — Global analytics section
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from components import C, SECTOR_COLOURS, TIER_COLOURS
from data import (load_master, load_tags, REGIONS, GROUPS,
                  filter_master, get_country_name)

master_df = load_master()
tags_df   = load_tags()

LABEL_STYLE = {
    "fontSize"      : "11px",
    "fontWeight"    : "600",
    "textTransform" : "uppercase",
    "letterSpacing" : "1.5px",
    "color"         : C["text_muted"],
    "marginBottom"  : "8px",
    "fontFamily"    : "Inter, sans-serif",
}

DESC_STYLE = {
    "fontSize"     : "12px",
    "color"        : C["text_muted"],
    "fontFamily"   : "Inter, sans-serif",
    "marginBottom" : "16px",
    "lineHeight"   : "1.6",
}

CARD_STYLE = {
    "backgroundColor" : C["surface"],
    "border"          : f"1px solid {C['border']}",
    "borderRadius"    : "6px",
    "padding"         : "24px",
}

SECTION_STYLE = {"marginBottom": "48px"}


def section_header(text, colour, description):
    return html.Div([
        html.Div(text, style={
            **LABEL_STYLE,
            "borderLeft"  : f"3px solid {colour}",
            "paddingLeft" : "10px",
            "marginBottom": "6px",
        }),
        html.Div(description, style=DESC_STYLE),
    ])


def stat_card(value, label, colour):
    return html.Div([
        html.Div(str(value), style={
            "fontSize"     : "28px",
            "fontWeight"   : "700",
            "color"        : colour,
            "fontFamily"   : "Inter, sans-serif",
            "lineHeight"   : "1",
            "marginBottom" : "4px",
        }),
        html.Div(label, style={
            "fontSize"  : "11px",
            "color"     : C["text_muted"],
            "fontFamily": "Inter, sans-serif",
            "lineHeight": "1.4",
        })
    ], style={
        "textAlign"       : "center",
        "flex"            : "1",
        "padding"         : "16px",
        "backgroundColor" : C["surface_high"],
        "border"          : f"1px solid {C['border']}",
        "borderRadius"    : "4px",
    })


def wrapped_graph(graph_id, figure):
    if figure is None:
        return html.Div()
    return dcc.Loading(
        type     = "circle",
        color    = C["emerald"],
        children = dcc.Graph(
            id     = graph_id,
            figure = figure,
            config = {"displayModeBar": False},
        )
    )


# ============================================================
# FILTER BAR
# ============================================================

def filter_bar():
    region_options  = [{"label": "All Regions",   "value": "ALL"}] + [
        {"label": r, "value": r} for r in sorted(REGIONS.keys())
    ]
    group_options   = [{"label": "All Groups",    "value": "ALL"}] + [
        {"label": g, "value": g} for g in GROUPS.keys()
    ]
    country_options = [{"label": "All Countries", "value": "ALL"}] + [
        {"label": get_country_name(iso), "value": iso}
        for iso in sorted(master_df["iso_code"].dropna())
    ]

    dd_style = {
        "backgroundColor": C["surface_high"],
        "color"          : C["text"],
        "fontSize"       : "12px",
        "border"         : f"1px solid {C['border']}",
        "fontFamily"     : "Inter, sans-serif",
    }

    lbl = {
        "fontSize"      : "10px",
        "color"         : C["text_muted"],
        "fontFamily"    : "Inter, sans-serif",
        "marginBottom"  : "4px",
        "fontWeight"    : "600",
        "textTransform" : "uppercase",
        "letterSpacing" : "1px",
    }

    return html.Div([
        html.Div([
            html.Div("Filter Analytics", style={
                **LABEL_STYLE, "marginBottom": "2px"
            }),
            html.Div(
                "Default: global view across all countries. "
                "Selecting a single country filters all charts.",
                style={**DESC_STYLE, "marginBottom": "16px"}
            ),
            html.Div([
                html.Div([
                    html.Div("Region", style=lbl),
                    dcc.Dropdown(id="filter-region",
                                 options=region_options,
                                 value="ALL", clearable=False,
                                 style=dd_style)
                ], style={"flex": "2"}),
                html.Div([
                    html.Div("Group", style=lbl),
                    dcc.Dropdown(id="filter-group",
                                 options=group_options,
                                 value="ALL", clearable=False,
                                 style=dd_style)
                ], style={"flex": "2"}),
                html.Div([
                    html.Div("Country", style=lbl),
                    dcc.Dropdown(id="filter-country",
                                 options=country_options,
                                 value="ALL", clearable=False,
                                 searchable=True,
                                 placeholder="Search country...",
                                 style=dd_style)
                ], style={"flex": "3"}),
                html.Div([
                    html.Div("", style={"height": "20px"}),
                    html.Button("Reset", id="filter-reset-btn",
                                style={
                                    "backgroundColor": "transparent",
                                    "color"          : C["text_muted"],
                                    "border"         : f"1px solid {C['border']}",
                                    "borderRadius"   : "4px",
                                    "padding"        : "8px 16px",
                                    "fontSize"       : "12px",
                                    "fontFamily"     : "Inter, sans-serif",
                                    "cursor"         : "pointer",
                                    "width"          : "100%",
                                })
                ], style={"flex": "1"}),
                html.Div([
                    html.Div("", style={"height": "20px"}),
                    html.Button("Export CSV", id="filter-export-btn",
                                style={
                                    "backgroundColor": C["emerald"],
                                    "color"          : C["bg"],
                                    "border"         : "none",
                                    "borderRadius"   : "4px",
                                    "padding"        : "8px 16px",
                                    "fontSize"       : "12px",
                                    "fontFamily"     : "Inter, sans-serif",
                                    "cursor"         : "pointer",
                                    "width"          : "100%",
                                    "fontWeight"     : "600",
                                }),
                    dcc.Download(id="download-csv"),
                ], style={"flex": "1"}),
            ], style={
                "display"    : "flex",
                "gap"        : "16px",
                "alignItems" : "flex-end",
            }),
            html.Div(id="filter-summary", style={
                "marginTop" : "12px",
                "fontSize"  : "11px",
                "color"     : C["emerald"],
                "fontFamily": "Inter, sans-serif",
            }),
        ], style={**CARD_STYLE, "marginBottom": "32px"})
    ])


# ============================================================
# SECTION 1 — PARIS ALIGNMENT
# ============================================================

def build_paris_alignment(df, tags):
    filtered_isos = set(df["iso_code"].dropna())
    tags_f        = tags[tags["iso_code"].isin(filtered_isos)]

    lens_counts = (
        tags_f[tags_f["climate_lens"].notna()]
        .groupby("climate_lens")
        .agg(count=("iso_code","nunique"))
        .reset_index()
    )

    lens_colours = {
        "Mitigation": C["emerald"],
        "Adaptation": C["cobalt"],
        "Dual"      : C["amber"],
    }

    fig_lens = None
    if len(lens_counts) >= 2:
        fig_lens = go.Figure(go.Pie(
            labels    = lens_counts["climate_lens"],
            values    = lens_counts["count"],
            hole      = 0.6,
            marker    = dict(
                colors = [lens_colours.get(l, C["text_muted"])
                          for l in lens_counts["climate_lens"]],
                line   = dict(color=C["bg"], width=2)
            ),
            textfont  = dict(color=C["text"], size=11,
                             family="Inter"),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Countries: %{value}<br>"
                "%{percent}<extra></extra>"
            )
        ))
        fig_lens.update_layout(
            paper_bgcolor = C["bg"],
            font          = dict(color=C["text"], family="Inter"),
            showlegend    = True,
            legend        = dict(
                font    = dict(color=C["text_muted"], size=11),
                bgcolor = "rgba(0,0,0,0)",
                x=1.0, y=0.5,
            ),
            margin      = dict(l=0, r=80, t=10, b=10),
            height      = 260,
            annotations = [dict(
                text      = "Climate<br>Lens",
                x=0.5, y=0.5,
                font      = dict(color=C["text"], size=12,
                                 family="Inter"),
                showarrow = False
            )]
        )

    cond_count = int(df["conditional_pct_uplift"].notna().sum())
    avg_uplift = df["conditional_pct_uplift"].mean()
    avg_str    = (f"{avg_uplift:.1f}%"
                  if pd.notna(avg_uplift) else "N/A")

    stats_row = html.Div([
        stat_card(cond_count,  "Countries with quantified conditional signal", C["crimson"]),
        stat_card(avg_str,     "Average conditional uplift where signalled",   C["amber"]),
        stat_card(len(df),     "Countries in current filter",                  C["emerald"]),
    ], style={
        "display"      : "flex",
        "gap"          : "16px",
        "marginBottom" : "24px",
    })

    cop_card = html.Div([
        html.Div("COP Climate Finance Commitment",
                 style={**LABEL_STYLE, "marginBottom": "8px"}),
        html.Div([
            html.Div([
                html.Div("$100bn", style={
                    "fontSize": "22px", "fontWeight": "700",
                    "color": C["emerald"], "fontFamily": "Inter, sans-serif",
                }),
                html.Div("Annual target (Paris Agreement)", style={
                    "fontSize": "11px", "color": C["text_muted"],
                    "fontFamily": "Inter, sans-serif"
                })
            ], style={"textAlign": "center", "flex": "1"}),
            html.Div([
                html.Div("~$89bn", style={
                    "fontSize": "22px", "fontWeight": "700",
                    "color": C["amber"], "fontFamily": "Inter, sans-serif",
                }),
                html.Div("Latest OECD reported (2021)", style={
                    "fontSize": "11px", "color": C["text_muted"],
                    "fontFamily": "Inter, sans-serif"
                })
            ], style={"textAlign": "center", "flex": "1"}),
            html.Div([
                html.Div("~$11bn", style={
                    "fontSize": "22px", "fontWeight": "700",
                    "color": C["crimson"], "fontFamily": "Inter, sans-serif",
                }),
                html.Div("Annual financing gap", style={
                    "fontSize": "11px", "color": C["text_muted"],
                    "fontFamily": "Inter, sans-serif"
                })
            ], style={"textAlign": "center", "flex": "1"}),
        ], style={"display": "flex", "gap": "16px"}),
        html.Div(
            "Live COP finance tracking will be added in the "
            "next data update via OECD Climate Finance API.",
            style={
                "fontSize" : "11px", "color": C["text_muted"],
                "fontFamily": "Inter, sans-serif",
                "marginTop": "12px", "fontStyle": "italic",
            }
        )
    ], style={
        **CARD_STYLE,
        "borderLeft": f"3px solid {C['amber']}",
    })

    lens_row = html.Div()
    if fig_lens:
        lens_row = html.Div([
            html.Div([
                html.Div("Mitigation vs Adaptation Split",
                         style={**LABEL_STYLE, "marginBottom": "8px"}),
                html.Div(
                    "Distribution of NDC sector tags across "
                    "mitigation, adaptation and dual-purpose "
                    "commitments.",
                    style=DESC_STYLE
                ),
                wrapped_graph("paris-lens-chart", fig_lens)
            ], style={**CARD_STYLE, "flex": "1"}),
            html.Div([cop_card], style={"flex": "1"}),
        ], style={"display": "flex", "gap": "24px"})

    return html.Div([stats_row, lens_row])


# ============================================================
# SECTION 2 — ENERGY AND CLIMATE READINESS
# ============================================================

def build_energy_readiness(df, single_country=False):
    renewable = (df[df["renewable_electricity_pct"].notna()]
                 .sort_values("renewable_electricity_pct",
                              ascending=False))

    charts      = []
    fig_scatter = None

    if single_country:
        if len(renewable) == 0:
            return html.Div()
        row  = renewable.iloc[0]
        name = get_country_name(row["iso_code"])
        val  = row["renewable_electricity_pct"]
        avg  = master_df["renewable_electricity_pct"].mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[val], y=[name], orientation="h",
            marker_color=C["emerald"],
            text=[f"{val:.0f}%"], textposition="outside",
            textfont=dict(color=C["text_muted"], size=12,
                          family="Inter"),
            name=name,
        ))
        fig.add_trace(go.Bar(
            x=[avg], y=["Global Average"], orientation="h",
            marker_color=C["cobalt"],
            text=[f"{avg:.0f}%"], textposition="outside",
            textfont=dict(color=C["text_muted"], size=12,
                          family="Inter"),
            name="Global Average",
        ))
        fig.update_layout(
            paper_bgcolor=C["bg"], plot_bgcolor=C["surface"],
            font=dict(color=C["text"], family="Inter"),
            xaxis=dict(color=C["text_muted"], showgrid=True,
                       gridcolor=C["border"],
                       title="Renewable Electricity %",
                       range=[0, 120]),
            yaxis=dict(color=C["text_muted"], showgrid=False),
            margin=dict(l=10, r=60, t=10, b=10),
            height=180, bargap=0.4, showlegend=False,
        )
        return html.Div([
            html.Div([
                html.Div("Renewable Electricity Share",
                         style={**LABEL_STYLE, "marginBottom": "8px"}),
                html.Div(
                    f"Renewable share for {name} vs global average.",
                    style=DESC_STYLE
                ),
                wrapped_graph("renewable-country-chart", fig)
            ], style=CARD_STYLE)
        ])

    # Top 10 and Bottom 10 as ranked lists
    top10    = renewable.head(10)
    bottom10 = renewable.tail(10).sort_values(
        "renewable_electricity_pct", ascending=True
    )

    if len(top10) > 0 or len(bottom10) > 0:
        row_items = []

        if len(top10) > 0:
            top_rows = []
            for i, (_, row) in enumerate(top10.iterrows()):
                name = get_country_name(row["iso_code"])
                top_rows.append(html.Div([
                    html.Span(f"{i+1}", style={
                        "width"     : "28px",
                        "fontSize"  : "12px",
                        "color"     : C["emerald"],
                        "fontFamily": "Inter, sans-serif",
                        "fontWeight": "700",
                        "flexShrink": "0",
                    }),
                    html.Span(name, style={
                        "flex"      : "1",
                        "fontSize"  : "13px",
                        "color"     : C["text"],
                        "fontFamily": "Inter, sans-serif",
                    }),
                ], style={
                    "display"      : "flex",
                    "alignItems"   : "center",
                    "gap"          : "8px",
                    "padding"      : "8px 0",
                    "borderBottom" : f"1px solid {C['border']}",
                }))
            row_items.append(html.Div([
                html.Div("Renewable Leaders",
                         style={**LABEL_STYLE, "marginBottom": "12px"}),
                html.Div(top_rows)
            ], style={**CARD_STYLE, "flex": "1"}))

        if len(bottom10) > 0:
            bot_rows = []
            for i, (_, row) in enumerate(bottom10.iterrows()):
                name = get_country_name(row["iso_code"])
                bot_rows.append(html.Div([
                    html.Span(f"{i+1}", style={
                        "width"     : "28px",
                        "fontSize"  : "12px",
                        "color"     : C["crimson"],
                        "fontFamily": "Inter, sans-serif",
                        "fontWeight": "700",
                        "flexShrink": "0",
                    }),
                    html.Span(name, style={
                        "flex"      : "1",
                        "fontSize"  : "13px",
                        "color"     : C["text"],
                        "fontFamily": "Inter, sans-serif",
                    }),
                ], style={
                    "display"      : "flex",
                    "alignItems"   : "center",
                    "gap"          : "8px",
                    "padding"      : "8px 0",
                    "borderBottom" : f"1px solid {C['border']}",
                }))
            row_items.append(html.Div([
                html.Div("Lowest Renewable Share",
                         style={**LABEL_STYLE, "marginBottom": "12px"}),
                html.Div(bot_rows)
            ], style={**CARD_STYLE, "flex": "1"}))

        charts.append(html.Div(row_items, style={
            "display": "flex", "gap": "24px",
            "marginBottom": "24px"
        }))

    # ND-GAIN scatter
    scatter_df = df[
        df["readiness_score"].notna() &
        df["vulnerability_score"].notna()
    ].copy()

    if len(scatter_df) >= 3:
        scatter_df["name"] = scatter_df["iso_code"].apply(
            get_country_name
        )
        tier_colour_map = {
            "Tier 1 — Established markets": C["tier1"],
            "Tier 2 — Emerging markets"   : C["tier2"],
            "Tier 3 — Frontier markets"   : C["tier3"],
            "Insufficient data"            : C["tier_none"],
        }
        fig_scatter = go.Figure()
        for tier, colour in tier_colour_map.items():
            subset = scatter_df[
                scatter_df["investment_tier"] == tier
            ]
            if len(subset) == 0:
                continue
            fig_scatter.add_trace(go.Scatter(
                x    = subset["readiness_score"],
                y    = subset["vulnerability_score"],
                mode = "markers",
                name = (tier.split(" — ")[-1]
                        if " — " in tier else tier),
                marker = dict(
                    color   = colour,
                    size    = 7,
                    opacity = 0.8,
                    line    = dict(color=C["bg"], width=0.5)
                ),
                text          = subset["name"],
                hovertemplate = (
                    "<b>%{text}</b><br>"
                    "Readiness: %{x:.2f}<br>"
                    "Vulnerability: %{y:.2f}"
                    "<extra></extra>"
                ),
            ))
        fig_scatter.update_layout(
            paper_bgcolor = C["bg"],
            plot_bgcolor  = C["surface"],
            font          = dict(color=C["text"], family="Inter"),
            xaxis         = dict(
                title="Readiness Score", color=C["text_muted"],
                gridcolor=C["border"], showgrid=True,
            ),
            yaxis         = dict(
                title="Vulnerability Score", color=C["text_muted"],
                gridcolor=C["border"], showgrid=True,
            ),
            legend        = dict(
                font    = dict(color=C["text_muted"], size=10),
                bgcolor = "rgba(0,0,0,0)",
            ),
            margin = dict(l=10, r=10, t=10, b=10),
            height = 320,
        )

    if fig_scatter:
        charts.append(html.Div([
            html.Div(
                "ND-GAIN Readiness vs Climate Vulnerability",
                style={**LABEL_STYLE, "marginBottom": "8px"}
            ),
            html.Div(
                "Countries bottom-right (high vulnerability, low "
                "readiness) represent the highest priority markets "
                "for adaptation finance. Colour indicates investment "
                "tier. Hover for country name.",
                style=DESC_STYLE
            ),
            wrapped_graph("ndgain-scatter", fig_scatter)
        ], style=CARD_STYLE))

    return html.Div(charts)


# ============================================================
# SECTION 3 — FINANCE FLOWS
# ============================================================

def build_finance_flows(df, tags, single_country=False):
    from data import ISO_TO_REGION

    filtered_isos = set(df["iso_code"].dropna())
    tags_f        = tags[tags["iso_code"].isin(filtered_isos)]

    if single_country and len(df) == 1:
        inst_counts = (
            tags_f[tags_f["financing_instrument"].notna()]
            .groupby("financing_instrument")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=True)
        )
        if len(inst_counts) == 0:
            return html.Div()

        inst_colours = {
            "Grant"    : C["emerald"],
            "Debt"     : C["cobalt"],
            "Equity"   : C["amber"],
            "Guarantee": C["industry"],
        }
        fig = go.Figure(go.Bar(
            x=inst_counts["count"],
            y=inst_counts["financing_instrument"],
            orientation="h",
            marker_color=[inst_colours.get(i, C["text_muted"])
                          for i in inst_counts["financing_instrument"]],
            text=inst_counts["count"],
            textposition="outside",
            textfont=dict(color=C["text_muted"], size=11,
                          family="Inter"),
            hovertemplate=(
                "<b>%{y}</b><br>Signals: %{x}<extra></extra>"
            ),
        ))
        fig.update_layout(
            paper_bgcolor=C["bg"], plot_bgcolor=C["surface"],
            font=dict(color=C["text"], family="Inter"),
            xaxis=dict(color=C["text_muted"], showgrid=True,
                       gridcolor=C["border"], title="Signal Count"),
            yaxis=dict(color=C["text_muted"], showgrid=False),
            margin=dict(l=10, r=50, t=10, b=10),
            height=220, bargap=0.3,
        )
        return html.Div([
            html.Div("Financing Instrument Mix",
                     style={**LABEL_STYLE, "marginBottom": "8px"}),
            html.Div(
                "Financing instruments signalled in the NDC.",
                style=DESC_STYLE
            ),
            wrapped_graph("instrument-country-chart", fig)
        ], style=CARD_STYLE)

    tags_r         = tags_f.copy()
    tags_r["region"] = tags_r["iso_code"].map(
        ISO_TO_REGION
    ).fillna("Other")

    instruments  = ["Grant", "Debt", "Equity", "Guarantee"]
    inst_colours = {
        "Grant"    : C["emerald"],
        "Debt"     : C["cobalt"],
        "Equity"   : C["amber"],
        "Guarantee": C["industry"],
    }

    inst_region = (
        tags_r[tags_r["financing_instrument"].notna()]
        .groupby(["region","financing_instrument"])
        .size()
        .reset_index(name="count")
    )
    regions = sorted(inst_region["region"].unique())

    fig_inst = None
    if len(regions) >= 2:
        fig_inst = go.Figure()
        for inst in instruments:
            subset = inst_region[
                inst_region["financing_instrument"] == inst
            ]
            counts = [
                int(subset[subset["region"] == r]["count"].sum())
                if r in subset["region"].values else 0
                for r in regions
            ]
            if sum(counts) == 0:
                continue
            fig_inst.add_trace(go.Bar(
                name=inst, x=regions, y=counts,
                marker_color=inst_colours.get(inst, C["text_muted"]),
                hovertemplate=(
                    f"<b>%{{x}}</b><br>{inst}: %{{y}}"
                    "<extra></extra>"
                ),
            ))
        fig_inst.update_layout(
            barmode       = "stack",
            paper_bgcolor = C["bg"],
            plot_bgcolor  = C["surface"],
            font          = dict(color=C["text"], family="Inter"),
            legend        = dict(
                font    = dict(color=C["text_muted"], size=11),
                bgcolor = "rgba(0,0,0,0)",
                orientation="h", x=0, y=1.1,
            ),
            xaxis  = dict(color=C["text_muted"], showgrid=False,
                          tickangle=-30),
            yaxis  = dict(color=C["text_muted"],
                          gridcolor=C["border"],
                          title="Signal Count"),
            margin = dict(l=10, r=10, t=40, b=80),
            height = 320,
        )

    tier_region = df.copy()
    tier_region["region"] = tier_region["iso_code"].map(
        ISO_TO_REGION
    ).fillna("Other")
    tier_region_counts = (
        tier_region.groupby(["region","investment_tier"])
        .size()
        .reset_index(name="count")
    )
    r_list = sorted(tier_region["region"].unique())

    fig_tier = None
    if len(r_list) >= 2:
        fig_tier = go.Figure()
        for tier, colour in [
            ("Tier 1 — Established markets", C["tier1"]),
            ("Tier 2 — Emerging markets",    C["tier2"]),
            ("Tier 3 — Frontier markets",    C["tier3"]),
        ]:
            subset = tier_region_counts[
                tier_region_counts["investment_tier"] == tier
            ]
            counts = [
                int(subset[subset["region"] == r]["count"].sum())
                if r in subset["region"].values else 0
                for r in r_list
            ]
            if sum(counts) == 0:
                continue
            short = tier.split(" — ")[-1]
            fig_tier.add_trace(go.Bar(
                name=short, x=r_list, y=counts,
                marker_color=colour,
                hovertemplate=(
                    f"<b>%{{x}}</b><br>{short}: %{{y}}"
                    "<extra></extra>"
                ),
            ))
        fig_tier.update_layout(
            barmode       = "group",
            paper_bgcolor = C["bg"],
            plot_bgcolor  = C["surface"],
            font          = dict(color=C["text"], family="Inter"),
            legend        = dict(
                font    = dict(color=C["text_muted"], size=11),
                bgcolor = "rgba(0,0,0,0)",
                orientation="h", x=0, y=1.1,
            ),
            xaxis  = dict(color=C["text_muted"], showgrid=False,
                          tickangle=-30),
            yaxis  = dict(color=C["text_muted"],
                          gridcolor=C["border"],
                          title="Countries"),
            margin = dict(l=10, r=10, t=40, b=80),
            height = 300,
        )

    top_signals = (
        df[df["conditional_pct_uplift"].notna()]
        .sort_values("conditional_pct_uplift", ascending=False)
        .head(10)
    )

    signal_rows = []
    for i, (_, row) in enumerate(top_signals.iterrows()):
        name   = get_country_name(row["iso_code"])
        uplift = float(row["conditional_pct_uplift"])
        tier   = str(row.get("investment_tier",""))
        short  = (tier.split(" — ")[-1]
                  if " — " in tier else "N/A")
        bar_w  = min(int(uplift), 100)
        signal_rows.append(html.Div([
            html.Div(f"{i+1}", style={
                "width": "20px", "fontSize": "10px",
                "color": C["text_muted"],
                "fontFamily": "Inter, sans-serif",
                "flexShrink": "0",
            }),
            html.Div(name, style={
                "flex": "1", "fontSize": "12px",
                "color": C["text"],
                "fontFamily": "Inter, sans-serif",
            }),
            html.Div([
                html.Div(style={
                    "width"          : f"{bar_w}%",
                    "backgroundColor": C["crimson"],
                    "height"         : "6px",
                    "borderRadius"   : "2px",
                    "minWidth"       : "4px",
                })
            ], style={
                "flex": "2", "display": "flex",
                "alignItems": "center", "paddingRight": "8px",
            }),
            html.Div(f"{uplift:.1f}%", style={
                "width": "44px", "fontSize": "12px",
                "color": C["crimson"], "fontWeight": "600",
                "fontFamily": "Inter, sans-serif",
                "textAlign": "right",
            }),
            html.Div(short, style={
                "width": "80px", "fontSize": "10px",
                "color": C["text_muted"],
                "fontFamily": "Inter, sans-serif",
                "textAlign": "right",
            }),
        ], style={
            "display": "flex", "alignItems": "center",
            "gap": "8px", "padding": "6px 0",
            "borderBottom": f"1px solid {C['border']}",
        }))

    charts = []

    if fig_inst:
        charts.append(html.Div([
            html.Div("Financing Instrument Mix by Region",
                     style={**LABEL_STYLE, "marginBottom": "8px"}),
            html.Div(
                "Instrument signals from NDC text, stacked by region.",
                style=DESC_STYLE
            ),
            wrapped_graph("instrument-region-chart", fig_inst)
        ], style={**CARD_STYLE, "marginBottom": "24px"}))

    row2 = []
    if fig_tier:
        row2.append(html.Div([
            html.Div("Investment Tier by Region",
                     style={**LABEL_STYLE, "marginBottom": "8px"}),
            html.Div(
                "Tier distribution across regions. Frontier markets "
                "indicate highest concessional finance need.",
                style=DESC_STYLE
            ),
            wrapped_graph("tier-region-chart", fig_tier)
        ], style={**CARD_STYLE, "flex": "1"}))

    if signal_rows:
        row2.append(html.Div([
            html.Div("Top Conditional Finance Signals",
                     style={**LABEL_STYLE, "marginBottom": "8px"}),
            html.Div(
                "Countries ranked by conditional GHG uplift "
                "percentage.",
                style=DESC_STYLE
            ),
            html.Div(signal_rows)
        ], style={**CARD_STYLE, "flex": "1"}))

    if row2:
        charts.append(html.Div(row2, style={
            "display": "flex", "gap": "24px"
        }))

    return html.Div(charts)


# ============================================================
# SECTION 4 — SECTOR INTELLIGENCE
# ============================================================

def build_sector_intelligence(df, tags):
    filtered_isos = set(df["iso_code"].dropna())
    tags_f        = tags[tags["iso_code"].isin(filtered_isos)]

    if len(tags_f) == 0:
        return html.Div()

    sector_counts = (
        tags_f.groupby("sector")
        .agg(country_count=("iso_code","nunique"))
        .reset_index()
        .sort_values("country_count", ascending=True)
    )

    colours = [SECTOR_COLOURS.get(s, C["text_muted"])
               for s in sector_counts["sector"]]

    fig_cov = None
    if len(sector_counts) >= 2:
        fig_cov = go.Figure(go.Bar(
            x=sector_counts["country_count"],
            y=sector_counts["sector"],
            orientation="h",
            marker_color=colours,
            text=sector_counts["country_count"],
            textposition="outside",
            textfont=dict(color=C["text_muted"], size=11,
                          family="Inter"),
            hovertemplate=(
                "<b>%{y}</b><br>Countries: %{x}<extra></extra>"
            ),
        ))
        fig_cov.update_layout(
            paper_bgcolor=C["bg"], plot_bgcolor=C["surface"],
            font=dict(color=C["text"], family="Inter"),
            xaxis=dict(showgrid=True, gridcolor=C["border"],
                       color=C["text_muted"], title="Countries"),
            yaxis=dict(color=C["text_muted"], showgrid=False),
            margin=dict(l=10, r=50, t=10, b=10),
            height=280, bargap=0.3,
        )

    commit_sector = (
        tags_f[tags_f["commitment_type"].notna()]
        .groupby(["sector","commitment_type"])
        .size()
        .reset_index(name="count")
    )

    fig_commit = None
    if len(commit_sector) >= 2:
        fig_commit = go.Figure()
        for ctype, colour in [
            ("Conditional",   C["crimson"]),
            ("Unconditional", C["emerald"]),
        ]:
            subset = commit_sector[
                commit_sector["commitment_type"] == ctype
            ]
            if len(subset) == 0:
                continue
            fig_commit.add_trace(go.Bar(
                name=ctype, x=subset["sector"],
                y=subset["count"], marker_color=colour,
                hovertemplate=(
                    f"<b>%{{x}}</b><br>{ctype}: %{{y}}"
                    "<extra></extra>"
                ),
            ))
        fig_commit.update_layout(
            barmode       = "group",
            paper_bgcolor = C["bg"],
            plot_bgcolor  = C["surface"],
            font          = dict(color=C["text"], family="Inter"),
            legend        = dict(
                font    = dict(color=C["text_muted"], size=11),
                bgcolor = "rgba(0,0,0,0)",
            ),
            xaxis  = dict(color=C["text_muted"], showgrid=False,
                          tickangle=-20),
            yaxis  = dict(color=C["text_muted"],
                          gridcolor=C["border"], title="Count"),
            margin = dict(l=10, r=10, t=10, b=60),
            height = 280, bargap=0.3,
        )

    horizon_sector = (
        tags_f[tags_f["implementation_horizon"].notna()]
        .groupby(["sector","implementation_horizon"])
        .size()
        .reset_index(name="count")
    )

    fig_horizon = None
    if len(horizon_sector) >= 2:
        fig_horizon = go.Figure()
        for horizon, colour in [
            ("Near-term",   C["emerald"]),
            ("Medium-term", C["amber"]),
            ("Long-term",   C["cobalt"]),
        ]:
            subset = horizon_sector[
                horizon_sector["implementation_horizon"] == horizon
            ]
            if len(subset) == 0:
                continue
            fig_horizon.add_trace(go.Bar(
                name=horizon, x=subset["sector"],
                y=subset["count"], marker_color=colour,
                hovertemplate=(
                    f"<b>%{{x}}</b><br>{horizon}: %{{y}}"
                    "<extra></extra>"
                ),
            ))
        fig_horizon.update_layout(
            barmode       = "stack",
            paper_bgcolor = C["bg"],
            plot_bgcolor  = C["surface"],
            font          = dict(color=C["text"], family="Inter"),
            legend        = dict(
                font    = dict(color=C["text_muted"], size=11),
                bgcolor = "rgba(0,0,0,0)",
                orientation="h", x=0, y=1.1,
            ),
            xaxis  = dict(color=C["text_muted"], showgrid=False,
                          tickangle=-20),
            yaxis  = dict(color=C["text_muted"],
                          gridcolor=C["border"], title="Count"),
            margin = dict(l=10, r=10, t=40, b=60),
            height = 280,
        )

    charts = []

    if fig_cov:
        charts.append(html.Div([
            html.Div("Sector Coverage Across NDCs",
                     style={**LABEL_STYLE, "marginBottom": "8px"}),
            html.Div(
                "Number of countries where each sector is identified "
                "in NDC text with at least low confidence.",
                style=DESC_STYLE
            ),
            wrapped_graph("sector-cov-chart", fig_cov)
        ], style={**CARD_STYLE, "marginBottom": "24px"}))

    row2 = []
    if fig_commit:
        row2.append(html.Div([
            html.Div("Commitment Type by Sector",
                     style={**LABEL_STYLE, "marginBottom": "8px"}),
            html.Div(
                "Conditional vs unconditional commitments by sector. "
                "High conditional counts indicate sectors most "
                "dependent on external finance.",
                style=DESC_STYLE
            ),
            wrapped_graph("sector-commit-chart", fig_commit)
        ], style={**CARD_STYLE, "flex": "1"}))

    if fig_horizon:
        row2.append(html.Div([
            html.Div("Implementation Horizon by Sector",
                     style={**LABEL_STYLE, "marginBottom": "8px"}),
            html.Div(
                "Near-term targets (by 2030) vs medium and long-term "
                "commitments. Shows where investment urgency is "
                "highest.",
                style=DESC_STYLE
            ),
            wrapped_graph("sector-horizon-chart", fig_horizon)
        ], style={**CARD_STYLE, "flex": "1"}))

    if row2:
        charts.append(html.Div(row2, style={
            "display": "flex", "gap": "24px"
        }))

    return html.Div(charts)


# ============================================================
# FULL LAYOUT
# ============================================================

def layout(df=None, tags=None):
    if df is None:
        df = master_df
    if tags is None:
        tags = tags_df

    n              = len(df)
    single_country = (n == 1)

    return html.Div([

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
            html.H2(
                f"Investment signals across {n} "
                f"{'country' if n == 1 else 'countries'}",
                id    = "analytics-header",
                style = {
                    "fontSize"     : "22px",
                    "fontWeight"   : "600",
                    "color"        : C["text"],
                    "marginBottom" : "32px",
                    "fontFamily"   : "Inter, sans-serif",
                }
            ),
        ]),

        filter_bar(),

        html.Div([
            section_header(
                "Paris Alignment",
                C["crimson"],
                "How NDC commitments align across mitigation and "
                "adaptation, and the aggregate conditional finance "
                "signal relative to COP commitments."
            ),
            dcc.Loading(type="circle", color=C["emerald"],
                children=html.Div(
                    id="paris-section",
                    children=build_paris_alignment(df, tags)
                )
            ),
        ], style=SECTION_STYLE),

        html.Div([
            section_header(
                "Energy and Climate Readiness",
                C["amber"],
                "Renewable electricity leaders and laggards, and "
                "the relationship between climate vulnerability and "
                "institutional readiness."
            ),
            dcc.Loading(type="circle", color=C["emerald"],
                children=html.Div(
                    id="energy-section",
                    children=build_energy_readiness(
                        df, single_country=single_country
                    )
                )
            ),
        ], style=SECTION_STYLE),

        html.Div([
            section_header(
                "Finance Flows",
                C["cobalt"],
                "Financing instrument mix by region, investment tier "
                "concentration and the strongest conditional finance "
                "signals."
            ),
            dcc.Loading(type="circle", color=C["emerald"],
                children=html.Div(
                    id="finance-section",
                    children=build_finance_flows(
                        df, tags,
                        single_country=single_country
                    )
                )
            ),
        ], style=SECTION_STYLE),

        html.Div([
            section_header(
                "Sector Intelligence",
                C["industry"],
                "Sector coverage, commitment types and implementation "
                "horizons extracted from NDC text."
            ),
            dcc.Loading(type="circle", color=C["emerald"],
                children=html.Div(
                    id="sector-section",
                    children=build_sector_intelligence(df, tags)
                )
            ),
        ], style=SECTION_STYLE),

    ], style={
        "padding"         : "80px",
        "backgroundColor" : C["bg"],
        "borderTop"       : f"1px solid {C['border']}",
    })


if __name__ == "__main__":
    page = layout()
    print("✅ analytics.py verified")
    print("   Sections: Paris Alignment, Energy Readiness,")
    print("             Finance Flows, Sector Intelligence")
    print(f"  Countries: {len(master_df)}")
