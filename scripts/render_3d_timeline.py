#!/usr/bin/env python3
"""
Headless 3D-style extruded density maps of Jewish population in Europe, 1933–1945.

Europe basemap (Natural Earth land polygons) is drawn first; isometric column bars
are drawn on top with higher zorder. Height ∝ population; color Blue → Red.
Exports high-resolution PNG frames and assembles MP4 + GIF animations.
"""

from __future__ import annotations

import csv
import json
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "jewish_population_timeseries.csv"
CACHE = ROOT / "data" / "cache"
NE_COUNTRIES = CACHE / "ne_110m_admin_0_countries.geojson"
NE_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
    "master/geojson/ne_110m_admin_0_countries.geojson"
)
FRAMES = ROOT / "outputs" / "frames"
ANIMS = ROOT / "outputs" / "animations"

RESIDENTIAL = {"city", "ghetto"}
SITE_TYPES = {"deportation_hub", "extermination_site"}

LON_MIN, LON_MAX = -5.0, 35.0
LAT_MIN, LAT_MAX = 35.0, 60.0

DPI = 200
FIGSIZE = (16, 10)

SKEW_X = 0.55
BAR_W = 0.42
BAR_D = 0.28
MAX_H = 8.5

LAND_FACE = "#4a678f"
LAND_EDGE = "#c5d6ee"
OCEAN = "#0b1020"


def blue_to_red_cmap() -> mcolors.LinearSegmentedColormap:
    return mcolors.LinearSegmentedColormap.from_list(
        "blue_yellow_red",
        [
            (0.00, "#08306b"),
            (0.25, "#2171b5"),
            (0.45, "#41b6c4"),
            (0.60, "#fee391"),
            (0.75, "#fd8d3c"),
            (0.90, "#e31a1c"),
            (1.00, "#67000d"),
        ],
    )


def load_rows() -> list[dict]:
    with DATA.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def years_present(rows: list[dict]) -> list[int]:
    return sorted({int(r["year"]) for r in rows})


def max_population(rows: list[dict]) -> float:
    vals = [
        int(r["jewish_population"])
        for r in rows
        if r["place_type"] in RESIDENTIAL and int(r["jewish_population"]) > 0
    ]
    return float(max(vals) if vals else 1)


def ensure_natural_earth() -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    if not NE_COUNTRIES.exists():
        urllib.request.urlretrieve(NE_URL, NE_COUNTRIES)
    return NE_COUNTRIES


def _rings_to_patches(rings) -> list[mpatches.Polygon]:
    """GeoJSON polygon exterior ring → matplotlib patch (lon/lat)."""
    if not rings:
        return []
    exterior = [(float(x), float(y)) for x, y, *_ in rings[0]]
    if len(exterior) < 3:
        return []
    return [
        mpatches.Polygon(
            exterior,
            closed=True,
            facecolor=LAND_FACE,
            edgecolor=LAND_EDGE,
            linewidth=0.45,
        )
    ]


def load_europe_land_patches() -> list[mpatches.Polygon]:
    ensure_natural_earth()
    with NE_COUNTRIES.open(encoding="utf-8") as f:
        geo = json.load(f)
    patches: list[mpatches.Polygon] = []
    for feat in geo["features"]:
        geom = feat.get("geometry") or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates")
        if not coords:
            continue
        if gtype == "Polygon":
            patches.extend(_rings_to_patches(coords))
        elif gtype == "MultiPolygon":
            for poly in coords:
                patches.extend(_rings_to_patches(poly))
    return patches


def _shade(rgba, factor: float) -> tuple:
    r, g, b, a = rgba
    return (r * factor, g * factor, b * factor, a)


def _iso_point(lon: float, lat: float, h: float) -> tuple[float, float]:
    return lon + h * SKEW_X, lat + h


