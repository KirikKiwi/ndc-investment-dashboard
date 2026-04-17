# ============================================================
# NDC Investment Dashboard
# callbacks.py — All interactivity
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash import Input, Output, callback
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
