# ============================================================
# NDC Investment Dashboard
# news_render.py: Dash components for news feed display
# Sprint 3
# ============================================================

from dash import html
from components import C

# ============================================================
# TIER BADGE
# ============================================================

TIER_LABELS = {1: "T1", 2: "T2", 3: "T3", 4: "T4"}
TIER_COLOURS = {
    1: C["emerald"],
    2: C["cobalt"],
    3: C["amber"],
    4: C["text_muted"],
}

def _tier_badge(tier):
    colour = TIER_COLOURS.get(tier, C["text_muted"])
    label  = TIER_LABELS.get(tier, "")
    return html.Span(label, style={
        "backgroundColor" : colour + "18",
        "color"           : colour,
        "border"          : f"1px solid {colour}40",
        "borderRadius"    : "3px",
        "padding"         : "1px 5px",
        "fontSize"        : "9px",
        "fontWeight"      : "700",
        "fontFamily"      : "Inter, sans-serif",
        "letterSpacing"   : "0.5px",
        "marginLeft"      : "6px",
        "verticalAlign"   : "middle",
    })


# ============================================================
# ARTICLE CARD
# ============================================================

def article_card(article):
    """
    Renders a single news article as a styled card.
    Expects dict with: title, summary, url, image_url,
    source, tier, date, score.
    """
    title     = article.get("title", "")
    summary   = article.get("summary", "")
    url       = article.get("url", "")
    image_url = article.get("image_url")
    source    = article.get("source", "")
    tier      = article.get("tier", 2)
    date      = article.get("date", "")

    # ── Image thumbnail (if available)
    image_el = None
    if image_url:
        image_el = html.Img(src=image_url, style={
            "width"        : "60px",
            "height"       : "60px",
            "objectFit"    : "cover",
            "borderRadius" : "4px",
            "flexShrink"   : "0",
        })

    # ── Source + date + tier line
    meta_parts = [
        html.Span(source, style={
            "fontSize"   : "10px",
            "fontWeight" : "600",
            "color"      : C["text_secondary"],
            "fontFamily" : "Inter, sans-serif",
        }),
        _tier_badge(tier),
    ]
    if article.get("match_type") == "global":
        meta_parts.append(
            html.Span("  ·  Global", style={
                "fontSize"   : "10px",
                "color"      : C["amber"],
                "fontFamily" : "Inter, sans-serif",
                "fontStyle"  : "italic",
            })
        )
    if date:
        meta_parts.append(
            html.Span(f"  ·  {date}", style={
                "fontSize"   : "10px",
                "color"      : C["text_muted"],
                "fontFamily" : "Inter, sans-serif",
            })
        )

    # ── Card content
    text_content = html.Div([
        html.Div(meta_parts, style={"marginBottom": "4px"}),
        html.A(
            title,
            href=url,
            target="_blank",
            style={
                "fontSize"       : "12px",
                "fontWeight"     : "600",
                "color"          : C["text"],
                "fontFamily"     : "Inter, sans-serif",
                "textDecoration" : "none",
                "lineHeight"     : "1.4",
                "display"        : "block",
                "marginBottom"   : "3px",
            }
        ),
        html.Div(
            summary[:120] + "..." if len(summary) > 120 else summary,
            style={
                "fontSize"   : "11px",
                "color"      : C["text_secondary"],
                "fontFamily" : "Inter, sans-serif",
                "lineHeight" : "1.5",
            }
        ) if summary else html.Div(),
    ], style={"flex": "1", "minWidth": "0"})

    # ── Assemble card
    card_children = []
    if image_el:
        card_children = [image_el, text_content]
        card_style = {
            "display"      : "flex",
            "gap"          : "10px",
            "alignItems"   : "flex-start",
            "padding"      : "10px 0",
            "borderBottom" : f"1px solid {C['border']}",
        }
    else:
        card_children = [text_content]
        card_style = {
            "padding"      : "10px 0",
            "borderBottom" : f"1px solid {C['border']}",
        }

    return html.Div(card_children, style=card_style)


# ============================================================
# SECTION RENDERERS
# ============================================================

def render_news_feed(articles, empty_message="No recent news found."):
    """
    Renders a list of articles as a styled feed section.
    Returns a Dash component.
    """
    if not articles:
        return html.Div([
            html.Div("○", style={
                "fontSize"     : "16px",
                "color"        : C["text_muted"],
                "marginBottom" : "4px",
            }),
            html.Div(empty_message, style={
                "fontSize"   : "11px",
                "color"      : C["text_muted"],
                "fontFamily" : "Inter, sans-serif",
            })
        ], style={
            "textAlign"       : "center",
            "padding"         : "16px",
            "backgroundColor" : C["surface_high"],
            "border"          : f"1px solid {C['border']}",
            "borderRadius"    : "4px",
        })

    cards = [article_card(a) for a in articles]

    return html.Div(cards, style={
        "backgroundColor" : C["surface_high"],
        "border"          : f"1px solid {C['border']}",
        "borderRadius"    : "4px",
        "padding"         : "4px 14px",
    })


def loading_placeholder():
    """Shown while news loads asynchronously."""
    return html.Div([
        html.Div("◌", style={
            "fontSize"     : "16px",
            "color"        : C["text_muted"],
            "marginBottom" : "4px",
            "animation"    : "pulse 1.5s infinite",
        }),
        html.Div("Loading news feed...", style={
            "fontSize"   : "11px",
            "color"      : C["text_muted"],
            "fontFamily" : "Inter, sans-serif",
        })
    ], style={
        "textAlign"       : "center",
        "padding"         : "16px",
        "backgroundColor" : C["surface_high"],
        "border"          : f"1px solid {C['border']}",
        "borderRadius"    : "4px",
    })


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    print("news_render.py loaded")
    print("  Components: article_card, render_news_feed, loading_placeholder")
    print("  Tier badges: T1-T4")
