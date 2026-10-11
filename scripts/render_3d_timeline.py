#!/usr/bin/env python3
"""
Headless 3D extruded density maps of Jewish population in Europe, 1933–1945.

Uses Matplotlib 3D bars (ColumnLayer-style extrusion): height ∝ population,
color via continuous Blue → Cyan → Yellow → Orange → Dark Red ramp.
Exports high-resolution PNG frames and assembles MP4 + GIF animations.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "jewish_population_timeseries.csv"
FRAMES = ROOT / "outputs" / "frames"
ANIMS = ROOT / "outputs" / "animations"

# Prefer city + ghetto for residential density; hubs/camps shown as markers.
RESIDENTIAL = {"city", "ghetto"}
SITE_TYPES = {"deportation_hub", "extermination_site"}

# Europe map extent
LON_MIN, LON_MAX = -5.0, 35.0
LAT_MIN, LAT_MAX = 35.0, 60.0

DPI = 200
FIGSIZE = (16, 10)


def blue_to_red_cmap() -> mcolors.LinearSegmentedColormap:
    return mcolors.LinearSegmentedColormap.from_list(
        "blue_yellow_red",
        [
            (0.00, "#08306b"),  # deep blue — low
            (0.25, "#2171b5"),
            (0.45, "#41b6c4"),
            (0.60, "#fee391"),  # yellow — medium
            (0.75, "#fd8d3c"),  # orange
            (0.90, "#e31a1c"),
            (1.00, "#67000d"),  # dark red — extremely high
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


def render_year(
    rows: list[dict],
    year: int,
    vmax: float,
    cmap: mcolors.Colormap,
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

    fig = plt.figure(figsize=FIGSIZE, dpi=DPI, facecolor="#0b1020")
    ax = fig.add_subplot(111, projection="3d", facecolor="#0b1020")

    # Subtle ground plane
    gx = np.linspace(LON_MIN, LON_MAX, 2)
    gy = np.linspace(LAT_MIN, LAT_MAX, 2)
    GX, GY = np.meshgrid(gx, gy)
    ax.plot_surface(GX, GY, np.zeros_like(GX), color="#152038", alpha=0.55, linewidth=0)

    # Europe outline cues (simple bounding grid)
    for lon in range(int(LON_MIN), int(LON_MAX) + 1, 5):
        ax.plot(
            [lon, lon],
            [LAT_MIN, LAT_MAX],
            [0, 0],
            color="#2a3a55",
            linewidth=0.4,
            alpha=0.5,
        )
    for lat in range(int(LAT_MIN), int(LAT_MAX) + 1, 5):
        ax.plot(
            [LON_MIN, LON_MAX],
            [lat, lat],
            [0, 0],
            color="#2a3a55",
            linewidth=0.4,
            alpha=0.5,
        )

    if residential:
        xs = np.array([float(r["longitude"]) for r in residential])
        ys = np.array([float(r["latitude"]) for r in residential])
        pops = np.array([int(r["jewish_population"]) for r in residential], dtype=float)
        # Height scale: max bar ~ vmax mapped to ~0.55 of z-axis visual range
        heights = (pops / vmax) * 45.0
        heights = np.clip(heights, 0.4, None)
        colors = cmap(np.clip(pops / vmax, 0, 1))

        dx = 0.55
        dy = 0.35
        ax.bar3d(
            xs - dx / 2,
            ys - dy / 2,
            np.zeros_like(heights),
            dx,
            dy,
            heights,
            color=colors,
            shade=True,
            alpha=0.92,
            edgecolor="#111111",
            linewidth=0.15,
        )

        # Labels for largest communities
        order = np.argsort(pops)[::-1][:8]
        for i in order:
            ax.text(
                xs[i],
                ys[i],
                heights[i] + 1.2,
                residential[i]["name"],
                color="#e8eef8",
                fontsize=7,
                ha="center",
                va="bottom",
            )

    # Deportation / extermination markers (flat diamonds on ground)
    for r in sites:
        marker = "^" if r["place_type"] == "extermination_site" else "D"
        color = "#ff4d4d" if r["place_type"] == "extermination_site" else "#f0c040"
        ax.scatter(
            float(r["longitude"]),
            float(r["latitude"]),
            0.2,
            c=color,
            marker=marker,
            s=28,
            depthshade=False,
            alpha=0.95,
            edgecolors="#220000",
            linewidths=0.3,
        )

    ax.set_xlim(LON_MIN, LON_MAX)
    ax.set_ylim(LAT_MIN, LAT_MAX)
    ax.set_zlim(0, 50)
    ax.set_xlabel("Longitude", color="#9fb0c8", labelpad=8)
    ax.set_ylabel("Latitude", color="#9fb0c8", labelpad=8)
    ax.set_zlabel("Relative density", color="#9fb0c8", labelpad=8)
    ax.tick_params(colors="#8aa0bc", labelsize=7)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor("#2a3a55")
    ax.yaxis.pane.set_edgecolor("#2a3a55")
    ax.zaxis.pane.set_edgecolor("#2a3a55")
    ax.grid(False)
    ax.view_init(elev=28, azim=-70)

    total = sum(int(r["jewish_population"]) for r in residential)
    fig.suptitle(
        f"Jewish Population Density in Europe — {year}",
        color="#f2f6ff",
        fontsize=18,
        fontweight="bold",
        y=0.96,
    )
    ax.text2D(
        0.02,
        0.02,
        f"Mapped residential total (cities + ghettos): {total:,.0f}\n"
        "Height ∝ local Jewish population  |  Blue→Red = low→extreme density\n"
        "△ extermination site   ◆ deportation / transit hub\n"
        "Estimates for visualization; see data/raw/SOURCES.txt",
        transform=ax.transAxes,
        color="#a8b8d0",
        fontsize=7,
        va="bottom",
    )

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=0, vmax=vmax))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.45, pad=0.08)
    cbar.set_label("Jewish population (local)", color="#cfd8e6")
    cbar.ax.yaxis.set_tick_params(color="#cfd8e6")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#cfd8e6")

    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


def assemble_animations(frame_paths: list[Path]) -> None:
    ANIMS.mkdir(parents=True, exist_ok=True)
    images = [Image.open(p).convert("RGB") for p in frame_paths]
    # Normalize sizes (even dims required by libx264 / yuv420p)
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
    # Hold each year ~0.9s
    normalized[0].save(
        gif_path,
        save_all=True,
        append_images=normalized[1:],
        duration=900,
        loop=0,
        optimize=False,
    )
    print(f"Wrote {gif_path}")

    # MP4 via imageio-ffmpeg if available, else ffmpeg CLI
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
    FRAMES.mkdir(parents=True, exist_ok=True)

    frame_paths: list[Path] = []
    for year in years_present(rows):
        out = FRAMES / f"density_3d_{year}.png"
        render_year(rows, year, vmax, cmap, out)
        frame_paths.append(out)

    assemble_animations(frame_paths)
    print("Done.")


if __name__ == "__main__":
    main()
