# Where the world's crude oil was born

A deep-time animation. A clock runs from 460 million years ago to the present
over reconstructed continents. Each petroleum province appears as a circle at
the moment its source rock was deposited, then drifts with its plate to its
modern position. Circle area is known oil in billion barrels. Colour is the
source-rock interval, oldest darkest.

The bar along the bottom is the legend. Each interval's age range is drawn in
its own map colour and stays muted until the clock reaches it, so it doubles as
a progress indicator.

## Files

| File | What it is |
|---|---|
| `make_oil.py` | Renders the animation and six interval stills |
| `export_hotspots.py` | Writes `assets/data/oil_hotspots.json` for the interactive page |
| `province_fields.csv` | Discovery year, major field names and produced-fraction per province |
| `basins_oil.csv` | Known oil per province and its split across intervals. The judgment layer |
| `usgs/WEP_PRVG.*` | USGS world geologic provinces, all 1,023 defined provinces |
| `owid_oil.csv` | EIA proved oil reserves by country, via Our World in Data |
| `out_oil/` | `oil_history.mp4`, `oil_history.gif`, six interval stills |

`pmm_data/` holds the Merdith plate model, about 99 MB. It is gitignored and is
re-downloaded automatically on first run.

`owid_oil.csv` is not read at runtime. It is kept because it is the anchor
behind the adjusted volumes in `basins_oil.csv`, and without it those numbers
cannot be audited.

## Run

```
python3 -m venv venv
./venv/bin/pip install geopandas matplotlib pandas pyogrio cartopy gplately
./venv/bin/python make_oil.py --stills      # six stills, about a minute
./venv/bin/python make_oil.py --step 4      # full animation, needs ffmpeg
```

## The six intervals

After Klemme and Ulmishek (1991), who assigned the world's oil and gas to six
source-rock intervals. Boundaries are used a little loosely so each major source
rock lands in the nearest bucket.

| Interval | Range used | Colour | Oil | Example source rocks |
|---|---|---|---|---|
| Silurian | 444–419 Ma | `#8c2d04` | 17 | Qusaiba, Tanezzuft |
| Upper Devonian – Mississippian | 383–330 Ma | `#cc4c02` | 266 | Domanik, Bakken, Exshaw |
| Pennsylvanian – Lower Permian | 323–273 Ma | `#ec7014` | 95 | Wolfcamp, Paradox, Fengcheng |
| Upper Jurassic | 164–140 Ma | `#fe9929` | 866 | Hanifa, Bazhenov, Tithonian, Vaca Muerta |
| Middle Cretaceous | 130–85 Ma | `#fec44f` | 977 | La Luna, Querecual, Lagoa Feia, Canje |
| Oligocene – Miocene | 34–5 Ma | `#fee391` | 278 | Maykop, Akata, Monterey |

Oil in billion barrels. A further 222 billion barrels sits in an `other` bucket
covering Precambrian, Cambrian–Ordovician, Triassic, Lower–Middle Jurassic and
Paleocene–Eocene sources. It is counted in the table but not drawn.

Two thirds of the world's oil comes from the Upper Jurassic and Middle
Cretaceous. The Silurian, which is the single largest source of natural gas
because of the North Field and South Pars, barely registers for oil.

## Method

Each province in `basins_oil.csv` carries a known-oil volume and an interval
split. Province centroids are assigned plate IDs and rotated back through the
Merdith et al. (2021) model, which covers 1000 Ma to the present. At each frame
the reconstructed coastlines are drawn, and every province whose interval has
already been reached appears at its reconstructed position.

Volumes are **known oil**, meaning cumulative production plus remaining proved
reserves, not oil left in the ground.

## Where the numbers come from, and how good they are

127 provinces, 2,721 billion barrels, split three ways by the `source` column:

| source | provinces | share of volume |
|---|---|---|
| `usgs` | 79 | 12% |
| `adjusted` | 15 | 78% |
| `added` | 33 | 10% |

- `usgs` takes the volume straight from the USGS World Petroleum Assessment
  2000, which used data through roughly 1995.
- `adjusted` starts from the USGS figure and revises it. The note column says
  why in each case.
- `added` is entered by hand. The 2000 assessment covered the world **excluding
  the United States**, so every US province is mine, as is the Santos pre-salt
  and the Guyana–Suriname basin, both found after the assessment.

**Only about an eighth of the oil volume is a published number taken
unchanged.** The adjusted group is small in count but holds the giants, and it
dominates because the two largest oil accumulations on Earth, the Orinoco heavy
oil belt and the Canadian oil sands, are unconventional and sit outside the
conventional assessment entirely.

Treat the absolute volumes as indicative. The relative pattern across intervals
is the part worth reading.

**A note on the interval splits.** Every interval fraction in `basins_oil.csv`
is the author's own attribution based on which source rock is known to charge
each basin. They were not transcribed from USGS Total Petroleum System reports
or any other single document. The underlying geology is standard and each row
carries a note naming the formations it rests on, but the fractions themselves
are judgment and have not been checked against a published per-basin source.

## Caveats

- A province is drawn as one point at its centroid. Large provinces such as
  West Siberia are not points in reality.
- Reconstruction is reliable for cratonic and passive-margin basins. It is
  rougher for basins caught in collision belts, such as the Zagros, where the
  modern outline has been shortened and displaced.
- Provinces appear at their source rock's **deposition** age. Oil generation
  happens tens of millions of years later, once burial reaches the oil window,
  and the animation does not model that lag.
- Oil volumes mix conventional and unconventional resources. Without the
  Orinoco belt and the Canadian oil sands, Venezuela and Canada would be
  near-invisible, but including them puts two different resource categories in
  one number.
- The plate model's time must be set on the `PlotTopologies` object before every
  frame is drawn. If it is not, the province circles still move but the
  continents silently stay at present day. Worth checking first if a new figure
  looks wrong.
- `export_hotspots.py` duplicates `FIGSIZE`, `DPI`, the `GridSpec` settings and
  the marker-size formula from `make_oil.py` so that the clickable circles land
  on the drawn ones. Change either file and the same change is needed in the
  other, then re-run the export, or the overlay drifts.
- Frames render at 200 dpi, giving 2500 x 1480. The GIF is downscaled to 1100 px
  because it is only a fallback; the page serves the full-resolution MP4.
- The export refuses to write NaN. Invalid JSON fails silently in the browser as
  a parse error, which is hard to trace back from an empty map.

## Sources

- Klemme, H.D. and Ulmishek, G.F., 1991, *Effective petroleum source rocks of
  the world*, AAPG Bulletin 75, 1809–1851.
- U.S. Geological Survey World Petroleum Assessment 2000, geologic provinces and
  known volumes.
- Merdith, A.S. et al., 2021, *Extending full-plate tectonic models into deep
  time*, Earth-Science Reviews 214.
- U.S. Energy Information Administration proved reserves, via Our World in Data.
