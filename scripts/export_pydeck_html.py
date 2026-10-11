#!/usr/bin/env python3
"""
Optional PyDeck ColumnLayer HTML export (no browser required to generate file).
Falls back gracefully if pydeck is not installed.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "jewish_population_timeseries.csv"
OUT = ROOT / "outputs" / "pydeck_columnlayer_timeline.html"


def main() -> None:
    try:
        import pydeck as pdk
    except ImportError:
        # Emit a lightweight self-contained HTML stub documenting the layer spec
        # so the repo still contains a ColumnLayer-oriented artifact.
        with DATA.open(encoding="utf-8") as f:
            rows = [
                r
                for r in csv.DictReader(f)
                if r["place_type"] in {"city", "ghetto"}
                and int(r["jewish_population"]) > 0
            ]
        payload = {
            "description": "PyDeck ColumnLayer data payload (pydeck not installed at build time)",
            "layer": "ColumnLayer",
            "color_ramp": "Blue (low) → Yellow/Orange (medium) → Dark Red (extreme)",
            "elevation_scale": 0.08,
            "rows": rows,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Jewish Population ColumnLayer Timeline (1933–1945)</title>
  <style>
    body {{ margin: 0; font-family: Georgia, serif; background: #0b1020; color: #e8eef8; }}
    header {{ padding: 1.2rem 1.5rem; border-bottom: 1px solid #2a3a55; }}
    main {{ padding: 1.5rem; max-width: 960px; }}
    code {{ color: #9fd3ff; }}
    pre {{ background: #152038; padding: 1rem; overflow: auto; border-radius: 6px; }}
  </style>
</head>
<body>
  <header>
    <h1>Jewish Population — PyDeck ColumnLayer Spec</h1>
    <p>Blue→Red density ramp · elevation ∝ local Jewish population · 1933–1945</p>
  </header>
  <main>
    <p>Install <code>pydeck</code> and re-run <code>scripts/export_pydeck_html.py</code>
    for an interactive map. Data payload (truncated in page source as JSON):</p>
    <pre id="data"></pre>
  </main>
  <script>
    const data = {json.dumps(payload, ensure_ascii=False)};
    document.getElementById('data').textContent = JSON.stringify({{
      layer: data.layer,
      color_ramp: data.color_ramp,
      elevation_scale: data.elevation_scale,
      n_rows: data.rows.length,
      sample: data.rows.slice(0, 5)
    }}, null, 2);
    window.JEWISH_POP_COLUMNLAYER = data;
  </script>
</body>
</html>
"""
        OUT.write_text(html, encoding="utf-8")
        print(f"Wrote fallback HTML (pydeck missing): {OUT}")
        return

    with DATA.open(encoding="utf-8") as f:
        rows = [
            {
                **r,
                "jewish_population": int(r["jewish_population"]),
                "latitude": float(r["latitude"]),
                "longitude": float(r["longitude"]),
                "year": int(r["year"]),
            }
            for r in csv.DictReader(f)
            if r["place_type"] in {"city", "ghetto"}
            and int(r["jewish_population"]) > 0
        ]

    # Use 1939 as default view year in the HTML; full series embedded.
    view_year = 1939
    data = [r for r in rows if r["year"] == view_year]

    def color(pop: int) -> list[int]:
        # Approximate blue→red
        t = min(1.0, pop / 380000)
        if t < 0.5:
            # blue to yellow
            u = t / 0.5
            return [int(8 + u * (254 - 8)), int(48 + u * (227 - 48)), int(107 + u * (145 - 107)), 200]
        u = (t - 0.5) / 0.5
        return [int(254 - u * (254 - 103)), int(227 - u * (227 - 0)), int(145 - u * 145), 220]

    for r in data:
        r["color"] = color(r["jewish_population"])
        r["elevation"] = r["jewish_population"]

    layer = pdk.Layer(
        "ColumnLayer",
        data=data,
        get_position=["longitude", "latitude"],
        get_elevation="elevation",
        elevation_scale=0.08,
        radius=18000,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )
    view = pdk.ViewState(latitude=50.5, longitude=15.0, zoom=3.5, pitch=45, bearing=-20)
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        map_style=None,
        tooltip={"text": "{name}\n{jewish_population} ({year})"},
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    deck.to_html(str(OUT), offline=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
