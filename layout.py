# ============================================================
# NDC Investment Dashboard
# layout.py — Page routing and app layout assembly
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash import html, dcc
from components import C, T
from pages.landing import layout as landing_layout
from pages.globe   import layout as globe_layout

# ============================================================
# NAVBAR
# ============================================================

def navbar():
    return html.Div([
        html.Div([

            # Logo
            html.A([
                html.Span("◆ ", style={
                    "color"    : C["emerald"],
                    "fontSize" : "16px"
                }),
                html.Span("NDC Intelligence", style={
                    "fontSize"   : "14px",
                    "fontWeight" : "600",
                    "color"      : C["text"],
                    "fontFamily" : "Inter, sans-serif",
                })
            ], href="/", style={
                "textDecoration" : "none",
                "display"        : "flex",
                "alignItems"     : "center",
                "gap"            : "2px",
            }),

            # Navigation links
            html.Div([
                html.A("Dashboard", href="/dashboard", style={
                    "color"          : C["text_secondary"],
                    "textDecoration" : "none",
                    "fontSize"       : "13px",
                    "fontFamily"     : "Inter, sans-serif",
                    "padding"        : "6px 12px",
                    "borderRadius"   : "4px",
                }),
                html.A("Methodology", href="/", style={
                    "color"          : C["text_secondary"],
                    "textDecoration" : "none",
                    "fontSize"       : "13px",
                    "fontFamily"     : "Inter, sans-serif",
                    "padding"        : "6px 12px",
                }),
                html.Span(
                    "Beta",
                    style={
                        "backgroundColor" : C["emerald"] + "20",
                        "color"           : C["emerald"],
                        "border"          : f"1px solid {C['emerald']}40",
                        "borderRadius"    : "3px",
                        "padding"         : "2px 8px",
                        "fontSize"        : "10px",
                        "fontWeight"      : "600",
                        "fontFamily"      : "Inter, sans-serif",
                        "letterSpacing"   : "1px",
                    }
                )
            ], style={
                "display"    : "flex",
                "alignItems" : "center",
                "gap"        : "4px",
            })

        ], style={
            "display"        : "flex",
            "justifyContent" : "space-between",
            "alignItems"     : "center",
            "maxWidth"       : "100%",
            "padding"        : "0 32px",
            "height"         : "52px",
        })

    ], style={
        "backgroundColor" : C["surface"],
        "borderBottom"    : f"1px solid {C['border']}",
        "position"        : "sticky",
        "top"             : "0",
        "zIndex"          : "1000",
    })


# ============================================================
# APP LAYOUT
# ============================================================

def create_layout():
    return html.Div([

        # URL routing
        dcc.Location(id="url", refresh=False),

        # Session storage for selected country
        dcc.Store(id="selected-country", storage_type="session"),

        # Navbar
        navbar(),

        # Page content — rendered by callback
        html.Div(id="page-content"),

    ], style={
        "backgroundColor" : C["bg"],
        "fontFamily"      : "Inter, sans-serif",
        "minHeight"       : "100vh",
        "margin"          : "0",
        "padding"         : "0",
    })


# ============================================================
# PAGE ROUTER CALLBACK
# ============================================================

from dash import callback, Output, Input

@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def route(pathname):
    if pathname == "/dashboard":
        return globe_layout()
    return landing_layout()


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    layout = create_layout()
    print("✅ layout.py verified")
    print("   Routes defined:")
    print("   /           → Landing page")
    print("   /dashboard  → Globe + analytics")
    print("   Navbar      : Logo + Dashboard + Methodology + Beta")