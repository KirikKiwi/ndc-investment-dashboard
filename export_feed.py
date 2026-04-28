# ============================================================
# NDC Investment Dashboard
# export_feed.py — Export news feed to Excel
# Run weekly alongside aggregator to maintain local archive
# Sprint 3
# ============================================================

import os
import sqlite3
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "database", "ndc_dashboard.db"
)

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "exports"
)

# ── Colour scheme matching dashboard
DARK_BG     = "0A0A0A"
SURFACE     = "111111"
HEADER_BG   = "1A1A1A"
BORDER_CLR  = "2A2A2A"
EMERALD     = "00C896"
TEXT        = "F0F0F0"
TEXT_SEC    = "888888"
AMBER       = "E67E22"
COBALT      = "2980B9"
CRIMSON     = "C0392B"

TIER_FILLS = {
    1: PatternFill(start_color="00C89620", end_color="00C89620", fill_type="solid"),
    2: PatternFill(start_color="2980B920", end_color="2980B920", fill_type="solid"),
    3: PatternFill(start_color="E67E2220", end_color="E67E2220", fill_type="solid"),
}

TIER_FONTS = {
    1: Font(color=EMERALD, size=10, bold=True),
    2: Font(color=COBALT, size=10, bold=True),
    3: Font(color=AMBER, size=10, bold=True),
}


