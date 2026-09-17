# Ranked church-planting gap areas — Northern California

**Home base:** Grace Church of Napa Valley (Napa, CA)  
**Generated:** 2026-09-17 (PT)  
**Like-minded set:** CoalitionCEC roster (64) + NorCal Coalition-map supplements + TMS/MacArthur-lane adds (see `churches.json`)  
**Gap radius:** ~18 miles primary; large cities (≥50k) flagged from ~12+ miles if no in-city church  

## Scoring method (transparent)

| Factor | Max pts | What it measures |
|---|---:|---|
| Population / metro size | 30 | Larger gap towns score higher |
| Distance to nearest like-minded church | 25 | Miles beyond coverage; Davis forced high (map pin) |
| Population growth / housing | 15 | Rough growth index 0–10 × 1.5 |
| Like-minded vacuum (≤40 mi count) | 15 | Fewer nearby Coalition churches → higher |
| Proximity to Napa (shepherding bonus) | 15 | Closer to home base → higher |
| **Total** | **100** | |

**Opportunity types**
- **A_send_pastor** — plausible existing like-minded families / commute pattern; send pastor to gather a plant
- **B_evangelism_first** — large population / thin gospel density; evangelism with future plant hope
- **mixed_or_explore** — needs local intel

**Not greenfield gaps (excluded or marked separately)**
- Plants **in progress:** ChristChurch of the Valley (Vacaville), Calvary Grace (Orangevale), Folsom Bible Church, Trinity Church Benicia, **Patterson Bible Church (Patterson)** — count as coverage, not empty gaps
- **Laytonville** Community Christian Church — on map, weak public presence; do not treat as strong coverage or as a ranked open gap
- **Adjacent / explore pins** (such as Windsor Christian Church) are tracked separately and do not close gaps, change nearest-church values, or count toward coverage.
- **Davis** — still ranked #1 as send-a-pastor target (Coalition “Needs a Church Planter”)

**Update 2026-09-17 (PT):** Patterson Bible Church added as `plant_in_progress` (green coverage). Patterson removed from full gap list. Tracy/Modesto nearest churches unchanged (still Manteca/Hickman); each gains +1 like-minded within 40 mi. Los Banos nearest lightly retargeted to Patterson plant (~33.4 mi; was Hollister ~33.8) — score left at 53.5 (no full rebuild).

**Update 2026-09-17 (PT) — Monterey Bay TMS lane:** Added **Grace Church Monterey Bay** (Seaside; Dominic Avila) and **First Baptist Church of Monterey** (Josh Nichols) as `established` coverage. **Seaside removed** from ranked gaps (now covered in-city). **Salinas** nearest retargeted to Grace Church Monterey Bay ~10.7 mi (was Hollister ~18.4); nearby≤40 mi now 5. Score left at 52.0 (no full rebuild). Monterey / Marina / Carmel dropped from full gap list as covered.

---

## Top ranked gaps

### 1. Davis — need_score **63.5**

- **Population (est.):** 67,000
- **Nearest like-minded:** Chinese Grace Bible Church Sacramento (Sacramento) — **10.7 mi**
- **Distance to Napa home base:** 34.6 mi
- **Like-minded within 40 mi:** 22
- **Opportunity type:** `A_send_pastor`
- **Score breakdown:** pop 18 + dist 22 + growth 7.5 + vacuum 4 + napa 12
- **Why it ranks:** AUTHORITATIVE Coalition pin: “Needs a Church Planter.” ~67k + UC Davis. Nearest Sac churches ~11–15 mi but Coalition still flags unmet local need. Classic send-a-pastor / gather-commuters plant. High Napa shepherding feasibility (~40 mi).

### 2. Stockton — need_score **51.0**

- **Population (est.):** 320,000
- **Nearest like-minded:** Crossroads Grace Community Church Manteca (Manteca) — **13.4 mi**
- **Distance to Napa home base:** 61.3 mi
- **Like-minded within 40 mi:** 7
- **Opportunity type:** `B_evangelism_first`
- **Score breakdown:** pop 30 + dist 6 + growth 6.0 + vacuum 4 + napa 5
- **Why it ranks:** ~320k metro core. Nearest Coalition church Crossroads Grace (Manteca) ~13 mi — soft gap by mileage but large unchurched/underserved urban mass. Evangelism-first with plant horizon. Limited Coalition density in Stockton proper.

### 3. Salinas — need_score **52.0**

- **Population (est.):** 160,000
- **Nearest like-minded:** Grace Church Monterey Bay (Seaside) — **10.7 mi**
- **Distance to Napa home base:** 119.5 mi
- **Like-minded within 40 mi:** 5
- **Opportunity type:** `B_evangelism_first`
- **Score breakdown:** pop 26 + dist 10 + growth 6.0 + vacuum 8 + napa 2 *(scores not rebuilt; nearest/nearby updated 2026-09-17)*
- **Why it ranks:** ~160k. Nearest now Grace Monterey Bay ~10.7 mi (was Hollister ~18). Peninsula TMS-lane coverage improved; Salinas proper still lacks an in-city pin. Strong B-type opportunity.

