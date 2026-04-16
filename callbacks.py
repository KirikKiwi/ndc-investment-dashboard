# ============================================================
# NDC Investment Dashboard
# callbacks.py — All interactivity logic
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash import Input, Output, callback, no_update
from pages.globe import (build_globe, country_panel_content,
                         empty_panel)

# ============================================================
# GLOBE — Update colour on selector change
# ============================================================

@callback(
    Output("globe-map", "figure"),
    Input("globe-colour-selector", "value"),
    Input("projection-selector",   "value"),
)
def update_globe(colour_by, projection):
    return build_globe(
        colour_by  = colour_by  or "tier_score",
        projection = projection or "orthographic"
    )


# ============================================================
# COUNTRY PANEL — Open on country click
# ============================================================

@callback(
    Output("country-panel-content", "children"),
    Input("globe-map", "clickData"),
)
def update_country_panel(click_data):
    if click_data is None:
        return empty_panel()
    try:
        iso = click_data["points"][0]["location"]
        return country_panel_content(iso)
    except Exception:
        return empty_panel()


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    print("✅ callbacks.py verified")
    print("   Callbacks defined:")
    print("   - update_globe (colour + projection)")
    print("   - update_country_panel (country click)")