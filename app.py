
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import os
import json

# ============================================================
# DATABASE
# ============================================================

DB_PATH = os.path.join(
    os.path.expanduser("~"),
    "Documents", "ndc_dashboard",
    "data", "database", "ndc_dashboard.db"
)

def query(sql, params=None):
    conn   = sqlite3.connect(DB_PATH)
    result = pd.read_sql(sql, conn, params=params)
    conn.close()
    return result

master_df = query("SELECT * FROM master_countries")
tags_df   = query("SELECT * FROM ndc_sector_tags")

print(f"Loaded {len(master_df)} countries and {len(tags_df)} sector tags")

# ============================================================
# COLOURS
# ============================================================

COLOURS = {
    "background"       : "#0f1117",
    "surface"          : "#1a1d2e",
    "surface_elevated" : "#252840",
    "primary"          : "#00d4aa",
    "primary_dark"     : "#00a884",
    "secondary"        : "#6c63ff",
    "accent"           : "#ff6b6b",
    "text_primary"     : "#ffffff",
    "text_secondary"   : "#a0a3b1",
    "border"           : "#2d3048",
    "tier_1"           : "#00d4aa",
    "tier_2"           : "#f7b731",
    "tier_3"           : "#ff6b6b",
    "high_confidence"  : "#00d4aa",
    "medium_confidence": "#f7b731",
    "low_confidence"   : "#ff6b6b",
}

SECTOR_COLOURS = {
    "Energy"                       : "#f7b731",
    "Transport"                    : "#6c63ff",
    "Land, Agriculture & Forestry" : "#26de81",
    "Water & Blue Economy"         : "#45aaf2",
    "Built Environment & Waste"    : "#fd9644",
    "Industry & Heavy Sector"      : "#a55eea",
    "Nature-Based Solutions"       : "#00d4aa",
}

TIER_COLOURS = {
    "Tier 1 — Established markets" : "#00d4aa",
    "Tier 2 — Emerging markets"    : "#f7b731",
    "Tier 3 — Frontier markets"    : "#ff6b6b",
    "Insufficient data"            : "#555770",
}

# ============================================================
# HELPER COMPONENTS
# ============================================================

def make_kpi_card(title, value, subtitle="", colour=None):
    return dbc.Card([
        dbc.CardBody([
            html.P(title, style={
                "color": COLOURS["text_secondary"],
                "fontSize": "11px",
                "margin": "0",
                "textTransform": "uppercase",
                "letterSpacing": "1px"
            }),
            html.H3(str(value), style={
                "color": colour or COLOURS["primary"],
                "margin": "4px 0",
                "fontSize": "26px",
                "fontWeight": "700"
            }),
            html.P(subtitle, style={
                "color": COLOURS["text_secondary"],
                "fontSize": "11px",
                "margin": "0"
            })
        ])
    ], style={
        "backgroundColor": COLOURS["surface"],
        "border": f"1px solid {COLOURS['border']}",
        "borderRadius": "8px",
        "height": "100%"
    })

# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_map_data():
    df = master_df.copy()

    tier_score = {
        "Tier 1 — Established markets" : 3,
        "Tier 2 — Emerging markets"    : 2,
        "Tier 3 — Frontier markets"    : 1,
        "Insufficient data"            : 0,
    }
    df["tier_score"] = df["investment_tier"].map(tier_score)

    sector_counts = (tags_df
                     .groupby("iso_code")["sector"]
                     .nunique()
                     .reset_index()
                     .rename(columns={"sector": "sector_count"}))
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

    def format_gdp(val):
        if pd.isna(val): return "N/A"
        if val >= 1e12:  return f"${val/1e12:.1f}T"
        if val >= 1e9:   return f"${val/1e9:.1f}B"
        return f"${val/1e6:.0f}M"

    def format_pop(val):
        if pd.isna(val): return "N/A"
        if val >= 1e9:   return f"{val/1e9:.2f}B"
        if val >= 1e6:   return f"{val/1e6:.1f}M"
        return f"{val/1e3:.0f}K"

    df["gdp_display"] = df["gdp_usd"].apply(format_gdp)
    df["pop_display"] = df["population"].apply(format_pop)

    def make_hover(r):
        ndgain = (f"{r['ndgain_score']:.1f}"
                  if pd.notna(r.get("ndgain_score")) else "N/A")
        return (
            f"<b>{r['iso_code']}</b><br>"
            f"Investment Tier: {r['investment_tier']}<br>"
            f"Sectors Identified: {r['sector_count']}<br>"
            f"Conditional Commitments: {r['conditional_count']}<br>"
            f"GDP: {r['gdp_display']}<br>"
            f"Population: {r['pop_display']}<br>"
            f"ND-GAIN Score: {ndgain}"
        )

    df["hover_text"] = df.apply(make_hover, axis=1)
    return df

