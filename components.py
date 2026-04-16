# ============================================================
# NDC Investment Dashboard
# components.py — Design system and reusable UI elements
# ============================================================

from dash import html
import dash_bootstrap_components as dbc

# ============================================================
# COLOUR SYSTEM
# ============================================================

C = {
    # Base canvas
    "bg"              : "#0a0a0a",
    "surface"         : "#111111",
    "surface_high"    : "#1a1a1a",
    "border"          : "#2a2a2a",
    "border_light"    : "#333333",

    # Text
    "text"            : "#f0f0f0",
    "text_secondary"  : "#888888",
    "text_muted"      : "#555555",

    # Primary accent
    "emerald"         : "#00c896",
    "emerald_dim"     : "#00c89620",

    # Sector colours
    "energy"          : "#f0a500",
    "transport"       : "#2980b9",
    "land"            : "#27ae60",
    "water"           : "#00bcd4",
    "built"           : "#e67e22",
    "industry"        : "#8e44ad",
    "nature"          : "#00c896",

    # Signal colours
    "crimson"         : "#c0392b",
    "crimson_dim"     : "#c0392b20",
    "amber"           : "#e67e22",
    "amber_dim"       : "#e67e2220",
    "cobalt"          : "#2980b9",
    "cobalt_dim"      : "#2980b920",
    "burgundy"        : "#7b1c1c",

    # Tier colours
    "tier1"           : "#00c896",
    "tier2"           : "#e67e22",
    "tier3"           : "#c0392b",
    "tier_none"       : "#333333",

    # Confidence
    "high"            : "#00c896",
    "medium"          : "#e67e22",
    "low"             : "#c0392b",
}

# ============================================================
# SECTOR COLOUR MAP
# ============================================================

SECTOR_COLOURS = {
    "Energy"                       : C["energy"],
    "Transport"                    : C["transport"],
    "Land, Agriculture & Forestry" : C["land"],
    "Water & Blue Economy"         : C["water"],
    "Built Environment & Waste"    : C["built"],
    "Industry & Heavy Sector"      : C["industry"],
    "Nature-Based Solutions"       : C["nature"],
}

TIER_COLOURS = {
    "Tier 1 — Established markets" : C["tier1"],
    "Tier 2 — Emerging markets"    : C["tier2"],
    "Tier 3 — Frontier markets"    : C["tier3"],
    "Insufficient data"            : C["tier_none"],
}

CONFIDENCE_COLOURS = {
    "High"   : C["high"],
    "Medium" : C["medium"],
    "Low"    : C["low"],
}

# ============================================================
# TYPOGRAPHY SCALE
# ============================================================

T = {
    "hero"    : {"fontSize": "52px", "fontWeight": "700",
                 "letterSpacing": "-1px", "lineHeight": "1.1"},
    "h1"      : {"fontSize": "32px", "fontWeight": "700",
                 "letterSpacing": "-0.5px"},
    "h2"      : {"fontSize": "22px", "fontWeight": "600"},
    "h3"      : {"fontSize": "16px", "fontWeight": "600"},
    "h4"      : {"fontSize": "13px", "fontWeight": "600",
                 "textTransform": "uppercase",
                 "letterSpacing": "1.5px"},
    "body"    : {"fontSize": "14px", "fontWeight": "400",
                 "lineHeight": "1.6"},
    "small"   : {"fontSize": "12px", "fontWeight": "400"},
    "micro"   : {"fontSize": "11px", "fontWeight": "400",
                 "letterSpacing": "0.5px"},
    "label"   : {"fontSize": "11px", "fontWeight": "600",
                 "textTransform": "uppercase",
                 "letterSpacing": "1.5px"},
}

# ============================================================
# SHARED STYLES
# ============================================================

CARD_STYLE = {
    "backgroundColor" : C["surface"],
    "border"          : f"1px solid {C['border']}",
    "borderRadius"    : "6px",
    "padding"         : "20px",
}

CARD_ELEVATED = {
    **CARD_STYLE,
    "backgroundColor" : C["surface_high"],
    "border"          : f"1px solid {C['border_light']}",
}

# ============================================================
# REUSABLE COMPONENTS
# ============================================================

def kpi_card(title, value, subtitle="", colour=None, border_colour=None):
    """
    A single KPI metric card.
    Used in the global overview strip.
    """
    accent = colour or C["emerald"]
    border = border_colour or C["border"]

    return html.Div([
        html.Div(title, style={
            **T["label"],
            "color"         : C["text_muted"],
            "marginBottom"  : "8px"
        }),
        html.Div(str(value), style={
            "fontSize"      : "28px",
            "fontWeight"    : "700",
            "color"         : accent,
            "lineHeight"    : "1",
            "marginBottom"  : "6px",
            "fontFamily"    : "Inter, sans-serif"
        }),
        html.Div(subtitle, style={
            **T["micro"],
            "color"         : C["text_muted"]
        })
    ], style={
        "backgroundColor"   : C["surface"],
        "border"            : f"1px solid {border}",
        "borderTop"         : f"2px solid {accent}",
        "borderRadius"      : "6px",
        "padding"           : "16px 20px",
        "minWidth"          : "140px",
    })


