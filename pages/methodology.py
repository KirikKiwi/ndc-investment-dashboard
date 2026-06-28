# ============================================================
# NDC Investment Dashboard
# pages/methodology.py: Methodology documentation page
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import html
from components import C, T

SECTIONS = [
    "Data Sources and Retrieval",
    "NDC Priority and Selection Logic",
    "Sector Taxonomy (357 keywords, 7 sectors)",
    "Confidence Scoring",
    "Investment Tier Classification",
    "Composite Benchmark Formula",
    "Finance Signal Extraction",
    "Governance Indicators (WGI)",
    "Climate Finance Flows (OECD Rio Markers)",
    "News Feed and Credibility Scoring",
]


def layout():
    return html.Div([

        # Page header
        html.Div([
            html.Div([
                html.Div(
                    "Methodology",
                    style={
                        "fontSize"      : "11px",
                        "fontWeight"    : "600",
                        "textTransform" : "uppercase",
                        "letterSpacing" : "1.5px",
                        "color"         : C["text_muted"],
                        "marginBottom"  : "8px",
                        "fontFamily"    : "Inter, sans-serif",
                    }
                ),
                html.H1(
                    "How Green-Gott's Vault works",
                    style={
                        "fontSize"     : "28px",
                        "fontWeight"   : "700",
                        "color"        : C["text"],
                        "marginBottom" : "12px",
                        "fontFamily"   : "Inter, sans-serif",
                        "letterSpacing": "-0.5px",
                    }
                ),
                html.P(
                    "Full documentation of data sources, classification logic "
                    "and scoring methodology. Sections are being published "
                    "progressively.",
                    style={
                        "fontSize"   : "14px",
                        "color"      : C["text_secondary"],
                        "fontFamily" : "Inter, sans-serif",
                        "lineHeight" : "1.6",
                        "maxWidth"   : "600px",
                    }
                ),
            ], style={
                "maxWidth" : "800px",
            })
        ], style={
            "backgroundColor" : C["bg"],
            "borderBottom"    : f"1px solid {C['border']}",
            "padding"         : "60px 80px 40px",
        }),

        # Sections
        html.Div([
            html.Div([

                html.Div([
                    html.Div([
                        html.Div(f"{i+1:02d}", style={
                            "fontSize"     : "11px",
                            "fontWeight"   : "700",
                            "color"        : C["emerald"],
                            "fontFamily"   : "Inter, sans-serif",
                            "marginBottom" : "8px",
                        }),
                        html.Div(section, style={
                            "fontSize"   : "15px",
                            "fontWeight" : "600",
                            "color"      : C["text"],
                            "fontFamily" : "Inter, sans-serif",
                            "marginBottom": "8px",
                        }),
                        html.Div("Content coming soon.", style={
                            "fontSize"   : "13px",
                            "color"      : C["text_muted"],
                            "fontFamily" : "Inter, sans-serif",
                            "fontStyle"  : "italic",
                        }),
                    ], style={
                        "backgroundColor" : C["surface_high"],
                        "border"          : f"1px solid {C['border']}",
                        "borderLeft"      : f"2px solid {C['emerald']}",
                        "borderRadius"    : "4px",
                        "padding"         : "18px 20px",
                    })
                ], style={"marginBottom": "12px"})

                for i, section in enumerate(SECTIONS)

            ], style={"maxWidth": "800px"})
        ], style={
            "backgroundColor" : C["bg"],
            "padding"         : "40px 80px 80px",
        }),

    ], style={
        "fontFamily"      : "Inter, sans-serif",
        "backgroundColor" : C["bg"],
        "minHeight"       : "100vh",
    })


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    page = layout()
    print("✅ methodology.py verified")
    print(f"   Sections: {len(SECTIONS)}")
