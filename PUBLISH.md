# Publish — Church Plant Scout map

Live: **https://jessarnds-design.github.io/coalition-plant-scout/**  
Repo: **https://github.com/jessarnds-design/coalition-plant-scout** (Pages from the `main` branch root)

## What to publish

| Local path | Repo role |
|---|---|
| `index.html` | GitHub Pages entry (same content as `map.html`) |
| `map.html` | Source map, kept in sync with `index.html` |
| `public/index.html` | Local copy of the Pages entry (optional; not required in the repo) |
| `churches.json` | Current inventory |
| `gaps.csv` / `gaps_curated.json` / `gaps_full.json` / `gaps-ranked.md` | Gap data |
| `sync_from_kml.py` | Reusable KML → map sync |
| `SYNC.md` | How to rerun and publish |
| `README.md` | Method + change notes |

The usual path is: `python3 sync_from_kml.py`, then commit and `git push origin main` as `jessarnds-design`. Full steps are in `SYNC.md`.

## Do not

- Plot a Weak Presence category (no `weak_public_presence` pins, legend, or overlay).
- Use CARTO tiles (they require an API key). Keep OpenStreetMap.
- Treat attached Spanish ministries of an English church as a second coverage pin.
- Include Hartstone Bible Camp (it is not a church).

## Status (2026-11-14 PT)

- Inventory synced from the live Coalition My Map: 84 coverage pins + Windsor Christian Church (`adjacent_explore`).
- CrossPointe Community Church (Redding) and Patterson Bible Church (not on the My Map) removed.
- San Mateo, Lodi, Tracy, and Modesto dropped from the ranked gap list (now have a like-minded / standalone Spanish congregation within 5 miles).
- South Lake Tahoe nearest is now Grace Community Church Minden (~12.4 mi).
- `gh` on the scout box was not authenticated as `jessarnds-design` at sync time; push still needs that login (or another checkout with push access).