### 4. Merced — need_score **61.5**

- **Population (est.):** 90,000
- **Nearest like-minded:** Hickman Community Church (Hickman) — **26.5 mi**
- **Distance to Napa home base:** 122.6 mi
- **Like-minded within 40 mi:** 1
- **Opportunity type:** `B_evangelism_first`
- **Score breakdown:** pop 22 + dist 18 + growth 7.5 + vacuum 12 + napa 2
- **Why it ranks:** ~90k + UC Merced growth. Nearest Hickman ~27 mi. Clear Central Valley gap south of Modesto cluster. Growth + distance.

### 5. Modesto — need_score **55.0**

- **Population (est.):** 218,000
- **Nearest like-minded:** Hickman Community Church (Hickman) — **13.6 mi**
- **Distance to Napa home base:** 86.2 mi
- **Like-minded within 40 mi:** 2
- **Opportunity type:** `B_evangelism_first`
- **Score breakdown:** pop 30 + dist 6 + growth 6.0 + vacuum 8 + napa 5
- **Why it ranks:** ~218k. Hickman (~14 mi) is small-town coverage — Modesto proper lacks a Coalition congregation. Treat as soft urban gap / B-type.

### 6. Yuba City — need_score **51.0**

- **Population (est.):** 70,000
- **Nearest like-minded:** Iglesia Bíblica de Lincoln (Lincoln) — **24.6 mi**
- **Distance to Napa home base:** 67.7 mi
- **Like-minded within 40 mi:** 12
- **Opportunity type:** `B_evangelism_first`
- **Score breakdown:** pop 22 + dist 14 + growth 6.0 + vacuum 4 + napa 5
- **Why it ranks:** ~70k (Yuba–Sutter). ~25 mi from Lincoln churches; thin north-of-Sac coverage toward Chico. B-type.

### 7. Novato — need_score **51.5**

- **Population (est.):** 53,000
- **Nearest like-minded:** FocalPoint Bible Church (El Sobrante) — **17.4 mi**
- **Distance to Napa home base:** 20.5 mi
- **Like-minded within 40 mi:** 19
- **Opportunity type:** `A_send_pastor`
- **Score breakdown:** pop 18 + dist 10 + growth 4.5 + vacuum 4 + napa 15
- **Why it ranks:** ~53k North Marin. ~17 mi to FocalPoint (El Sobrante) across the bay/bridge or longer to Santa Rosa. Marin County largely uncovered. A-type: some families may drive to East Bay/North Bay.

### 8. Woodland — need_score **51.5**

- **Population (est.):** 61,000
- **Nearest like-minded:** The Cornerstone Bible Church Sacramento (Sacramento) — **15.5 mi**
- **Distance to Napa home base:** 38.2 mi
- **Like-minded within 40 mi:** 22
- **Opportunity type:** `A_send_pastor`
- **Score breakdown:** pop 18 + dist 10 + growth 7.5 + vacuum 4 + napa 12
- **Why it ranks:** ~61k. Adjacent to Davis need; ~15 mi to Sac Cornerstone. Natural tandem with Davis plant corridor (Woodland–Davis–Dixon). A-type.

### 9. Tracy — need_score **49.0**

- **Population (est.):** 95,000
- **Nearest like-minded:** Crossroads Grace Community Church Manteca (Manteca) — **13.2 mi**
- **Distance to Napa home base:** 63.2 mi
- **Like-minded within 40 mi:** 13
- **Opportunity type:** `A_send_pastor`
- **Score breakdown:** pop 22 + dist 6 + growth 12.0 + vacuum 4 + napa 5
- **Why it ranks:** ~95k, high housing growth. Between Livermore GCC and Manteca Crossroads (~13 mi). Soft gap but growth + commute families → A-type gather plant.

### 10. San Mateo — need_score **51.0**

- **Population (est.):** 100,000
- **Nearest like-minded:** Light By The Bay Church (San Lorenzo) — **13.0 mi**
- **Distance to Napa home base:** 52.8 mi
- **Like-minded within 40 mi:** 19
- **Opportunity type:** `mixed_or_explore`
- **Score breakdown:** pop 26 + dist 6 + growth 6.0 + vacuum 4 + napa 9
- **Why it ranks:** ~100k Peninsula. Nearest Light By The Bay (San Lorenzo) ~13 mi across the bay or SF Bible farther NW. Mid-Peninsula lacks a Coalition pin (no San Mateo/Redwood City/Palo Alto church on roster). Soft but strategic.