map_df = prepare_map_data()

# ============================================================
# CHART BUILDERS
# ============================================================

def build_world_map(colour_by="tier_score"):
    colour_configs = {
        "tier_score": {
            "label": "Investment Tier",
            "colorscale": [
                [0.00, "#2d3048"],
                [0.33, "#ff6b6b"],
                [0.66, "#f7b731"],
                [1.00, "#00d4aa"],
            ],
            "range": [0, 3],
        },
        "ndgain_score": {
            "label": "ND-GAIN Score",
            "colorscale": "RdYlGn",
            "range": [20, 75],
        },
        "vulnerability_score": {
            "label": "Climate Vulnerability",
            "colorscale": "RdYlGn_r",
            "range": [0.2, 0.7],
        },
        "renewable_electricity_pct": {
            "label": "Renewable Electricity %",
            "colorscale": "Greens",
            "range": [0, 100],
        },
    }
    cfg = colour_configs.get(colour_by, colour_configs["tier_score"])

    fig = go.Figure(go.Choropleth(
        locations         = map_df["iso_code"],
        z                 = map_df[colour_by],
        text              = map_df["hover_text"],
        hovertemplate     = "%{text}<extra></extra>",
        colorscale        = cfg["colorscale"],
        zmin              = cfg["range"][0],
        zmax              = cfg["range"][1],
        marker_line_color = COLOURS["border"],
        marker_line_width = 0.5,
        colorbar=dict(
            title=dict(
                text=cfg["label"],
                font=dict(color=COLOURS["text_secondary"], size=11)
            ),
            tickfont=dict(color=COLOURS["text_secondary"], size=10),
            bgcolor=COLOURS["surface"],
            bordercolor=COLOURS["border"],
            borderwidth=1,
            thickness=12,
            len=0.6,
        )
    ))

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor=COLOURS["border"],
            showland=True,
            landcolor=COLOURS["surface"],
            showocean=True,
            oceancolor=COLOURS["background"],
            showcountries=True,
            countrycolor=COLOURS["border"],
            bgcolor=COLOURS["background"],
            projection_type="natural earth",
        ),
        paper_bgcolor=COLOURS["background"],
        plot_bgcolor=COLOURS["background"],
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
    )
    return fig