def section_header(title, subtitle=None):
    """Section title with optional subtitle."""
    return html.Div([
        html.Div(title, style={
            **T["h4"],
            "color"        : C["text_muted"],
            "marginBottom" : "4px"
        }),
        html.Div(subtitle, style={
            **T["h2"],
            "color"        : C["text"],
        }) if subtitle else None
    ], style={"marginBottom": "24px"})


def confidence_badge(level):
    """Colour-coded confidence indicator badge."""
    colour = CONFIDENCE_COLOURS.get(level, C["text_muted"])
    return html.Span(level, style={
        "backgroundColor" : colour + "20",
        "color"           : colour,
        "border"          : f"1px solid {colour}40",
        "borderRadius"    : "3px",
        "padding"         : "2px 8px",
        **T["micro"],
        "fontWeight"      : "600"
    })


def sector_pill(sector_name):
    """Coloured sector identification pill."""
    colour = SECTOR_COLOURS.get(sector_name, C["text_muted"])
    short  = sector_name.split(" & ")[0].split(",")[0]
    return html.Span(short, style={
        "backgroundColor" : colour + "18",
        "color"           : colour,
        "border"          : f"1px solid {colour}30",
        "borderRadius"    : "12px",
        "padding"         : "3px 10px",
        **T["micro"],
        "marginRight"     : "4px",
        "marginBottom"    : "4px",
        "display"         : "inline-block"
    })


def tier_badge(tier):
    """Investment tier badge."""
    colour = TIER_COLOURS.get(tier, C["tier_none"])
    label  = tier.split(" — ")[1] if " — " in tier else tier
    return html.Span(label, style={
        "backgroundColor" : colour + "18",
        "color"           : colour,
        "border"          : f"1px solid {colour}40",
        "borderRadius"    : "3px",
        "padding"         : "3px 10px",
        **T["small"],
        "fontWeight"      : "600"
    })


def divider():
    """Subtle horizontal divider."""
    return html.Hr(style={
        "borderColor"  : C["border"],
        "margin"       : "20px 0",
        "opacity"      : "1"
    })


def data_row(label, value, colour=None):
    """
    A single label-value row for the country panel.
    Used to display NDC data points cleanly.
    """
    return html.Div([
        html.Span(label, style={
            **T["micro"],
            "color"      : C["text_muted"],
            "display"    : "block",
            "marginBottom": "2px"
        }),
        html.Span(str(value) if value else "N/A", style={
            **T["small"],
            "color"      : colour or C["text"],
            "fontWeight" : "500"
        })
    ], style={"marginBottom": "14px"})


def flag_pill(text, colour=None):
    """
    A small flag pill for data quality indicators.
    Used for translation flags, data gaps etc.
    """
    c = colour or C["amber"]
    return html.Span(text, style={
        "backgroundColor" : c + "18",
        "color"           : c,
        "border"          : f"1px solid {c}40",
        "borderRadius"    : "3px",
        "padding"         : "2px 8px",
        **T["micro"],
        "display"         : "inline-block",
        "marginRight"     : "4px"
    })


def loading_state(message="Loading data..."):
    """Placeholder shown while data loads."""
    return html.Div([
        html.Div("◌", style={
            "fontSize"     : "32px",
            "color"        : C["text_muted"],
            "marginBottom" : "12px"
        }),
        html.Div(message, style={
            **T["small"],
            "color" : C["text_muted"]
        })
    ], style={
        "textAlign"  : "center",
        "padding"    : "48px 24px"
    })


def empty_state(message="No data available", submessage=None):
    """Shown when a query returns no results."""
    return html.Div([
        html.Div("○", style={
            "fontSize"     : "28px",
            "color"        : C["text_muted"],
            "marginBottom" : "12px"
        }),
        html.Div(message, style={
            **T["body"],
            "color"        : C["text_secondary"],
            "marginBottom" : "4px"
        }),
        html.Div(submessage, style={
            **T["small"],
            "color" : C["text_muted"]
        }) if submessage else None
    ], style={
        "textAlign"  : "center",
        "padding"    : "40px 24px"
    })


# ============================================================
# VERIFY ON IMPORT
# ============================================================

if __name__ == "__main__":
    print("✅ components.py verified")
    print(f"   Colours defined    : {len(C)}")
    print(f"   Sector colours     : {len(SECTOR_COLOURS)}")
    print(f"   Typography scales  : {len(T)}")
    print(f"   Components defined : 10")
    print(f"\n   Palette preview:")
    for name, hex_val in list(C.items())[:8]:
        print(f"   {name:<20} {hex_val}")