### 11. Lodi — need_score **51.0**

- **Population (est.):** 68,000
- **Nearest like-minded:** Laguna Chinese Baptist Church Elk Grove (Elk Grove) — **22.4 mi**
- **Distance to Napa home base:** 58.3 mi
- **Like-minded within 40 mi:** 16
- **Opportunity type:** `mixed_or_explore`
- **Score breakdown:** pop 18 + dist 14 + growth 6.0 + vacuum 4 + napa 9
- **Why it ranks:** ~68k. ~22 mi from Elk Grove cluster. North San Joaquin gap between Sac south and Stockton/Manteca.

### 12. Los Banos — need_score **53.5**

- **Population (est.):** 47,000
- **Nearest like-minded:** Patterson Bible Church (Patterson) — **33.4 mi**
- **Distance to Napa home base:** 118.8 mi
- **Like-minded within 40 mi:** 2
- **Opportunity type:** `mixed_or_explore`
- **Score breakdown:** pop 14 + dist 22 + growth 7.5 + vacuum 8 + napa 2
- **Why it ranks:** ~47k on I-5 corridor. ~34 mi to Hollister. Isolated Valley west-side town; long drives either direction. Nearest lightly updated to Patterson Bible Church plant (~33 mi).

### 13. South Lake Tahoe — need_score **55.5**

- **Population (est.):** 21,000
- **Nearest like-minded:** Colfax Baptist Church (Colfax) — **54.1 mi**
- **Distance to Napa home base:** 133.2 mi
- **Like-minded within 40 mi:** 0
- **Opportunity type:** `mixed_or_explore`
- **Score breakdown:** pop 10 + dist 24 + growth 4.5 + vacuum 15 + napa 2
- **Why it ranks:** ~21k tourist/resident mix. ~54 mi to Colfax Baptist (was ~36 mi to Grizzly Flats; removed 2026-09-17). Sierra recreation gap; seasonal + year-round gospel need.

### 14. Crescent City — need_score **49.5**

- **Population (est.):** 6,500
- **Nearest like-minded:** Grace Baptist Church (Eureka) — **67.0 mi**
- **Distance to Napa home base:** 257.0 mi
- **Like-minded within 40 mi:** 0
- **Opportunity type:** `mixed_or_explore`
- **Score breakdown:** pop 6 + dist 25 + growth 1.5 + vacuum 15 + napa 2
- **Why it ranks:** Far North Coast (~6.5k). ~67 mi to Eureka Grace Baptist. Extreme distance; small pop but total coverage void Del Norte.

---

## Opportunity-type summary

### A) Send-a-pastor / gather plants
- **Davis** (score 63.5)
- **Novato** (score 51.5)
- **Woodland** (score 51.5)
- **Tracy** (score 49.0)

### B) Evangelism-first (plant horizon)
- **Stockton** (score 51.0)
- **Salinas** (score 52.0)
- **Merced** (score 61.5)
- **Modesto** (score 55.0)
- **Yuba City** (score 51.0)

### Mixed / explore
- **San Mateo** (score 51.0)
- **Lodi** (score 51.0)
- **Los Banos** (score 53.5)
- **South Lake Tahoe** (score 55.5)
- **Crescent City** (score 49.5)

---

## Corridor notes (scout judgment)

1. **Davis–Woodland–Dixon:** Highest strategic priority near Sac; Davis already map-flagged.
2. **Marin (Novato / San Rafael):** Surprising soft gap between Santa Rosa cluster and East Bay FocalPoint/SF.
3. **Peninsula mid-corridor (San Mateo / Redwood City / Palo Alto):** Soft distances to East Bay/SF but no Coalition pin on the Peninsula spine.
4. **North San Joaquin (Stockton / Lodi / Tracy):** Large populations; Manteca/Livermore edges only.
5. **Modesto–Turlock–Merced:** Central Valley south of Hickman is thin.
6. **Salinas / Monterey Peninsula:** Peninsula now has TMS-lane coverage (Grace Monterey Bay, FBC Monterey); **Salinas Valley** proper remains the soft gap (nearest Seaside ~10.7 mi).
7. **Far North / Sierra (Crescent City, Truckee, Tahoe, Susanville):** High isolation, lower absolute pop — mission/outpost profile.

## Confidence & limitations

- Inventory is Coalition-first plus confirmed TMS/MacArthur-lane adds (e.g. Monterey Bay 2026-09-17); further off-map like-minded churches may still shrink gaps.
- Distances are great-circle miles, not drive time (traffic, bridges, mountains matter — Marin, Tahoe, North Coast especially).
- Population and growth are approximate ACS-order estimates for ranking, not census extracts.
- This is a **first-pass scout**, not a planting decision.
