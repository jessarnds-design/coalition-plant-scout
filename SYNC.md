# Sync and publish the Church Plant Scout heat map

Weekly (or anytime the Coalition Google My Map changes), rerun the sync and push the updated Pages site.

## Sync

From this folder:

```bash
python3 sync_from_kml.py
```

That command:

1. Fetches the public KML: https://www.google.com/maps/d/kml?mid=1BFWKsEJu0DoY82dBpnqJ-jFAbnHAj5mO&forcekml=1
2. Rebuilds `churches.json` from the Like-Minded, Church Plants, and standalone Spanish layers
3. Patches `map.html`, `index.html`, and `public/index.html` (same Leaflet page; OpenStreetMap tiles; no Weak Presence category)
4. Recalculates nearest-church, distance, and need scores for gap areas, and drops gaps now covered within 5 miles (Davis is kept)
5. Writes `gaps.csv`, `gaps_curated.json`, `gaps_full.json`, `gaps-ranked.md`, `live-map.kml`, and `last-sync-report.md`

Useful flags:

```bash
python3 sync_from_kml.py --dry-run          # print the diff only
python3 sync_from_kml.py --kml live-map.kml # use a local KML, no fetch
```

If a new My Map pin has no city/website/pastor in the script, it is still included and a warning asks you to add a `PIN_META` row in `sync_from_kml.py`. Hartstone Bible Camp is skipped. Spanish ministries attached to an English church (Pleasant Hill, NorthCreek, Hickman) are not plotted as a second pin. Windsor Christian Church stays `adjacent_explore` and does not count as coverage.

## Publish

GitHub Pages is served from the **root of `main`** in https://github.com/jessarnds-design/coalition-plant-scout  
Live URL: https://jessarnds-design.github.io/coalition-plant-scout/

From a machine authenticated as `jessarnds-design` (`gh auth login` or a checkout with push access):

```bash
# If this folder is not already the git clone, copy the built files into the clone root.
git add index.html map.html churches.json gaps.csv gaps_curated.json gaps_full.json \
        gaps-ranked.md README.md PUBLISH.md SYNC.md sync_from_kml.py last-sync-report.md
git commit -m "Sync plant scout heat map from Coalition My Map ($(date +%F))"
git push origin main
```

Wait a minute, then confirm the live page shows the new date in the legend (`Updated YYYY-MM-DD PT`). GitHub Pages can take a short while to refresh.

Do not switch the tiles back to CARTO (they need an API key). Do not add a Weak Presence legend or pins.
