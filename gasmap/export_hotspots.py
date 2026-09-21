"""
Export clickable hotspots for the interactive version of the oil animation.

For every province holding more than a threshold volume, this works out where
its circle lands in the final (present-day) frame of the animation, as a
fraction of the image, and bundles that with the facts the detail panel shows:
country, nearest city, discovery year, major fields, and recoverable oil split
into what has already been produced and what remains.

The geometry here must match make_oil.py exactly, or the overlay will not sit on
top of the drawn circles. Figure size, dpi, projection and the marker size
formula are all duplicated from that script on purpose.

Inputs
  basins_oil.csv        volumes and interval fractions
  province_fields.csv   discovery year and major field names, hand-mapped
  usgs/WEP_PRVG.SHP     province polygons, and CUM_OIL / REM_OIL per province
  ne50/                 Natural Earth countries and populated places
  merdith2021           plate model (only to confirm present-day positions)

Output
  ../assets/data/oil_hotspots.json

Usage
  python export_hotspots.py
"""
import argparse
import json
import math
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

# --- kept identical to make_oil.py ---------------------------------------
INTERVALS = [
    ("silurian",       "Silurian",                       430, "#8c2d04"),
    ("devonian",       "Upper Devonian - Mississippian", 360, "#cc4c02"),
    ("penn_permian",   "Pennsylvanian - Lower Permian",  300, "#ec7014"),
    ("upper_jurassic", "Upper Jurassic",                 152, "#fe9929"),
    ("mid_cretaceous", "Middle Cretaceous",              100, "#fec44f"),
    ("oligo_miocene",  "Oligocene - Miocene",             20, "#fee391"),
]
KEYS = [k for k, *_ in INTERVALS]
LABEL = {k: l for k, l, _, _ in INTERVALS}
COLOR = {k: c for k, _, _, c in INTERVALS}
MARKER_MIN, MARKER_MAX = 10.0, 900.0
REF = 350.0
FIGSIZE = (12.5, 7.4)
DPI = 200
GRID = dict(height_ratios=[10, 1.5], left=0.015, right=0.985,
            top=0.985, bottom=0.045, hspace=0.16)
# -------------------------------------------------------------------------

MIN_VOL = 1.0     # billion barrels; below this a province is not clickable
MIN_HIT_PX = 9.0  # minimum click radius so tiny circles stay reachable


def nearest_city(lon, lat, cities):
    """Great-circle nearest populated place, preferring larger ones."""
    dlon = np.radians(cities.lon.values - lon)
    la1, la2 = math.radians(lat), np.radians(cities.lat.values)
    d = np.arccos(np.clip(np.sin(la1) * np.sin(la2) +
                          np.cos(la1) * np.cos(la2) * np.cos(dlon), -1, 1)) * 6371.0
    # a big city slightly further away reads better than a hamlet next door
    score = d / np.clip(np.log10(np.maximum(cities.popmax.values, 1000)) - 2.0, 0.35, 5.0)
    i = int(np.argmin(score))
    return cities.name.values[i], cities.country.values[i], round(float(d[i]))


