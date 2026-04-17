# ============================================================
# NDC Investment Dashboard
# app.py — Application entry point
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import dash
import dash_bootstrap_components as dbc
from flask import jsonify

from layout    import create_layout
import callbacks

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

# Register country data endpoint for D3 globe
from pages.globe import get_country_data_json

@server.route("/country-data")
def country_data_endpoint():
    return jsonify(get_country_data_json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    print("\n" + "=" * 55)
    print("  NDC CLIMATE INTELLIGENCE DASHBOARD")
    print("=" * 55)
    print(f"  Local:   http://127.0.0.1:{port}")
    print("=" * 55 + "\n")
    app.run(debug=False, port=port, host="0.0.0.0")