def export_to_excel(output_path=None):
    """
    Exports the full news_feed table to a styled Excel file.
    Returns the output file path.
    """
    if not output_path:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_path = os.path.join(
            OUTPUT_DIR,
            f"ndc_newsfeed_{timestamp}.xlsx"
        )

    # ── Fetch all articles
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT title, summary, url, source_label, source_tier,
               category, published_date, countries, sectors,
               credibility_score, image_url
        FROM news_feed
        ORDER BY credibility_score DESC, published_date DESC
    """).fetchall()
    conn.close()

    # ── Create workbook
    wb = Workbook()

    # ──────────────────────────────────────────────────────
    # SHEET 1: All Articles
    # ──────────────────────────────────────────────────────
    ws = wb.active
    ws.title = "All Articles"

    headers = [
        "Title", "Source", "Tier", "Category", "Date",
        "Countries", "Sectors", "Score", "Summary", "URL"
    ]
    widths = [50, 20, 6, 12, 12, 15, 25, 8, 40, 40]

    # Header row
    header_font = Font(color=TEXT, size=10, bold=True)
    header_fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type="solid")
    thin_border = Border(
        bottom=Side(style="thin", color=BORDER_CLR)
    )

    for col, (header, width) in enumerate(zip(headers, widths), 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = thin_border
        ws.column_dimensions[get_column_letter(col)].width = width

    # Data rows
    data_font = Font(color=TEXT, size=10)
    muted_font = Font(color=TEXT_SEC, size=10)
    link_font = Font(color=COBALT, size=10, underline="single")
    row_fill = PatternFill(start_color=SURFACE, end_color=SURFACE, fill_type="solid")

    for i, row in enumerate(rows, 2):
        title, summary, url, source, tier, category, date, \
            countries, sectors, score, image_url = row

        ws.cell(row=i, column=1, value=title).font = data_font
        ws.cell(row=i, column=2, value=source).font = data_font
        tier_cell = ws.cell(row=i, column=3, value=f"T{tier}")
        tier_cell.font = TIER_FONTS.get(tier, data_font)
        ws.cell(row=i, column=4, value=category or "news").font = muted_font
        ws.cell(row=i, column=5, value=date or "").font = muted_font
        ws.cell(row=i, column=6, value=countries or "").font = data_font
        ws.cell(row=i, column=7, value=sectors or "").font = data_font
        ws.cell(row=i, column=8, value=score).font = data_font
        ws.cell(row=i, column=9, value=(summary or "")[:200]).font = muted_font

        url_cell = ws.cell(row=i, column=10, value=url)
        url_cell.font = link_font
        url_cell.hyperlink = url

        # Alternate row shading
        if i % 2 == 0:
            for col in range(1, 11):
                ws.cell(row=i, column=col).fill = row_fill

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:J{len(rows)+1}"

    # ──────────────────────────────────────────────────────
    # SHEET 2: By Source
    # ──────────────────────────────────────────────────────
    ws2 = wb.create_sheet("By Source")

    conn = sqlite3.connect(DB_PATH)
    source_stats = conn.execute("""
        SELECT source_label, source_tier, COUNT(*) as cnt,
               SUM(CASE WHEN countries != '' THEN 1 ELSE 0 END) as tagged
        FROM news_feed
        GROUP BY source_label, source_tier
        ORDER BY source_tier, cnt DESC
    """).fetchall()
    conn.close()

    src_headers = ["Source", "Tier", "Articles", "Country-Tagged", "Tag Rate"]
    src_widths = [30, 8, 12, 15, 12]

    for col, (header, width) in enumerate(zip(src_headers, src_widths), 1):
        cell = ws2.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        ws2.column_dimensions[get_column_letter(col)].width = width

    for i, (source, tier, cnt, tagged) in enumerate(source_stats, 2):
        ws2.cell(row=i, column=1, value=source).font = data_font
        tier_cell = ws2.cell(row=i, column=2, value=f"T{tier}")
        tier_cell.font = TIER_FONTS.get(tier, data_font)
        ws2.cell(row=i, column=3, value=cnt).font = data_font
        ws2.cell(row=i, column=4, value=tagged).font = data_font
        rate = f"{tagged/cnt*100:.0f}%" if cnt > 0 else "0%"
        ws2.cell(row=i, column=5, value=rate).font = muted_font

    ws2.freeze_panes = "A2"

    # ──────────────────────────────────────────────────────
    # SHEET 3: By Country
    # ──────────────────────────────────────────────────────
    ws3 = wb.create_sheet("By Country")

    conn = sqlite3.connect(DB_PATH)
    # Explode comma-separated countries
    all_articles = conn.execute(
        "SELECT countries FROM news_feed WHERE countries != ''"
    ).fetchall()
    conn.close()

    country_counts = {}
    for (countries,) in all_articles:
        for iso in countries.split(","):
            iso = iso.strip()
            if iso:
                country_counts[iso] = country_counts.get(iso, 0) + 1

    sorted_countries = sorted(country_counts.items(), key=lambda x: -x[1])

    ctry_headers = ["Country (ISO)", "Articles"]
    for col, header in enumerate(ctry_headers, 1):
        cell = ws3.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill

    ws3.column_dimensions["A"].width = 18
    ws3.column_dimensions["B"].width = 12

    for i, (iso, count) in enumerate(sorted_countries, 2):
        ws3.cell(row=i, column=1, value=iso).font = data_font
        ws3.cell(row=i, column=2, value=count).font = data_font

    ws3.freeze_panes = "A2"

    # ──────────────────────────────────────────────────────
    # SHEET 4: By Sector
    # ──────────────────────────────────────────────────────
    ws4 = wb.create_sheet("By Sector")

    conn = sqlite3.connect(DB_PATH)
    all_sectors = conn.execute(
        "SELECT sectors FROM news_feed WHERE sectors != ''"
    ).fetchall()
    conn.close()

    sector_counts = {}
    for (sectors,) in all_sectors:
        for s in sectors.split(","):
            s = s.strip()
            if s:
                sector_counts[s] = sector_counts.get(s, 0) + 1

    sorted_sectors = sorted(sector_counts.items(), key=lambda x: -x[1])

    sec_headers = ["Sector", "Articles"]
    for col, header in enumerate(sec_headers, 1):
        cell = ws4.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill

    ws4.column_dimensions["A"].width = 30
    ws4.column_dimensions["B"].width = 12

    for i, (sector, count) in enumerate(sorted_sectors, 2):
        ws4.cell(row=i, column=1, value=sector).font = data_font
        ws4.cell(row=i, column=2, value=count).font = data_font

    ws4.freeze_panes = "A2"

    # ── Save
    wb.save(output_path)
    return output_path, len(rows)


# ============================================================
# VERIFY
# ============================================================

if __name__ == "__main__":
    path, count = export_to_excel()
    print(f"Exported {count} articles to:")
    print(f"  {path}")