def build_sector_chart():
    sector_summary = (tags_df
                      .groupby("sector")
                      .agg(country_count=("iso_code", "nunique"))
                      .reset_index()
                      .sort_values("country_count", ascending=True))

    colours = [SECTOR_COLOURS.get(s, COLOURS["secondary"])
               for s in sector_summary["sector"]]

    fig = go.Figure(go.Bar(
        x=sector_summary["country_count"],
        y=sector_summary["sector"],
        orientation="h",
        marker_color=colours,
        text=sector_summary["country_count"],
        textposition="outside",
        textfont=dict(color=COLOURS["text_secondary"], size=11),
        hovertemplate="<b>%{y}</b><br>Countries: %{x}<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor=COLOURS["background"],
        plot_bgcolor=COLOURS["surface"],
        font=dict(color=COLOURS["text_primary"], family="Inter"),
        xaxis=dict(showgrid=True, gridcolor=COLOURS["border"],
                   color=COLOURS["text_secondary"],
                   title="Number of Countries"),
        yaxis=dict(color=COLOURS["text_secondary"], showgrid=False),
        margin=dict(l=10, r=40, t=10, b=10),
        height=260,
        bargap=0.3,
    )
    return fig


def build_tier_donut():
    tier_counts = master_df["investment_tier"].value_counts()
    fig = go.Figure(go.Pie(
        labels=tier_counts.index,
        values=tier_counts.values,
        hole=0.65,
        marker=dict(
            colors=[TIER_COLOURS.get(t, "#555770")
                    for t in tier_counts.index],
            line=dict(color=COLOURS["background"], width=2)
        ),
        textfont=dict(color=COLOURS["text_primary"], size=11),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Countries: %{value}<br>"
            "Share: %{percent}<extra></extra>"
        )
    ))
    fig.update_layout(
        paper_bgcolor=COLOURS["background"],
        font=dict(color=COLOURS["text_primary"], family="Inter"),
        showlegend=True,
        legend=dict(
            font=dict(color=COLOURS["text_secondary"], size=10),
            bgcolor="rgba(0,0,0,0)",
            orientation="v",
            x=1.0, y=0.5,
        ),
        margin=dict(l=0, r=80, t=10, b=10),
        height=260,
        annotations=[dict(
            text=f"<b>{len(master_df)}</b><br>Countries",
            x=0.5, y=0.5,
            font=dict(color=COLOURS["text_primary"], size=14),
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
    colours = {
        "Conditional"  : COLOURS["accent"],
        "Unconditional": COLOURS["primary"],
    }
    fig = go.Figure(go.Bar(
        x=commitment_summary["commitment_type"],
        y=commitment_summary["count"],
        marker_color=[colours.get(c, COLOURS["secondary"])
                      for c in commitment_summary["commitment_type"]],
        text=commitment_summary["count"],
        textposition="outside",
        textfont=dict(color=COLOURS["text_secondary"], size=12),
        hovertemplate="<b>%{x}</b><br>Countries: %{y}<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor=COLOURS["background"],
        plot_bgcolor=COLOURS["surface"],
        font=dict(color=COLOURS["text_primary"], family="Inter"),
        xaxis=dict(color=COLOURS["text_secondary"], showgrid=False),
        yaxis=dict(color=COLOURS["text_secondary"],
                   gridcolor=COLOURS["border"],
                   title="Countries"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
        bargap=0.4,
    )
    return fig

# ============================================================
# APP INITIALISATION
# ============================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="NDC Climate Investment Dashboard"
)

GLOBAL_STYLE = {
    "backgroundColor": COLOURS["background"],
    "fontFamily"     : "Inter, sans-serif",
    "color"          : COLOURS["text_primary"],
    "minHeight"      : "100vh",
    "margin"         : "0",
    "padding"        : "0"
}

NAVBAR_STYLE = {
    "backgroundColor": COLOURS["surface"],
    "borderBottom"   : f"1px solid {COLOURS['border']}",
    "padding"        : "12px 24px",
    "position"       : "sticky",
    "top"            : "0",
    "zIndex"         : "1000"
}

navbar = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Span("◆ ", style={"color": COLOURS["primary"],
                                       "fontSize": "18px"}),
                html.Span("NDC Climate Investment Dashboard",
                          style={"fontSize": "16px",
                                 "fontWeight": "600",
                                 "color": COLOURS["text_primary"]}),
                html.Span(" | Research Tool",
                          style={"fontSize": "12px",
                                 "color": COLOURS["text_secondary"],
                                 "marginLeft": "8px"})
            ])
        ], width=6),
        dbc.Col([
            html.Div([
                html.Span("🌐 Global Overview",
                          style={"cursor": "pointer",
                                 "marginRight": "24px",
                                 "fontSize": "13px",
                                 "color": COLOURS["primary"]}),
                html.Span("📋 Country Profile",
                          id="nav-country",
                          style={"cursor": "pointer",
                                 "marginRight": "24px",
                                 "fontSize": "13px",
                                 "color": COLOURS["text_secondary"]}),
                html.Span("🔍 Sector Deep-Dive",
                          id="nav-sector",
                          style={"cursor": "pointer",
                                 "fontSize": "13px",
                                 "color": COLOURS["text_secondary"]})
            ], style={"textAlign": "right"})
        ], width=6)
    ])
], style=NAVBAR_STYLE)

# ============================================================
# KPI CALCULATIONS
# ============================================================

conditional_countries = tags_df[
    tags_df["commitment_type"] == "Conditional"
]["iso_code"].nunique()

total_projects  = int(master_df["wb_project_count"].fillna(0).sum())
avg_ndgain      = round(float(master_df["ndgain_score"].mean()), 1)
avg_renewable   = round(float(master_df["renewable_electricity_pct"].mean()), 1)

# ============================================================
# LAYOUT
# ============================================================

