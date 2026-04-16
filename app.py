# ============================================================
# NDC Investment Dashboard
# app.py — Application entry point
# Run with: python app.py
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dash
import dash_bootstrap_components as dbc

from layout    import create_layout
import callbacks  # registers all callbacks

# ============================================================
# INITIALISE APP
# ============================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Inter:"
        "wght@300;400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions = True,
    title                        = "NDC Climate Intelligence",
    update_title                 = None,
)

app.layout = create_layout()
server     = app.server

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))

    print("\n" + "=" * 55)
    print("  NDC CLIMATE INTELLIGENCE DASHBOARD")
    print("=" * 55)
    print(f"  Local:   http://127.0.0.1:{port}")
    print(f"  Network: http://0.0.0.0:{port}")
    print("=" * 55)
    print("  Press Control+C to stop\n")

    app.run(
        debug = False,
        port  = port,
        host  = "0.0.0.0"
    )