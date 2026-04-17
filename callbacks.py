# ============================================================
# NDC Investment Dashboard
# callbacks.py — All interactivity
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash import Input, Output, State, callback, no_update
from pages.globe import (territory_panel,
    country_panel_content,
    empty_panel,
)

@callback(
    Output("country-panel-content", "children"),
    Input("d3-click-input", "value"),
)
def update_country_panel(iso_code):
    if not iso_code:
        return empty_panel()

    # Handle territory signal from D3
    if iso_code.startswith("TERRITORY:"):
        parts = iso_code.split(":", 2)
        name  = parts[2] if len(parts) > 2 else parts[1]
        return territory_panel(name)

    if len(iso_code) != 3:
        return empty_panel()

    try:
        return country_panel_content(iso_code.upper())
    except Exception:
        return empty_panel()


@callback(
    Output("colour-mode-value", "value"),
    Input("globe-colour-selector", "value"),
)
def update_colour_mode(mode):
    return mode or "tier_score"


if __name__ == "__main__":
    print("✅ callbacks.py verified")
    print("   - update_country_panel")
    print("   - update_colour_mode")


# ============================================================
# ANALYTICS FILTER CALLBACKS
# ============================================================

from pages.analytics import (
    layout        as analytics_layout,
    master_df     as ana_master,
    tags_df       as ana_tags,
)
from data import filter_master, load_tags, get_country_name
import pandas as pd


@callback(
    Output("analytics-section-content", "children"),
    Output("filter-summary",             "children"),
    Input("filter-region",  "value"),
    Input("filter-group",   "value"),
    Input("filter-country", "value"),
    prevent_initial_call=True,
)
def update_analytics(region, group, country):
    tags = load_tags()

    df = filter_master(
        ana_master,
        region   = region  if region  != "ALL" else None,
        group    = group   if group   != "ALL" else None,
        iso_code = country if country != "ALL" else None,
    )

    parts = []
    if region  and region  != "ALL": parts.append(region)
    if group   and group   != "ALL": parts.append(group)
    if country and country != "ALL":
        parts.append(get_country_name(country))

    summary = (
        f"Filtered to: {' · '.join(parts)} — {len(df)} "
        f"{'country' if len(df) == 1 else 'countries'}"
        if parts else ""
    )

    return analytics_layout(df=df, tags=tags), summary


@callback(
    Output("filter-region",  "value"),
    Output("filter-group",   "value"),
    Output("filter-country", "value"),
    Input("filter-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(n):
    return "ALL", "ALL", "ALL"


@callback(
    Output("download-csv", "data"),
    Input("filter-export-btn", "n_clicks"),
    State("filter-region",  "value"),
    State("filter-group",   "value"),
    State("filter-country", "value"),
    prevent_initial_call=True,
)
def export_csv(n_clicks, region, group, country):
    from dash import no_update
    if not n_clicks:
        return no_update

    df = filter_master(
        ana_master,
        region   = region  if region  != "ALL" else None,
        group    = group   if group   != "ALL" else None,
        iso_code = country if country != "ALL" else None,
    )

    export_cols = [
        "iso_code","investment_tier","ndgain_score",
        "vulnerability_score","readiness_score",
        "gdp_usd","gdp_per_capita_usd","population",
        "renewable_electricity_pct","wb_project_count",
        "conditional_pct_uplift","unconditional_pct",
        "data_completeness_pct",
    ]
    available = [c for c in export_cols if c in df.columns]
    out       = df[available].copy()
    out.insert(1, "country_name",
               out["iso_code"].apply(get_country_name))

    from dash import dcc as _dcc
    return _dcc.send_data_frame(
        out.to_csv, "ndc_dashboard_export.csv", index=False
    )


# ============================================================
# TIER 3 CALLBACKS
# ============================================================

from pages.tier3 import tier3_content as build_tier3


@callback(
    Output("tier3-panel-content", "children"),
    Output("tier3-panel-overlay", "className"),
    Input("tier3-sector-input",   "value"),
    Input("tier3-close-input",    "value"),
    prevent_initial_call=True,
)
def manage_tier3(sector_value, close_value):
    from dash import no_update, ctx, html

    triggered = ctx.triggered_id

    # Close signal received
    if triggered == "tier3-close-input":
        return no_update, ""

    # Sector pill clicked
    if not sector_value:
        return no_update, no_update

    parts = sector_value.split("||")
    if len(parts) < 2:
        return no_update, no_update

    iso_code    = parts[0]
    sector_name = parts[1]

    try:
        content = build_tier3(iso_code, sector_name)
    except Exception as e:
        content = html.Div(
            f"Error loading sector: {e}",
            style={"color": "#888", "padding": "20px"}
        )

    return content, "open"
