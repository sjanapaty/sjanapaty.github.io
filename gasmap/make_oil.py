"""
Deep-time animation: where the world's crude oil was born.

A clock runs from 460 Ma to the present over reconstructed continents. Each
petroleum province appears as a circle when its source rock was deposited and
then drifts with its plate to the modern position. Circle area is known oil in
billion barrels; colour is the source-rock interval, oldest darkest.

The bar along the bottom is the legend: each interval's age range is drawn in
its own colour, muted until the clock reaches it.

Inputs
  basins_oil.csv        province code, known oil (billion bbl), interval fractions
  usgs/WEP_PRVG.SHP     USGS world geologic provinces, all defined provinces
  merdith2021           plate model, fetched and cached by plate_model_manager

Outputs (in out_oil/)
  frames/f####.png
  oil_history.mp4 / .gif
  interval_<key>.png    a still at each interval's deposition moment

Usage
  python make_oil.py --stills
  python make_oil.py --step 4
"""
import argparse
import subprocess
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

import gplately
from plate_model_manager import PlateModelManager

# key, label, deposition age drawn, (range start Ma, range end Ma), colour, bar label
INTERVALS = [
    ("silurian",       "Silurian",                       430, (444, 419), "#8c2d04", "Silurian"),
    ("devonian",       "Upper Devonian - Mississippian", 360, (383, 330), "#cc4c02", "Upper Devonian\nMississippian"),
    ("penn_permian",   "Pennsylvanian - Lower Permian",  300, (323, 273), "#ec7014", "Pennsylvanian\nLower Permian"),
    ("upper_jurassic", "Upper Jurassic",                 152, (164, 140), "#fe9929", "Upper\nJurassic"),
    ("mid_cretaceous", "Middle Cretaceous",              100, (130, 85),  "#fec44f", "Middle\nCretaceous"),
    ("oligo_miocene",  "Oligocene - Miocene",             20, (34, 5),    "#fee391", "Oligocene\nMiocene"),
]
KEYS = [k for k, *_ in INTERVALS]
COLOR = {k: c for k, _, _, _, c, _ in INTERVALS}
DEP_AGE = {k: a for k, _, a, _, _, _ in INTERVALS}

SURFACE, OCEAN, LAND, SHELF = "#fcfcfb", "#eef1f4", "#dedcd3", "#e8e6de"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
BAR_BG = "#eceae3"

# Figure geometry. export_hotspots.py duplicates FIGSIZE and the marker formula,
# so any change here needs the same change there or the clickable circles in the
# web version drift off the drawn ones.
FIGSIZE = (12.5, 7.4)
DPI = 200          # 2500 x 1480, enough that the bar labels stay crisp

MARKER_MIN, MARKER_MAX = 10.0, 900.0
REF = 350.0        # billion barrels mapping to the largest marker
MIN_DRAW = 0.05
FADE_MYR = 25.0
T_START = 460


def load_model(data_dir: Path):
    m = PlateModelManager().get_model("merdith2021", data_dir=str(data_dir))
    recon = gplately.PlateReconstruction(
        m.get_rotation_model(), m.get_layer("Topologies"), m.get_layer("StaticPolygons"))
    plot = gplately.PlotTopologies(
        recon, coastlines=m.get_layer("Coastlines"),
        continents=m.get_layer("ContinentalPolygons"), time=0)
    return recon, plot


def load_basins(csv: Path, prov_shp: Path):
    b = pd.read_csv(csv)
    s = b[KEYS + ["other"]].sum(axis=1)
    bad = b[(s - 1).abs() > 0.005]
    if len(bad):
        raise SystemExit(f"fractions do not sum to 1:\n{bad[['code','name']]}")

    prov = gpd.read_file(prov_shp)[["CODE", "NAME", "geometry"]]
    prov["CODE"] = prov.CODE.astype(int)
    prov = prov.assign(_a=prov.to_crs("ESRI:54030").geometry.area) \
               .sort_values("_a", ascending=False).drop_duplicates("CODE").drop(columns="_a")

    m = b.merge(prov, left_on="code", right_on="CODE", how="left")
    miss = m[m.geometry.isna()]
    if len(miss):
        print("no polygon for:", ", ".join(miss.name))
    m = m[m.geometry.notna()].copy()
    g = gpd.GeoDataFrame(m, geometry="geometry", crs=prov.crs)
    pt = g.geometry.representative_point()
    g["lon"], g["lat"] = pt.x.values, pt.y.values
    df = pd.DataFrame(g.drop(columns=["geometry"]))
    print(f"{len(df)} provinces, {df.vol.sum():,.0f} billion barrels")
    return df


def precompute(recon, df, times):
    pts = gplately.Points(recon, df.lon.values, df.lat.values)
    return {t: tuple(np.asarray(v) for v in pts.reconstruct(float(t), return_array=True))
            for t in times}


def draw_bar(ax, t):
    """Timeline doubling as the legend: each interval in its own map colour."""
    ax.set_xlim(T_START, 0)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.axhspan(0.42, 0.80, color=BAR_BG, lw=0)

    for key, lab, dep, (a, b), c, short in INTERVALS:
        reached = t <= dep
        ax.axvspan(a, b, 0.42, 0.80, color=c, lw=0, alpha=1.0 if reached else 0.30)
        ax.text((a + b) / 2, 0.30, short, ha="center", va="top", linespacing=1.25,
                fontsize=9.5, color=INK if reached else MUTED,
                fontweight="bold" if reached else "normal")

    for age in (450, 400, 350, 300, 250, 200, 150, 100, 50, 0):
        if abs(age - t) < 20:      # keep clear of the moving time readout
            continue
        ax.text(age, 0.86, f"{age}", ha="center", va="bottom", fontsize=8, color=MUTED)

    ax.axvline(t, 0.36, 0.86, color=INK, lw=1.8)
    ha = "left" if t > 435 else ("right" if t < 25 else "center")
    ax.text(t, 0.94, f"{t:,.0f} Ma", ha=ha, va="bottom", fontsize=12,
            color=INK, fontweight="bold")


