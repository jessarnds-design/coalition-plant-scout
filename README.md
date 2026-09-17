# Church Plant Scout — Northern California (first pass)

**For:** Grace Church / Jess Arnds / Coalition of Christ-Exalting Churches  
**Home base:** Grace Church of Napa Valley, Napa, CA  
**Date:** 2026-09-17 (PT)

## Deliverables

| File | Contents |
|---|---|
| `churches.json` | Inventory of like-minded churches (Coalition roster + map supplements) with lat/lon |
| `gaps-ranked.md` | Ranked gap areas with scores, rationale, opportunity types |
| `gaps.csv` | Machine-readable top gaps for heat-map / sheets |
| `map.html` | Simple Folium map: churches (cool) vs gaps (hot) |
| `README.md` | This file |

## Method

1. **Authoritative inventory:** 64 churches from `/workspace/church-directory/norcal-roster-for-plant-scout.md` (CoalitionCEC circle).
2. **Coordinates:** Matched to Coalition Google My Map KML (`/workspace/coalition-map.kml`); city centroid fallback if needed.
3. **Supplements for coverage analysis only:** CrossPointe Redding, Evangel Berkeley, Orland EFC, Grace Bible Chico (on Coalition map, not in the 64-row MD). Laytonville CCC noted as weak public presence.
4. **Gap detection:** Cities with meaningful population and no like-minded church within ~18 mi (or ≥12 mi for large cities without an in-city church). Davis kept as #1 per Coalition “Needs a Church Planter” pin.
5. **Plants in progress** (Vacaville ChristChurch of the Valley, Orangevale Calvary Grace, Folsom Bible, Benicia Trinity, **Patterson Bible Church**) **count as coverage**, not greenfield gaps.
6. **Need score (0–100):** population (30) + distance (25) + growth (15) + like-minded vacuum (15) + Napa proximity bonus (15).

## Like-minded definition (authoritative)

A church counts if CoalitionCEC / clearly in that circle, **or** TMS / 9Marks / MacArthur-aligned lane: expository preaching, elder-led, Doctrines of Grace, 5 Solas, sufficiency of Scripture / ACBC-friendly, complementarian, generally cessationist.

This scout **prioritized the Coalition roster** rather than cold-searching all evangelicals.

## Adjacent / explore

- **Windsor Christian Church** (formerly First Baptist Church of Windsor / Windsor First Baptist) is tracked with status `adjacent_explore`. Its GARBC/Regular Baptist roots and conservative SOF make it worth exploring, but it is **not** treated as like-minded coverage and does not change gap calculations.


## Removals (2026-09-17 PT)

Per Jess / Coalition:

- **Community Bible Church Placerville** (Paul Anthes) — removed; church closed.
- **Grizzly Flats Community Church** — removed; no longer like-minded.

Map, gaps (South Lake Tahoe nearest recalculated to Colfax Baptist Church ~54.1 mi), and `churches.json` reflect these removals. Do not treat either congregation as coverage.

## Limitations / confidence

- **First-pass scout.** Directories are incomplete; unaffiliated but like-minded churches may exist and would change gap geometry.
- Miles are **great-circle**, not drive time (bridges, traffic, mountain passes).
- Populations/growth are **approximate** for relative ranking.
- Spanish-language and ethnic congregations on the roster (e.g. Capilla Calvario, Iglesia Bíblica, Laguna Chinese, Grace River City Hmong) are counted as coverage — language fit for a given plant still needs pastoral judgment.
- Do **not** treat Laytonville as strong coverage.

## Executive snapshot

- **Inventory size:** see `churches.json` meta.count (~64 roster + Coalition-map supplements + TMS-lane adds).
- **Top gap:** **Davis** (send-a-pastor; Coalition-marked).
- **Other high-need corridors:** Stockton / North San Joaquin; **Salinas** (Peninsula now covered by TMS-lane churches); Merced–Modesto; Marin (Novato); Davis–Woodland; mid-Peninsula (San Mateo).

## Plants in progress (coverage)

In-progress plants count as coverage on the map (green) and are **not** greenfield gaps:

- ChristChurch of the Valley — Vacaville
- Calvary Grace Church — Orangevale
- Folsom Bible Church — Folsom
- Trinity Church Benicia — Benicia
- **Patterson Bible Church — Patterson** (added 2026-09-17 PT; website lists 2959 Speno Dr; pastor not public; covers Patterson / I-5 west-side corridor near Tracy–Modesto)

## TMS / MacArthur-lane established adds (coverage)

Confirmed like-minded churches outside the Coalition roster MD, added for coverage analysis:

- **Grace Church Monterey Bay** — Seaside (Dominic Avila; TMU/TMS + CHBC internship signals) — added 2026-09-17 PT; removes Seaside gap
- **First Baptist Church of Monterey** — Monterey (Josh Nichols; TMS) — added 2026-09-17 PT