def _bar_faces(lon: float, lat: float, h: float, rgba) -> list[tuple[float, mpatches.Polygon]]:
    w, d = BAR_W, BAR_D
    sw, se, ne, nw = (lon - w, lat - d), (lon + w, lat - d), (lon + w, lat + d), (lon - w, lat + d)

    def lift(p, hh):
        return _iso_point(p[0], p[1], hh)

    b_sw, b_se, b_ne, b_nw = lift(sw, 0), lift(se, 0), lift(ne, 0), lift(nw, 0)
    t_sw, t_se, t_ne, t_nw = lift(sw, h), lift(se, h), lift(ne, h), lift(nw, h)
    depth = lat - 0.35 * lon
    return [
        (
            depth - 0.02,
            mpatches.Polygon(
                [b_se, b_ne, t_ne, t_se],
                closed=True,
                facecolor=_shade(rgba, 0.55),
                edgecolor="#0a0a12",
                linewidth=0.25,
            ),
        ),
        (
            depth - 0.01,
            mpatches.Polygon(
                [b_sw, b_se, t_se, t_sw],
                closed=True,
                facecolor=_shade(rgba, 0.72),
                edgecolor="#0a0a12",
                linewidth=0.25,
            ),
        ),
        (
            depth + h,
            mpatches.Polygon(
                [t_sw, t_se, t_ne, t_nw],
                closed=True,
                facecolor=rgba,
                edgecolor="#0a0a12",
                linewidth=0.3,
            ),
        ),
    ]


def render_year(
    rows: list[dict],
    year: int,
    vmax: float,
    cmap: mcolors.Colormap,
    land_patches: list[mpatches.Polygon],
    out_path: Path,
) -> None:
    residential = [
        r
        for r in rows
        if int(r["year"]) == year
        and r["place_type"] in RESIDENTIAL
        and int(r["jewish_population"]) > 0
        and LON_MIN <= float(r["longitude"]) <= LON_MAX
        and LAT_MIN <= float(r["latitude"]) <= LAT_MAX
    ]
    sites = [
        r
        for r in rows
        if int(r["year"]) == year
        and r["place_type"] in SITE_TYPES
        and LON_MIN <= float(r["longitude"]) <= LON_MAX
        and LAT_MIN <= float(r["latitude"]) <= LAT_MAX
    ]

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI, facecolor=OCEAN)
    ax.set_facecolor(OCEAN)

    # Ocean rectangle + land (zorder below bars). PatchCollection shares one zorder.
    ocean = mpatches.Rectangle(
        (LON_MIN - 2, LAT_MIN - 2),
        (LON_MAX - LON_MIN) + 6,
        (LAT_MAX - LAT_MIN) + MAX_H + 4,
        facecolor=OCEAN,
        edgecolor="none",
        zorder=0,
    )
    ax.add_patch(ocean)

    land_coll = PatchCollection(
        land_patches,
        match_original=True,
        zorder=1,
    )
    ax.add_collection(land_coll)

    # Lon/lat grid on the map
    for lon in range(int(LON_MIN), int(LON_MAX) + 1, 5):
        ax.plot(
            [lon, lon],
            [LAT_MIN, LAT_MAX],
            color="#2f4060",
            linewidth=0.5,
            zorder=2,
            solid_capstyle="butt",
        )
    for lat in range(int(LAT_MIN), int(LAT_MAX) + 1, 5):
        ax.plot(
            [LON_MIN, LON_MAX],
            [lat, lat],
            color="#2f4060",
            linewidth=0.5,
            zorder=2,
            solid_capstyle="butt",
        )

    ax.set_xlim(LON_MIN - 1.5, LON_MAX + 2.5)
    ax.set_ylim(LAT_MIN - 1.0, LAT_MAX + MAX_H + 1.5)

    face_items: list[tuple[float, mpatches.Polygon]] = []
    labels: list[tuple] = []

    if residential:
        pops = np.array([int(r["jewish_population"]) for r in residential], dtype=float)
        heights = np.clip((pops / vmax) * MAX_H, 0.25, None)
        colors = cmap(np.clip(pops / vmax, 0, 1))

        for r, h, rgba in zip(residential, heights, colors):
            lon = float(r["longitude"])
            lat = float(r["latitude"])
            face_items.extend(_bar_faces(lon, lat, float(h), tuple(rgba)))

        order = np.argsort(pops)[::-1][:8]
        for i in order:
            lon = float(residential[i]["longitude"])
            lat = float(residential[i]["latitude"])
            h = float(heights[i])
            tx, ty = _iso_point(lon, lat, h + 0.25)
            labels.append((tx, ty, residential[i]["name"], lat - 0.35 * lon + h))

    face_items.sort(key=lambda t: t[0])
    for _, poly in face_items:
        poly.set_zorder(10)
        ax.add_patch(poly)

    for r in sites:
        lon = float(r["longitude"])
        lat = float(r["latitude"])
        marker = "^" if r["place_type"] == "extermination_site" else "D"
        color = "#ff4d4d" if r["place_type"] == "extermination_site" else "#f0c040"
        ax.scatter(
            [lon],
            [lat],
            c=color,
            marker=marker,
            s=36,
            zorder=8,
            edgecolors="#220000",
            linewidths=0.4,
        )

    labels.sort(key=lambda t: t[3])
    for tx, ty, name, _ in labels:
        ax.text(
            tx,
            ty,
            name,
            color="#f2f6ff",
            fontsize=8,
            ha="center",
            va="bottom",
            zorder=20,
        )

    total = sum(int(r["jewish_population"]) for r in residential)
    ax.set_xlabel("Longitude", color="#9fb0c8")
    ax.set_ylabel("Latitude (+ bar height)", color="#9fb0c8")
    ax.tick_params(colors="#8aa0bc", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#2a3a55")

    fig.suptitle(
        f"Jewish Population Density in Europe — {year}",
        color="#f2f6ff",
        fontsize=18,
        fontweight="bold",
        y=0.98,
    )
    ax.text(
        0.01,
        0.02,
        f"Mapped residential total (cities + ghettos): {total:,.0f}\n"
        "Height ∝ local Jewish population  |  Blue→Red = low→extreme density\n"
        "△ extermination site   ◆ deportation / transit hub\n"
        "Estimates for visualization; see data/raw/SOURCES.txt",
        transform=ax.transAxes,
        color="#a8b8d0",
        fontsize=7,
        va="bottom",
        zorder=30,
    )

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=0, vmax=vmax))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.02)
    cbar.set_label("Jewish population (local)", color="#cfd8e6")
    cbar.ax.yaxis.set_tick_params(color="#cfd8e6")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#cfd8e6")

    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


