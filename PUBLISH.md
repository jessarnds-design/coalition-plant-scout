# Publish — Church Plant Scout map

Files ready to push to **https://github.com/jessarnds-design/coalition-plant-scout** for GitHub Pages.

## What to publish

| Local path | Repo role |
|---|---|
| `public/index.html` | GitHub Pages entry (same content as `map.html`) |
| `map.html` | Source map (keep in sync with `public/index.html`) |
| `churches.json` | Current inventory (71 churches after 2026-09-17 removals) |
| `gaps.csv` / `gaps_curated.json` / `gaps_full.json` / `gaps-ranked.md` | Gap data (Tahoe nearest updated) |
| `README.md` | Method + removals note |

## Suggested push (from a machine authenticated as `jessarnds-design`)

```bash
cd /workspace/church-plant-scout   # or your local clone of coalition-plant-scout
# copy these files into the repo root / docs / as your Pages setup expects
git add public/index.html map.html churches.json gaps.csv gaps_curated.json gaps_full.json gaps-ranked.md README.md PUBLISH.md
git commit -m "Refresh plant scout map after Placerville + Grizzly Flats removals (2026-09-17)"
git push origin main
```

If Pages is served from `/docs` or the `gh-pages` branch, place `public/index.html` accordingly (often as `index.html` at the Pages root).

## Do not

- Notify or contact removed churches/pastors.
- Treat Community Bible Church Placerville or Grizzly Flats Community Church as like-minded coverage.

## Status (2026-09-17 PT)

- Map regenerated from `churches.json`; both removed names absent from `map.html` / `public/index.html`.
- South Lake Tahoe nearest like-minded: **Colfax Baptist Church (Colfax), ~54.1 mi** (was Grizzly Flats ~36.2 mi).
- `gh` on the scout box was **not** authenticated as jessarnds-design — push left for Jess.

## Legend (Jess 2026-09-17)

No **Weak presence** category on the heat map. Do not plot `weak_public_presence` pins or show that overlay.
