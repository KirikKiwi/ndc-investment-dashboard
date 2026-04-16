# ============================================================
# NDC Investment Dashboard
# pages/landing.py — Introductory landing page
# ============================================================
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dash import html, dcc
import dash_bootstrap_components as dbc
from components import C, T

# ============================================================
# USE CASE CARDS
# ============================================================

USE_CASES = [
    {
        "icon"    : "◈",
        "title"   : "Investment & Finance",
        "text"    : "Identify conditional finance signals and sector-level investment opportunities across 198 countries.",
        "colour"  : C["emerald"],
    },
    {
        "icon"    : "◉",
        "title"   : "Policy Research",
        "text"    : "Analyse NDC commitments, track ambition levels and compare mitigation targets across jurisdictions.",
        "colour"  : C["cobalt"],
    },
    {
        "icon"    : "◎",
        "title"   : "Climate Intelligence",
        "text"    : "Cross-reference vulnerability scores, renewable energy data and MDB project pipelines in one view.",
        "colour"  : C["amber"],
    },
    {
        "icon"    : "◐",
        "title"   : "Education & Training",
        "text"    : "Explore how countries are responding to climate commitments with structured, sourced data.",
        "colour"  : C["industry"],
    },
]

# ============================================================
# STAT STRIP
# ============================================================

STATS = [
    {"value": "198",  "label": "Countries"},
    {"value": "671",  "label": "NDC Indicators"},
    {"value": "7",    "label": "Investment Sectors"},
    {"value": "500+", "label": "MDB Projects"},
]

# ============================================================
# DATA SOURCE LOGOS (text-based)
# ============================================================

SOURCES = [
    "UNFCCC", "Climate Watch", "World Bank",
    "ND-GAIN", "IRENA", "Our World in Data"
]

# ============================================================
# LAYOUT
# ============================================================