def main():
    ap = argparse.ArgumentParser()
    here = Path(__file__).parent
    ap.add_argument("--basins", type=Path, default=here / "basins_oil.csv")
    ap.add_argument("--fields", type=Path, default=here / "province_fields.csv")
    ap.add_argument("--provinces", type=Path, default=here / "usgs" / "WEP_PRVG.SHP")
    ap.add_argument("--ne", type=Path, default=here / "ne50")
    ap.add_argument("--out", type=Path,
                    default=here.parent / "assets" / "data" / "oil_hotspots.json")
    a = ap.parse_args()

    import cartopy.crs as ccrs
    PROJ, PLATE = ccrs.Robinson(central_longitude=0), ccrs.PlateCarree()

    basins = pd.read_csv(a.basins)
    fields = pd.read_csv(a.fields)

    prov = gpd.read_file(a.provinces)
    prov["CODE"] = prov.CODE.astype(int)
    for c in ("CUM_OIL", "REM_OIL"):
        prov[c] = pd.to_numeric(prov[c], errors="coerce").clip(lower=0)
    prov = prov.assign(_a=prov.to_crs("ESRI:54030").geometry.area) \
               .sort_values("_a", ascending=False).drop_duplicates("CODE")

    countries = gpd.read_file(a.ne / "ne_50m_admin_0_countries.shp")[["ADMIN", "geometry"]]
    cities_raw = gpd.read_file(a.ne / "ne_50m_populated_places.shp")
    cities = pd.DataFrame({
        "name": cities_raw.NAME.values,
        "country": cities_raw.ADM0NAME.values,
        "popmax": pd.to_numeric(cities_raw.POP_MAX, errors="coerce").fillna(0).values,
        "lon": cities_raw.geometry.x.values,
        "lat": cities_raw.geometry.y.values,
    })

    df = basins.merge(prov[["CODE", "NAME", "CUM_OIL", "REM_OIL", "geometry"]],
                      left_on="code", right_on="CODE", how="left")
    df = df[df.geometry.notna()].copy()
    df = df.merge(fields, on="code", how="left")
    g = gpd.GeoDataFrame(df, geometry="geometry", crs=prov.crs)
    pt = g.geometry.representative_point()
    g["lon"], g["lat"] = pt.x.values, pt.y.values

    # which country each province sits in
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(g.lon, g.lat), crs="EPSG:4326")
    joined = gpd.sjoin(pts, countries, how="left", predicate="within")
    joined = joined[~joined.index.duplicated(keep="first")]
    g["country"] = joined.ADMIN.reindex(g.index).values

    # Build the same figure make_oil.py builds, so pixel positions line up.
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    gs = GridSpec(2, 1, figure=fig, **GRID)
    ax = fig.add_subplot(gs[0], projection=PROJ)
    ax.set_global()
    fig.canvas.draw()
    W, H = fig.get_size_inches() * fig.dpi

    out = []
    for _, r in g.iterrows():
        if r.vol <= MIN_VOL:
            continue
        x, y = PROJ.transform_point(r.lon, r.lat, PLATE)
        px, py = ax.transData.transform((x, y))
        # matplotlib y is measured from the bottom, CSS from the top
        fx, fy = px / W, 1.0 - py / H
        if not (0 <= fx <= 1 and 0 <= fy <= 1):
            print("  off-canvas, skipped:", r["name"])
            continue

        parts = []
        biggest_r = 0.0
        for k in KEYS:
            v = float(r[k]) * float(r.vol)
            if v <= 0.05:
                continue
            s = MARKER_MIN + (MARKER_MAX - MARKER_MIN) * math.sqrt(min(v / REF, 1.0))
            biggest_r = max(biggest_r, math.sqrt(s / math.pi) * DPI / 72.0)
            parts.append({"interval": LABEL[k], "color": COLOR[k], "bbl": round(v, 1)})
        parts.sort(key=lambda d: -d["bbl"])

        city, city_country, dist = nearest_city(r.lon, r.lat, cities)
        # Past is cumulative production, future is whatever the basin's total
        # leaves over. A hand-set past_frac wins, because the USGS cumulative
        # is missing for every US province and understates any basin whose
        # total was raised for unconventional or post-1995 resources.
        total = float(r.vol)
        if not pd.isna(r.get("past_frac")):
            past = total * float(r.past_frac)
        elif float(r.CUM_OIL or 0) > 0:
            past = float(r.CUM_OIL) / 1000.0
        else:
            past = None
        future = None if past is None else max(total - past, 0.0)

        # An offshore province falls inside no country polygon, so the spatial
        # join yields NaN. NaN is truthy in Python, so it has to be tested for
        # explicitly rather than leaned on with `or`.
        country = None if pd.isna(r.country) else str(r.country)
        if country is None:
            country = None if pd.isna(city_country) else str(city_country)

        out.append({
            "code": int(r.code),
            "name": r["name"],
            "country": country or "offshore",
            "city": city,
            "city_km": dist,
            "discovered": None if pd.isna(r.discovered) else int(r.discovered),
            "fields": "" if pd.isna(r.major_fields) else r.major_fields,
            "total": round(float(r.vol), 1),
            "past": None if past is None else round(past, 1),
            "future": None if future is None else round(future, 1),
            "intervals": parts,
            "x": round(fx, 5), "y": round(fy, 5),
            "r": round(max(biggest_r, MIN_HIT_PX) / W, 5),
            "note": "" if pd.isna(r.note) else r.note,
        })

    out.sort(key=lambda d: -d["total"])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    # allow_nan=False makes this raise rather than emit NaN, which is not legal
    # JSON and fails silently in the browser as a parse error.
    a.out.write_text(json.dumps(
        {"width": int(W), "height": int(H), "hotspots": out},
        indent=1, allow_nan=False))
    plt.close(fig)

    missing_year = [h["name"] for h in out if h["discovered"] is None]
    print(f"{len(out)} hotspots -> {a.out}")
    print(f"canvas {int(W)}x{int(H)} px")
    if missing_year:
        print("no discovery year:", ", ".join(missing_year))


if __name__ == "__main__":
    main()
