# Jewish Population Timeline in Europe (1933–1945)

Historically informed, geocoded time-series of Jewish populations at city, ghetto, deportation-hub, and extermination-site locations across Europe, with headless 3D density visualizations and a year-by-year time-lapse.

> Estimates are for spatial visualization and education. They are rounded secondary aggregates (USHMM, Yad Vashem, community tallies, ghetto registries) — not archival microdata. See `data/raw/SOURCES.txt`.

## Contents

| Path | Description |
|------|-------------|
| `data/raw/places_catalog.csv` | Place registry with WGS84 coordinates |
| `data/raw/SOURCES.txt` | Source classes and methodology notes |
| `data/processed/jewish_population_timeseries.csv` | Long-form yearly populations |
| `data/processed/jewish_population_by_place.geojson` | Wide GeoJSON (`population_by_year`) |
| `data/processed/jewish_population_long.geojson` | Long GeoJSON (one feature per place-year > 0) |
| `data/processed/jewish_density_grid.csv` | Coarse density grid for extrusion |
| `scripts/build_dataset.py` | Rebuild CSV/GeoJSON from curated series |
| `scripts/render_3d_timeline.py` | Matplotlib 3D ColumnLayer-style frames + MP4/GIF |
| `scripts/export_pydeck_html.py` | PyDeck ColumnLayer HTML (or data payload stub) |
| `outputs/frames/` | High-resolution PNG per milestone year |
| `outputs/animations/` | Time-lapse MP4 and GIF |

## Color & extrusion

- **Height** ∝ local Jewish population (cities + ghettos)
- **Color** continuous Blue → Yellow/Orange → Dark Red (low → extreme density)
- Deportation hubs (◆) and extermination sites (△) marked on the ground plane

## Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_dataset.py
python scripts/render_3d_timeline.py
python scripts/export_pydeck_html.py
```

Requires `ffmpeg` on PATH for MP4 (or `imageio-ffmpeg`).

## Milestone years

1933, 1935, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945

Covered communities include Warsaw, Łódź, Berlin, Vienna, Budapest, Kiev, Thessaloniki, Amsterdam, Paris, Kraków, Lwów/Lviv, Vilnius, and others, plus major ghettos, transit camps, and killing centers.