def assemble_animations(frame_paths: list[Path]) -> None:
    ANIMS.mkdir(parents=True, exist_ok=True)
    images = [Image.open(p).convert("RGB") for p in frame_paths]
    w = max(im.width for im in images)
    h = max(im.height for im in images)
    if w % 2:
        w += 1
    if h % 2:
        h += 1
    normalized = []
    for im in images:
        canvas = Image.new("RGB", (w, h), (11, 16, 32))
        canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
        normalized.append(canvas)

    gif_path = ANIMS / "jewish_population_1933_1945.gif"
    normalized[0].save(
        gif_path,
        save_all=True,
        append_images=normalized[1:],
        duration=900,
        loop=0,
        optimize=False,
    )
    print(f"Wrote {gif_path}")

    mp4_path = ANIMS / "jewish_population_1933_1945.mp4"
    try:
        import imageio.v2 as imageio

        writer = imageio.get_writer(
            mp4_path,
            fps=1.2,
            codec="libx264",
            quality=8,
            pixelformat="yuv420p",
            macro_block_size=1,
        )
        for im in normalized:
            writer.append_data(np.asarray(im))
        writer.close()
        print(f"Wrote {mp4_path}")
    except Exception as exc:
        print(f"imageio MP4 failed ({exc}); trying ffmpeg CLI")
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for i, im in enumerate(normalized):
                im.save(tmp_path / f"frame_{i:03d}.png")
            cmd = [
                "ffmpeg",
                "-y",
                "-framerate",
                "1.2",
                "-i",
                str(tmp_path / "frame_%03d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(mp4_path),
            ]
            subprocess.run(cmd, check=True)
            print(f"Wrote {mp4_path}")


def main() -> None:
    rows = load_rows()
    cmap = blue_to_red_cmap()
    vmax = max_population(rows)
    land_patches = load_europe_land_patches()
    FRAMES.mkdir(parents=True, exist_ok=True)

    frame_paths: list[Path] = []
    for year in years_present(rows):
        out = FRAMES / f"density_3d_{year}.png"
        render_year(rows, year, vmax, cmap, land_patches, out)
        frame_paths.append(out)

    assemble_animations(frame_paths)
    print("Done.")


if __name__ == "__main__":
    main()