def frame(fig, gs, plot, df, pos, t):
    fig.clear()
    ax = fig.add_subplot(gs[0], projection=PROJ)
    ax.set_global()
    ax.patch.set_facecolor(OCEAN)

    # Set the model's time BEFORE drawing, or the continents stay at present day.
    plot.time = float(t)
    try:
        plot.plot_continents(ax, facecolor=SHELF, edgecolor="none", zorder=1)
        plot.plot_coastlines(ax, facecolor=LAND, edgecolor="none", zorder=2)
    except Exception as e:
        print(f"  [warn] {t} Ma coastlines: {type(e).__name__}")

    lo, la = pos[t]
    total = 0.0
    for key, lab, dep, _, c, _short in INTERVALS:
        if t > dep:
            continue
        vals = df[key].values * df.vol.values
        sel = vals > MIN_DRAW
        if not sel.any():
            continue
        size = MARKER_MIN + (MARKER_MAX - MARKER_MIN) * np.sqrt(np.clip(vals[sel] / REF, 0, 1))
        since = dep - t
        ax.scatter(lo[sel], la[sel], s=size, facecolor=c, edgecolor=INK,
                   linewidth=0.7, alpha=0.60 + 0.35 * min(since / FADE_MYR, 1.0),
                   zorder=5, transform=CRS_PLATE)
        total += vals[sel].sum()

    # The running total and the source note used to sit here. Both now live in
    # the surrounding web page instead, so the frame stays clean.
    draw_bar(fig.add_subplot(gs[1]), t)


def main():
    ap = argparse.ArgumentParser()
    here = Path(__file__).parent
    ap.add_argument("--basins", type=Path, default=here / "basins_oil.csv")
    ap.add_argument("--provinces", type=Path, default=here / "usgs" / "WEP_PRVG.SHP")
    ap.add_argument("--model-dir", type=Path, default=here / "pmm_data")
    ap.add_argument("--out", type=Path, default=here / "out_oil")
    ap.add_argument("--step", type=float, default=4)
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--hold", type=int, default=18)
    ap.add_argument("--gif-loops", type=int, default=-1,
                    help="GIF looping: -1 plays once and rests on the modern map, "
                         "0 loops forever, n repeats n times")
    ap.add_argument("--dpi", type=int, default=DPI,
                    help="frame resolution; the figure is 12.5 x 7.4 in, so 200 gives 2500 x 1480")
    ap.add_argument("--gif-width", type=int, default=1100,
                    help="GIF width in pixels; the MP4 keeps the full frame resolution")
    ap.add_argument("--stills", action="store_true")
    a = ap.parse_args()

    global PROJ, CRS_PLATE
    import cartopy.crs as ccrs
    PROJ, CRS_PLATE = ccrs.Robinson(central_longitude=0), ccrs.PlateCarree()

    a.out.mkdir(parents=True, exist_ok=True)
    recon, plot = load_model(a.model_dir)
    df = load_basins(a.basins, a.provinces)
    for k, lab, *_rest in INTERVALS:
        print(f"  {lab:32s} {(df[k]*df.vol).sum():8,.0f} bn bbl")
    print(f"  {'other / unattributed':32s} {(df['other']*df.vol).sum():8,.0f} bn bbl")

    fig = plt.figure(figsize=FIGSIZE, facecolor=SURFACE)
    gs = GridSpec(2, 1, height_ratios=[10, 1.5], figure=fig,
                  left=0.015, right=0.985, top=0.985, bottom=0.045, hspace=0.16)

    times = (sorted({DEP_AGE[k] for k in KEYS} | {0}) if a.stills
             else [round(float(x), 3) for x in np.arange(T_START, -0.001, -a.step)])
    print(f"reconstructing {len(times)} frame positions ...")
    pos = precompute(recon, df, times)

    if a.stills:
        for t in sorted(times, reverse=True):
            frame(fig, gs, plot, df, pos, t)
            name = next((k for k in KEYS if DEP_AGE[k] == t), "present")
            fig.savefig(a.out / f"interval_{name}.png", dpi=a.dpi, facecolor=SURFACE)
            print("  still", name)
        return

    fdir = a.out / "frames"
    fdir.mkdir(exist_ok=True)
    for i, t in enumerate(times):
        frame(fig, gs, plot, df, pos, t)
        fig.savefig(fdir / f"f{i:04d}.png", dpi=a.dpi, facecolor=SURFACE)
        if i % 10 == 0:
            print(f"  frame {i}/{len(times)}  {t} Ma")
    for j in range(a.hold):
        (fdir / f"f{len(times)+j:04d}.png").write_bytes(
            (fdir / f"f{len(times)-1:04d}.png").read_bytes())

    mp4, gif, pal = a.out / "oil_history.mp4", a.out / "oil_history.gif", a.out / "_pal.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps),
                    "-i", str(fdir / "f%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", str(mp4)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4),
                    "-vf", f"fps=10,scale={a.gif_width}:-1:flags=lanczos,palettegen", str(pal)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-i", str(pal),
                    "-lavfi", f"fps=10,scale={a.gif_width}:-1:flags=lanczos[x];[x][1:v]paletteuse",
                    "-loop", str(a.gif_loops), str(gif)], check=True)
    pal.unlink(missing_ok=True)
    print("wrote", mp4, "and", gif)


if __name__ == "__main__":
    main()