app.layout = html.Div([

    dcc.Location(id="url", refresh=False),
    dcc.Store(id="selected-country", storage_type="session"),

    navbar,

    html.Div([

        # Header
        html.Div([
            html.H4("Global NDC Investment Overview",
                    style={"color": COLOURS["text_primary"],
                           "fontWeight": "600",
                           "margin": "0 0 4px 0"}),
            html.P(
                "Hover over a country to preview. "
                "Click to open the Country Profile.",
                style={"color": COLOURS["text_secondary"],
                       "fontSize": "13px",
                       "margin": "0"}
            )
        ], style={"marginBottom": "20px"}),

        # KPI Row
        dbc.Row([
            dbc.Col(make_kpi_card(
                "NDC Countries", len(master_df),
                "With registered NDCs", COLOURS["primary"]
            ), width=2),
            dbc.Col(make_kpi_card(
                "Conditional Finance Signals", conditional_countries,
                "Countries signalling capital need", COLOURS["accent"]
            ), width=2),
            dbc.Col(make_kpi_card(
                "WB Climate Projects", total_projects,
                "Active pipeline", COLOURS["secondary"]
            ), width=2),
            dbc.Col(make_kpi_card(
                "Avg ND-GAIN Score", avg_ndgain,
                "Climate readiness (0-100)", COLOURS["tier_2"]
            ), width=2),
            dbc.Col(make_kpi_card(
                "Sector Tags", f"{len(tags_df):,}",
                "Across all NDCs", COLOURS["primary"]
            ), width=2),
            dbc.Col(make_kpi_card(
                "Avg Renewable Share", f"{avg_renewable}%",
                "Electricity generation", COLOURS["tier_1"]
            ), width=2),
        ], className="g-3", style={"marginBottom": "20px"}),

        # Map controls
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("Colour map by: ",
                              style={"color": COLOURS["text_secondary"],
                                     "fontSize": "12px",
                                     "marginRight": "8px"}),
                    dcc.Dropdown(
                        id="map-colour-selector",
                        options=[
                            {"label": "Investment Tier",
                             "value": "tier_score"},
                            {"label": "ND-GAIN Score",
                             "value": "ndgain_score"},
                            {"label": "Climate Vulnerability",
                             "value": "vulnerability_score"},
                            {"label": "Renewable Energy %",
                             "value": "renewable_electricity_pct"},
                        ],
                        value="tier_score",
                        clearable=False,
                        style={
                            "width": "220px",
                            "display": "inline-block",
                            "backgroundColor": COLOURS["surface"],
                            "color": COLOURS["text_primary"],
                            "fontSize": "12px",
                        }
                    )
                ], style={"display": "flex", "alignItems": "center"})
            ], width=12)
        ], style={"marginBottom": "12px"}),

        # World Map
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dcc.Graph(
                        id="world-map",
                        figure=build_world_map(),
                        config={"displayModeBar": False,
                                "scrollZoom": True},
                        style={"cursor": "pointer"}
                    )
                ], style={
                    "backgroundColor": COLOURS["surface"],
                    "border": f"1px solid {COLOURS['border']}",
                    "borderRadius": "8px",
                    "padding": "8px"
                })
            ], width=12)
        ], style={"marginBottom": "20px"}),

        # Bottom charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.Div([
                        html.P("Sector Coverage Across NDCs",
                               style={"color": COLOURS["text_primary"],
                                      "fontWeight": "600",
                                      "fontSize": "13px",
                                      "margin": "0 0 12px 0"}),
                        dcc.Graph(id="sector-chart",
                                  figure=build_sector_chart(),
                                  config={"displayModeBar": False})
                    ], style={"padding": "16px"})
                ], style={
                    "backgroundColor": COLOURS["surface"],
                    "border": f"1px solid {COLOURS['border']}",
                    "borderRadius": "8px"
                })
            ], width=5),

            dbc.Col([
                dbc.Card([
                    html.Div([
                        html.P("Investment Tier Distribution",
                               style={"color": COLOURS["text_primary"],
                                      "fontWeight": "600",
                                      "fontSize": "13px",
                                      "margin": "0 0 12px 0"}),
                        dcc.Graph(id="tier-donut",
                                  figure=build_tier_donut(),
                                  config={"displayModeBar": False})
                    ], style={"padding": "16px"})
                ], style={
                    "backgroundColor": COLOURS["surface"],
                    "border": f"1px solid {COLOURS['border']}",
                    "borderRadius": "8px"
                })
            ], width=4),

            dbc.Col([
                dbc.Card([
                    html.Div([
                        html.P("Commitment Type",
                               style={"color": COLOURS["text_primary"],
                                      "fontWeight": "600",
                                      "fontSize": "13px",
                                      "margin": "0 0 12px 0"}),
                        dcc.Graph(id="commitment-chart",
                                  figure=build_commitment_chart(),
                                  config={"displayModeBar": False})
                    ], style={"padding": "16px"})
                ], style={
                    "backgroundColor": COLOURS["surface"],
                    "border": f"1px solid {COLOURS['border']}",
                    "borderRadius": "8px"
                })
            ], width=3),
        ], className="g-3"),

    ], style={"padding": "24px"}),

    # Footer
    html.Div([
        html.Hr(style={"borderColor": COLOURS["border"]}),
        html.P([
            "Data: UNFCCC · Climate Watch · World Bank · "
            "ND-GAIN · Our World in Data · ",
            html.Span(
                "⚠️ Research tool only — not investment advice",
                style={"color": COLOURS["accent"]}
            )
        ], style={"fontSize": "11px",
                  "color": COLOURS["text_secondary"],
                  "textAlign": "center",
                  "padding": "16px"})
    ])

], style=GLOBAL_STYLE)

# ============================================================
# CALLBACKS
# ============================================================

@app.callback(
    Output("world-map", "figure"),
    Input("map-colour-selector", "value")
)
def update_map_colour(colour_by):
    return build_world_map(colour_by)


@app.callback(
    Output("selected-country", "data"),
    Input("world-map", "clickData")
)
def store_selected_country(click_data):
    if click_data is None:
        return None
    try:
        return click_data["points"][0]["location"]
    except Exception:
        return None

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  NDC DASHBOARD — http://127.0.0.1:8050")
    print("="*55 + "\n")
    app.run(debug=False, port=8050, host="127.0.0.1")