def layout():
    return html.Div([

        # ── HERO SECTION ─────────────────────────────────────
        html.Div([

            # Subtle grid background effect via CSS
            html.Div(style={
                "position"        : "absolute",
                "inset"           : "0",
                "backgroundImage" : (
                    f"linear-gradient(to right, "
                    f"{C['border']}44 1px, transparent 1px), "
                    f"linear-gradient(to bottom, "
                    f"{C['border']}44 1px, transparent 1px)"
                ),
                "backgroundSize"  : "60px 60px",
                "pointerEvents"   : "none",
            }),

            # Hero content
            html.Div([

                # Eyebrow label
                html.Div([
                    html.Span("◆ ", style={"color": C["emerald"]}),
                    html.Span(
                        "NDC Climate Investment Intelligence",
                        style={
                            **T["label"],
                            "color"       : C["text_muted"],
                            "letterSpacing": "2px"
                        }
                    )
                ], style={"marginBottom": "28px"}),

                # Main headline
                html.H1([
                    html.Span("Climate Finance\n"),
                    html.Span(
                        "Decoded.",
                        style={"color": C["emerald"]}
                    )
                ], style={
                    **T["hero"],
                    "color"        : C["text"],
                    "fontFamily"   : "Inter, sans-serif",
                    "marginBottom" : "24px",
                    "whiteSpace"   : "pre-line",
                }),

                # Subheadline
                html.P(
                    "A structured research tool mapping NDC commitments, "
                    "sector-level investment signals and climate risk data "
                    "across 198 countries — built for analysts, researchers "
                    "and policy professionals.",
                    style={
                        **T["body"],
                        "color"        : C["text_secondary"],
                        "maxWidth"     : "520px",
                        "marginBottom" : "40px",
                        "lineHeight"   : "1.7"
                    }
                ),

                # CTA Button
                html.A([
                    html.Button([
                        html.Span("Explore the Dashboard  "),
                        html.Span("→", style={"fontWeight": "300"})
                    ], id="enter-btn", style={
                        "backgroundColor" : C["emerald"],
                        "color"           : C["bg"],
                        "border"          : "none",
                        "borderRadius"    : "4px",
                        "padding"         : "14px 32px",
                        "fontSize"        : "14px",
                        "fontWeight"      : "600",
                        "fontFamily"      : "Inter, sans-serif",
                        "cursor"          : "pointer",
                        "letterSpacing"   : "0.3px",
                        "transition"      : "opacity 0.2s",
                    })
                ], href="/dashboard"),

                # Scroll hint
                html.Div([
                    html.Span("↓ ", style={"color": C["emerald"]}),
                    html.Span(
                        "or scroll to learn more",
                        style={
                            **T["micro"],
                            "color": C["text_muted"]
                        }
                    )
                ], style={"marginTop": "20px"})

            ], style={
                "position"   : "relative",
                "zIndex"     : "1",
                "maxWidth"   : "640px",
            })

        ], style={
            "position"        : "relative",
            "backgroundColor" : C["bg"],
            "minHeight"       : "100vh",
            "display"         : "flex",
            "alignItems"      : "center",
            "padding"         : "80px 80px",
            "overflow"        : "hidden",
        }),

        # ── STAT STRIP ───────────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Div(s["value"], style={
                        "fontSize"     : "36px",
                        "fontWeight"   : "700",
                        "color"        : C["emerald"],
                        "fontFamily"   : "Inter, sans-serif",
                        "lineHeight"   : "1",
                        "marginBottom" : "6px"
                    }),
                    html.Div(s["label"], style={
                        **T["label"],
                        "color" : C["text_muted"]
                    })
                ], style={
                    "textAlign"   : "center",
                    "padding"     : "0 40px",
                    "borderRight" : (
                        f"1px solid {C['border']}"
                        if i < len(STATS) - 1 else "none"
                    )
                })
                for i, s in enumerate(STATS)
            ], style={
                "display"        : "flex",
                "justifyContent" : "center",
                "alignItems"     : "center",
            })
        ], style={
            "backgroundColor" : C["surface"],
            "borderTop"       : f"1px solid {C['border']}",
            "borderBottom"    : f"1px solid {C['border']}",
            "padding"         : "40px 80px",
        }),

        # ── USE CASES ────────────────────────────────────────
        html.Div([

            # Section header
            html.Div([
                html.Div(
                    "Built for multiple disciplines",
                    style={
                        **T["label"],
                        "color"        : C["text_muted"],
                        "marginBottom" : "8px"
                    }
                ),
                html.H2(
                    "One tool, many applications",
                    style={
                        **T["h2"],
                        "color"        : C["text"],
                        "marginBottom" : "48px"
                    }
                )
            ]),

            # Use case grid
            html.Div([
                html.Div([
                    html.Div(uc["icon"], style={
                        "fontSize"     : "24px",
                        "color"        : uc["colour"],
                        "marginBottom" : "16px"
                    }),
                    html.Div(uc["title"], style={
                        **T["h3"],
                        "color"        : C["text"],
                        "marginBottom" : "10px"
                    }),
                    html.Div(uc["text"], style={
                        **T["small"],
                        "color"      : C["text_secondary"],
                        "lineHeight" : "1.6"
                    })
                ], style={
                    "backgroundColor" : C["surface"],
                    "border"          : f"1px solid {C['border']}",
                    "borderTop"       : f"2px solid {uc['colour']}",
                    "borderRadius"    : "6px",
                    "padding"         : "24px",
                    "flex"            : "1",
                    "minWidth"        : "200px",
                })
                for uc in USE_CASES
            ], style={
                "display" : "flex",
                "gap"     : "16px",
                "flexWrap": "wrap",
            })

        ], style={
            "backgroundColor" : C["bg"],
            "padding"         : "80px 80px",
        }),

        # ── METHODOLOGY STRIP ────────────────────────────────
        html.Div([

            html.Div(
                "Methodology at a glance",
                style={
                    **T["label"],
                    "color"        : C["text_muted"],
                    "marginBottom" : "8px"
                }
            ),
            html.H2(
                "How this tool works",
                style={
                    **T["h2"],
                    "color"        : C["text"],
                    "marginBottom" : "40px"
                }
            ),

            # Three methodology steps
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("01", style={
                            "fontSize"   : "11px",
                            "fontWeight" : "700",
                            "color"      : C["emerald"],
                            "fontFamily" : "Inter, sans-serif"
                        }),
                    ], style={"marginBottom": "12px"}),
                    html.Div("NDC Ingestion", style={
                        **T["h3"],
                        "color"        : C["text"],
                        "marginBottom" : "8px"
                    }),
                    html.Div(
                        "NDC documents from 198 countries are ingested "
                        "via the Climate Watch API, covering 671 structured "
                        "indicators per submission including mitigation "
                        "targets, adaptation measures and finance signals.",
                        style={
                            **T["small"],
                            "color"      : C["text_secondary"],
                            "lineHeight" : "1.6"
                        }
                    )
                ], style={
                    "flex"        : "1",
                    "paddingRight": "40px",
                    "borderRight" : f"1px solid {C['border']}",
                }),

                html.Div([
                    html.Div([
                        html.Span("02", style={
                            "fontSize"   : "11px",
                            "fontWeight" : "700",
                            "color"      : C["emerald"],
                            "fontFamily" : "Inter, sans-serif"
                        }),
                    ], style={"marginBottom": "12px"}),
                    html.Div("Sector Classification", style={
                        **T["h3"],
                        "color"        : C["text"],
                        "marginBottom" : "8px"
                    }),
                    html.Div(
                        "A 357-keyword taxonomy maps NDC text to seven "
                        "investment sectors. Each tag carries a confidence "
                        "score — High, Medium or Low — based on the strength "
                        "of keyword evidence. Dimension flags capture "
                        "mitigation vs adaptation, commitment type and "
                        "financing instrument signals.",
                        style={
                            **T["small"],
                            "color"      : C["text_secondary"],
                            "lineHeight" : "1.6"
                        }
                    )
                ], style={
                    "flex"         : "1",
                    "padding"      : "0 40px",
                    "borderRight"  : f"1px solid {C['border']}",
                }),

                html.Div([
                    html.Div([
                        html.Span("03", style={
                            "fontSize"   : "11px",
                            "fontWeight" : "700",
                            "color"      : C["emerald"],
                            "fontFamily" : "Inter, sans-serif"
                        }),
                    ], style={"marginBottom": "12px"}),
                    html.Div("Data Enrichment", style={
                        **T["h3"],
                        "color"        : C["text"],
                        "marginBottom" : "8px"
                    }),
                    html.Div(
                        "Country profiles are enriched with World Bank "
                        "economic indicators, ND-GAIN climate vulnerability "
                        "scores, World Bank MDB project pipelines and "
                        "renewable energy policy data from Our World in Data.",
                        style={
                            **T["small"],
                            "color"      : C["text_secondary"],
                            "lineHeight" : "1.6"
                        }
                    )
                ], style={
                    "flex"       : "1",
                    "paddingLeft": "40px",
                }),

            ], style={
                "display" : "flex",
                "gap"     : "0",
            }),

        ], style={
            "backgroundColor" : C["surface"],
            "borderTop"       : f"1px solid {C['border']}",
            "borderBottom"    : f"1px solid {C['border']}",
            "padding"         : "80px 80px",
        }),

        # ── DATA SOURCES ─────────────────────────────────────
        html.Div([

            html.Div(
                "Open source data only",
                style={
                    **T["label"],
                    "color"        : C["text_muted"],
                    "marginBottom" : "24px",
                    "textAlign"    : "center"
                }
            ),

            html.Div([
                html.Span(source, style={
                    "color"         : C["text_muted"],
                    "fontSize"      : "13px",
                    "fontWeight"    : "500",
                    "padding"       : "6px 16px",
                    "border"        : f"1px solid {C['border']}",
                    "borderRadius"  : "3px",
                    "fontFamily"    : "Inter, sans-serif",
                })
                for source in SOURCES
            ], style={
                "display"        : "flex",
                "justifyContent" : "center",
                "gap"            : "10px",
                "flexWrap"       : "wrap",
            }),

        ], style={
            "backgroundColor" : C["bg"],
            "padding"         : "60px 80px",
        }),

        # ── FINAL CTA ────────────────────────────────────────
        html.Div([
            html.Div([
                html.H2([
                    "Ready to explore?  ",
                    html.Span(
                        "◆",
                        style={"color": C["emerald"]}
                    )
                ], style={
                    **T["h2"],
                    "color"        : C["text"],
                    "marginBottom" : "16px"
                }),
                html.P(
                    "Open the interactive dashboard to explore "
                    "NDC investment signals across 198 countries.",
                    style={
                        **T["body"],
                        "color"        : C["text_secondary"],
                        "marginBottom" : "32px"
                    }
                ),
                html.A([
                    html.Button([
                        html.Span("Open Dashboard  "),
                        html.Span("→")
                    ], style={
                        "backgroundColor" : C["emerald"],
                        "color"           : C["bg"],
                        "border"          : "none",
                        "borderRadius"    : "4px",
                        "padding"         : "14px 32px",
                        "fontSize"        : "14px",
                        "fontWeight"      : "600",
                        "fontFamily"      : "Inter, sans-serif",
                        "cursor"          : "pointer",
                    })
                ], href="/dashboard"),

                # Disclaimer
                html.P(
                    "⚠️  For research purposes only. "
                    "Not investment advice.",
                    style={
                        **T["micro"],
                        "color"     : C["text_muted"],
                        "marginTop" : "24px"
                    }
                )
            ], style={"textAlign": "center"})

        ], style={
            "backgroundColor" : C["surface"],
            "borderTop"       : f"1px solid {C['border']}",
            "padding"         : "100px 80px",
        }),

    ], style={
        "fontFamily"      : "Inter, sans-serif",
        "backgroundColor" : C["bg"],
    })


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    page = layout()
    print("✅ landing.py verified")
    print(f"   Sections  : Hero, Stats, Use Cases, "
          f"Methodology, Sources, CTA")
    print(f"   Use cases : {len(USE_CASES)}")
    print(f"   Sources   : {len(SOURCES)}")
    print(f"   CTA routes to: /dashboard")