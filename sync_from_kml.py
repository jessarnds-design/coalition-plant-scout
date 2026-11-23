#!/usr/bin/env python3
"""Sync the NorCal Church Plant Scout heat map from the Coalition Google My Map KML.

Fetches the public KML, rebuilds churches.json and the Leaflet map HTML, refreshes
gap nearest-church / scores, and prints a diff (added / removed / renamed / moved).

Usage:
  python3 sync_from_kml.py              # fetch live KML, write files, print diff
  python3 sync_from_kml.py --dry-run    # compute and print diff, do not write
  python3 sync_from_kml.py --kml PATH   # use a local KML instead of fetching

Source of truth: CoalitionCEC Google My Map public KML.
Does not plot a Weak Presence category. Attached Spanish ministries of an
English church are not added as a second heat/coverage pin. Hartstone Bible
Camp is excluded. OpenStreetMap tiles and map styling are left unchanged.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

NS = {"k": "http://www.opengis.net/kml/2.2"}
DIR = Path(__file__).resolve().parent
KML_URL = (
    "https://www.google.com/maps/d/kml?mid=1BFWKsEJu0DoY82dBpnqJ-jFAbnHAj5mO"
    "&forcekml=1"
)
INCLUDE_LAYERS = {
    "Like-Minded Churches",
    "Church Plants - In Progress",
    "Spanish Churches",
}
HOME_BASE = {
    "name": "Grace Church of Napa Valley",
    "city": "Napa",
    "lat": 38.326962,
    "lon": -122.316686,
}
COVERED_MILES = 5.0  # in-city coverage: drop non-Davis gaps this close
MOVED_MILES = 0.15
URL_RE = re.compile(r"https?://[^\s<>\"']+")

# Pin metadata for disambiguation, city, website, display name.
# Match is (layer, pin name), plus optional lat/lon when the same name
# appears more than once on a layer (within ~5 mi of the hint).
# Add a new row when a brand-new church is pinned on the My Map.
PIN_META = [
    # Like-Minded
    dict(layer="Like-Minded Churches", pin="Gold Country Baptist Church", city="Shingle Springs", website="https://gcb.church", region="Sacramento & Foothills", pastor="Phil Layton"),
    dict(layer="Like-Minded Churches", pin="River City Grace Community Church", city="Sacramento", website="https://rivercitygrace.org", region="Sacramento & Foothills", pastor="Greg Stoever"),
    dict(layer="Like-Minded Churches", pin="Grace Bible Church", city="Roseville", website="https://gracebibleroseville.com", region="Sacramento & Foothills", display="Grace Bible Church Roseville", pastor="Louie Handugan", lat=38.75256, lon=-121.31332),
    dict(layer="Like-Minded Churches", pin="Christian Family Fellowship Santa Rosa", city="Santa Rosa", website="https://www.cffsantarosa.org", region="North Bay", pastor="Aaron Pendergrass"),
    dict(layer="Like-Minded Churches", pin="Potter Valley Bible Church", city="Potter Valley", website="https://pottervalleybible.org", region="North Coast", pastor="Greg Pederson"),
    dict(layer="Like-Minded Churches", pin="Middletown Bible Church", city="Middletown", website="https://middletownbible.org", region="North Bay", pastor="Rob Rainey"),
    dict(layer="Like-Minded Churches", pin="Community Bible Church", city="Vallejo", website="https://cbcvallejo.org", region="North Bay", display="Community Bible Church Vallejo", pastor="Phil Foley"),
    dict(layer="Like-Minded Churches", pin="Grace Church of Napa Valley", city="Napa", website="https://gracenapa.org", region="North Bay", pastor="Jess Arnds", home=True),
    dict(layer="Like-Minded Churches", pin="Redeemer Bible Church", city="San Jose", website="https://redeemersj.com", region="San Francisco / Peninsula / South Bay", display="Redeemer Bible Church San Jose", pastor="Aaron Vega", lat=37.32241, lon=-121.84283),
    dict(layer="Like-Minded Churches", pin="Creekside Bible Church", city="Cupertino", website="https://www.creeksidebiblechurch.com", region="San Francisco / Peninsula / South Bay", display="Creekside Bible Church Cupertino", pastor="Cliff McManis"),
    dict(layer="Like-Minded Churches", pin="Grace Bible Church of Pleasant Hill", city="Pleasant Hill", website="https://www.graceforus.org", region="East Bay", pastor="Tony Sanelli"),
    dict(layer="Like-Minded Churches", pin="Living Hope Fellowship", city="Chico", website="https://livinghopechico.com", region="North Valley", display="Living Hope Fellowship Chico", pastor="Heath Jarrett"),
    dict(layer="Like-Minded Churches", pin="Cool Community Church", city="Cool", website="https://coolchurch.org", region="Sacramento & Foothills", pastor="Drew Buell"),
    dict(layer="Like-Minded Churches", pin="Chinese Grace Bible Church", city="Sacramento", website="https://www.cgbcsac.org", region="Sacramento & Foothills", display="Chinese Grace Bible Church Sacramento", pastor="Tranwei Yu"),
    dict(layer="Like-Minded Churches", pin="Trinity Bible Church", city="Morgan Hill", website="https://trinitybiblechurch.org", region="San Francisco / Peninsula / South Bay", display="Trinity Bible Church Morgan Hill", pastor="Manny Pereira"),
    dict(layer="Like-Minded Churches", pin="Gateway Bible Church", city="Castro Valley", website="https://www.gatewaylife.org", region="East Bay", display="Gateway Bible Church Castro Valley", pastor="Rod Phillips"),
    dict(layer="Like-Minded Churches", pin="Laguna Chinese Baptist Church", city="Elk Grove", website="https://www.lagunabaptist.org", region="Sacramento & Foothills", display="Laguna Chinese Baptist Church Elk Grove", pastor="Jonathan Szeto"),
    dict(layer="Like-Minded Churches", pin="FocalPoint Bible Church", city="El Sobrante", website="https://focalpointbible.org", region="East Bay", pastor="Charlie Nason"),
    dict(layer="Like-Minded Churches", pin="San Francisco Bible Church", city="San Francisco", website="https://www.sfbible.org", region="San Francisco / Peninsula / South Bay", pastor="Henry Tam"),
    dict(layer="Like-Minded Churches", pin="First Baptist Church", city="Weaverville", website="https://www.fbcweaverville.org", region="Far North", display="First Baptist Church Weaverville", pastor="Travis Flournoy"),
    dict(layer="Like-Minded Churches", pin="Orchard Community Church", city="Campbell", website="https://www.orchardcommunity.org", region="San Francisco / Peninsula / South Bay", display="Orchard Community Church Campbell", pastor="Jeremy Wong and Daniel Kim"),
    dict(layer="Like-Minded Churches", pin="Hartstone Bible Camp", city="Potter Valley", region="North Coast", skip=True, skip_reason="Camp, not a church."),
    dict(layer="Like-Minded Churches", pin="Redwood Christian Fellowship", city="Fortuna", website="https://www.rcffortuna.org", region="North Coast", display="Redwood Christian Fellowship Fortuna", pastor="Bob Hapgood"),
    dict(layer="Like-Minded Churches", pin="Light By The Bay Church", city="San Lorenzo", website="https://lightbythebay.church", region="East Bay", pastor="Glenn Nicolas"),
    dict(layer="Like-Minded Churches", pin="Lone Hill Church", city="Los Gatos", website="https://www.lonehillchurch.org", region="San Francisco / Peninsula / South Bay", display="Lone Hill Church San Jose", pastor="Bj Lopez"),
    dict(layer="Like-Minded Churches", pin="Elk Grove Bible Church", city="Elk Grove", website="https://www.redeemerbible.net", region="Sacramento & Foothills", display="Redeemer Bible Church Elk Grove", pastor="Justin Schroeder", note="Map pin is still titled Elk Grove Bible Church; the congregation now goes by Redeemer Bible Church."),
    dict(layer="Like-Minded Churches", pin="First Baptist Church of Fortuna", city="Fortuna", website="https://www.fbcfortuna.com", region="North Coast", pastor="John Carter"),
    dict(layer="Like-Minded Churches", pin="Grace Bible Fellowship", city="Brentwood", website="https://www.gbfellowship.net", region="East Bay", display="Grace Bible Fellowship Brentwood", pastor="Mike Shrout, Wes Wade, and Deepak Koilvaram"),
    dict(layer="Like-Minded Churches", pin="NorthCreek Church", city="Walnut Creek", website="https://northcreek.org", region="East Bay", pastor="Kent Dresdow"),
    dict(layer="Like-Minded Churches", pin="Redeemer Bible Church", city="Oceanside", website="http://www.christredeemedus.org", region="Southern California", display="Redeemer Bible Church Oceanside", pastor="Angelo Tolentino", lat=33.20610, lon=-117.31486),
    dict(layer="Like-Minded Churches", pin="The Cornerstone Bible Church", city="Sacramento", website="https://www.tcbcsacramento.org", region="Sacramento & Foothills", display="The Cornerstone Bible Church Sacramento", pastor="Nick Haight"),
    dict(layer="Like-Minded Churches", pin="Grace Church of Santa Rosa", city="Santa Rosa", website="https://www.gracechurchsr.com", region="North Bay", pastor="Carl Fletcher"),
    dict(layer="Like-Minded Churches", pin="Grace Bible Church", city="Fair Oaks", website="https://gracefairoaks.com", region="Sacramento & Foothills", display="Grace Bible Church Fair Oaks", pastor="Richard Gregory", lat=38.65706, lon=-121.22516),
    dict(layer="Like-Minded Churches", pin="Gospel Community Church", city="Santa Cruz", website="https://www.gospelcommunitysc.org", region="Central Coast / Monterey Bay", display="Gospel Community Church Santa Cruz", pastor="Brandon O’Sullivan"),
    dict(layer="Like-Minded Churches", pin="Grace Community Church", city="Minden", state="NV", website="https://www.gracenevada.com", region="Sierra / Tahoe", display="Grace Community Church Minden", pastor="Brian Borgman"),
    dict(layer="Like-Minded Churches", pin="Grace Bible Church of Hollister", city="Hollister", website="https://www.gracehollister.org", region="Central Coast / Monterey Bay", pastor="Michael Burchfield"),
    dict(layer="Like-Minded Churches", pin="Lighthouse Bible Church, San Jose", city="Sunnyvale", website="https://www.lbcsj.com", region="San Francisco / Peninsula / South Bay", display="Lighthouse Bible Church San Jose / Cupertino", pastor="Mark Chin"),
    dict(layer="Like-Minded Churches", pin="Crossroads Grace Community Church", city="Manteca", website="https://crossroadsgrace.org", region="Central Valley", display="Crossroads Grace Community Church Manteca", pastor="Brian Hunt"),
    dict(layer="Like-Minded Churches", pin="Newark Community Church", city="Newark", website="https://newarkcommunitychurch.org", region="East Bay", pastor="Pius Abeshi"),
    dict(layer="Like-Minded Churches", pin="Evangel Bible Church of Berkeley", city="Berkeley", website="https://www.ebcb.org", region="East Bay", pastor="John Shim"),
    dict(layer="Like-Minded Churches", pin="Higher Ground Church", city="Oakland", website="https://www.highergroundchurch.org", region="East Bay", display="Higher Ground Church Oakland", pastor="Billie Dempsey"),
    dict(layer="Like-Minded Churches", pin="Family Bible Church", city="Fairfield", website="https://www.familybible.net", region="North Bay", display="Family Bible Church Fairfield", pastor="Rich Manrique"),
    dict(layer="Like-Minded Churches", pin="Berean Baptist Church", city="Rohnert Park", website="https://bbaptist.org", region="North Bay", display="Berean Baptist Church Rohnert Park", pastor="V. Mark Smith"),
    dict(layer="Like-Minded Churches", pin="Santa Rosa Bible Church", city="Santa Rosa", website="https://srbible.org", region="North Bay", pastor="Josh Carrillo"),
    dict(layer="Like-Minded Churches", pin="Grace Pointe Church", city="Rio Vista", website="https://ubcriovista.org/", region="North Bay", pastor="Sean McDonald"),
    dict(layer="Like-Minded Churches", pin="Immanuel Baptist Church", city="Sacramento", website="https://ibcsac.org", region="Sacramento & Foothills", display="Immanuel Baptist Church Sacramento", pastor="Robert Briggs and Steve Meister"),
    dict(layer="Like-Minded Churches", pin="MT. Pleasant Baptist Church", city="Lincoln", website="https://www.mtpbclincoln.org/", region="Sacramento & Foothills", display="Mt. Pleasant Baptist Church", pastor="Adam Hatfield"),
    dict(layer="Like-Minded Churches", pin="Colfax Baptist Church", city="Colfax", website="https://www.colfaxbaptist.com/", region="Sacramento & Foothills", pastor="Gary Howard"),
    dict(layer="Like-Minded Churches", pin="Orland Evangelical Free Church", city="Orland", website="https://www.orlandefc.org/", region="North Valley", pastor="Jeff Tollison"),
    dict(layer="Like-Minded Churches", pin="Christ Community Church of Vina", city="Vina", website="https://www.christchurchvina.org/", region="North Valley", pastor="Chris Dotson"),
    dict(layer="Like-Minded Churches", pin="Grace Bible Church of Chico", city="Chico", website="https://www.gracebiblechico.com/", region="North Valley"),
    dict(layer="Like-Minded Churches", pin="Community Christian Church", city="Laytonville", website="https://www.laytonvilleccc.org/", region="North Coast", display="Community Christian Church (Laytonville)", pastor="Mike Moody"),
    dict(layer="Like-Minded Churches", pin="Grace River City Church (Hmong)", city="Sacramento", website="https://gracerivercity.org/", region="Sacramento & Foothills", display="Grace River City Church", pastor="Zong Moua"),
    dict(layer="Like-Minded Churches", pin="Iglesia Biblica de Lincoln", city="Lincoln", website="https://iglesiadelincoln.org/", region="Sacramento & Foothills", display="Iglesia Bíblica de Lincoln", pastor="Marco A. García", spanish=True),
    dict(layer="Like-Minded Churches", pin="Doxa Church", city="Rocklin", website="https://doxa.church", region="Sacramento & Foothills", display="Doxa Church Rocklin", pastor="Scott Hollingshead"),
    dict(layer="Like-Minded Churches", pin="Faith Community Church", city="Vacaville", website="https://www.vacavillefaith.org/", region="North Bay", pastor="Jon Kile"),
    dict(layer="Like-Minded Churches", pin="Lighthouse Bible Fellowship", city="Fremont", website="https://lighthousebiblefellowship.snappages.site/", region="East Bay", pastor="Craig Greatman"),
    dict(layer="Like-Minded Churches", pin="Hickman Community Church", city="Hickman", website="https://hickmanchurch.org/", region="Central Valley", pastor="Andrew Callaway"),
    dict(layer="Like-Minded Churches", pin="City Bible Church", city="Sacramento", website="https://www.citybiblesacramento.com/", region="Sacramento & Foothills", pastor="Vlad Burlaka"),
    dict(layer="Like-Minded Churches", pin="GraceHill Church", city="Citrus Heights", website="https://www.gracehillonline.org/", region="Sacramento & Foothills", pastor="Tim Vusik"),
    dict(layer="Like-Minded Churches", pin="Grace Baptist Church", city="Eureka", website="https://gbceureka.churchcenter.com/", region="North Coast", pastor="Jason Hunt"),
    dict(layer="Like-Minded Churches", pin="City Light Bible Church", city="Santa Clara", website="https://www.citylightbible.org/", region="San Francisco / Peninsula / South Bay", display="City Light Bible Church Santa Clara", pastor="Chris Gee"),
    dict(layer="Like-Minded Churches", pin="First Family Church", city="Antioch", website="https://firstfamily.us", region="East Bay", display="First Family Church Antioch", pastor="Nick Neves, Paul Abeyta, and John Williams"),
    dict(layer="Like-Minded Churches", pin="Grace Church Monterey Bay", city="Seaside", website="https://www.gracemontereybay.org", region="Central Coast / Monterey Bay", pastor="Dominic Avila"),
    dict(layer="Like-Minded Churches", pin="First Baptist Church of Monterey", city="Monterey", website="https://www.fbcmonterey.org", region="Central Coast / Monterey Bay", pastor="Josh Nichols"),
    dict(layer="Like-Minded Churches", pin="Clayton Valley Church", city="Concord", website="https://www.claytonvalleychurch.com/", region="East Bay", pastor="Chris Oliveri"),
    dict(layer="Like-Minded Churches", pin="Grace Bible Church of Cedar Ridge", city="Cedar Ridge", website="https://gracebiblecr.org/", region="Sacramento & Foothills", pastor="Chris Bogstad"),
    dict(layer="Like-Minded Churches", pin="Faith Community Church (Fremont)", city="Fremont", website="https://www.fccbay.org/", region="East Bay", display="Faith Community Church Fremont", pastor="Dan Lee"),
    dict(layer="Like-Minded Churches", pin="Grace Church of the Bay Area", city="San Mateo", website="https://www.gracebayarea.org/", region="San Francisco / Peninsula / South Bay", pastor="Roger Chen"),
    dict(layer="Like-Minded Churches", pin="Calvary Community Church", city="Knightsen", website="https://calvarytruth.org/", region="East Bay", display="Calvary Community Church Knightsen", pastor="Josh Kornoff"),
    dict(layer="Like-Minded Churches", pin="Grace Church of Orland", city="Orland", website="https://www.graceorland.org", region="North Valley", pastor="Tommy Hass"),
    dict(layer="Like-Minded Churches", pin="Silicon Valley Reformed Baptist Church", city="Sunnyvale", website="https://svrbc.org", region="San Francisco / Peninsula / South Bay", pastor="Conley Owens"),
    dict(layer="Like-Minded Churches", pin="Hillside Church", city="San Jose", website="https://www.hillside.org", region="San Francisco / Peninsula / South Bay", display="Hillside Church San Jose", pastor="Jono Burlini"),
    dict(layer="Like-Minded Churches", pin="Redeemer Bible Fellowship", city="Mountain View", website="https://redeemermv.org", region="San Francisco / Peninsula / South Bay", display="Redeemer Bible Fellowship Mountain View", pastor="Stephen Chen"),
    # Plants
    dict(layer="Church Plants - In Progress", pin="ChristChurch of the Valley", city="Vacaville", website="https://christcv.org/", region="North Bay", pastor="John Jordan"),
    dict(layer="Church Plants - In Progress", pin="Calvary Grace Church", city="Orangevale", website="https://calvarygrace.website/", region="Sacramento & Foothills", pastor="Jason Jarvis"),
    dict(layer="Church Plants - In Progress", pin="Folsom Bible Church", city="Folsom", website="https://www.folsombiblechurch.org/", region="Sacramento & Foothills", pastor="Tony Arnds and Maks Vusik"),
    dict(layer="Church Plants - In Progress", pin="Trinity Church Benicia", city="Benicia", website="https://www.trinitybenicia.com/", region="North Bay", pastor="Ryan Rippee"),
    dict(layer="Church Plants - In Progress", pin="The Shepherd's Church", city="Folsom", website="https://www.tscfolsom.org/", region="Sacramento & Foothills", pastor="Maxwell Monaghan"),
    dict(layer="Church Plants - In Progress", pin="Gospel Community Church", city="Livermore", website="https://gcclivermore.org", region="East Bay", display="Gospel Community Church Livermore", pastor="Sammy Barton"),
    dict(layer="Church Plants - In Progress", pin="Christ Bible Church", city="Sacramento", website="https://christbiblesac.churchcenter.com", region="Sacramento & Foothills", display="Christ Bible Church Sacramento", pastor="Ben Ito"),
    # Spanish — standalone congregations count as coverage; attached ministries do not
    dict(layer="Spanish Churches", pin="Iglesia del Pueblo de Dios (Tracy)", city="Tracy", website="https://iglesiadelpueblodedios.com/", region="Central Valley", display="Iglesia del Pueblo de Dios Tracy", pastor="Luis Floriano", spanish=True),
    dict(layer="Spanish Churches", pin="Iglesia del Pueblo de Dios (Lodi)", city="Lodi", website="https://iglesiadelpueblodedios.com/", region="Central Valley", display="Iglesia del Pueblo de Dios Lodi", pastor="Luis Floriano", spanish=True),
    dict(layer="Spanish Churches", pin="Iglesia del Valle Central (IVC)", city="Ceres", website="https://iglesiadelvallecentral.com/", region="Central Valley", display="Iglesia del Valle Central", pastor="Enrique Sarria", spanish=True),
    dict(layer="Spanish Churches", pin="Grace Church of the Valley – Ministerio en Español", city="Kingsburg", website="https://www.graceofthevalley.org/", region="Central Valley", display="Grace Church of the Valley Kingsburg", pastor="Jose Alcivar", spanish=True, note="Only the Spanish ministry is pinned; the English congregation is not on the map."),
    dict(layer="Spanish Churches", pin="Grace Bible Church Pleasant Hill – Servicio en Español", skip=True, skip_reason="Attached Spanish ministry of Grace Bible Church of Pleasant Hill; would double-count coverage.", merge_into="Grace Bible Church of Pleasant Hill"),
    dict(layer="Spanish Churches", pin="NorthCreek – Comunidad Bíblica Hispana", skip=True, skip_reason="Attached Spanish ministry of NorthCreek Church; would double-count coverage.", merge_into="NorthCreek Church"),
    dict(layer="Spanish Churches", pin="Hickman Community Church – Servicio en Español", skip=True, skip_reason="Attached Spanish ministry of Hickman Community Church; would double-count coverage.", merge_into="Hickman Community Church"),
    dict(layer="Spanish Churches", pin="Iglesia Bíblica Calvario de Napa", city="Napa", website="https://ibcnapa.org", region="North Bay", pastor="Arturo Solorzano", spanish=True, note="Meets at Grace Church of Napa Valley."),
]

# Tracked on the heat map but not on the Coalition like-minded layers.
# Does not count as coverage and does not close gaps.
ADJACENT_SUPPLEMENTS = [
    dict(
        name="Windsor Christian Church",
        city="Windsor",
        state="CA",
        pastor="Lance Wallace",
        website="https://www.windsorchristianchurch.com/",
        lat=38.5617155,
        lon=-122.8270463,
        affiliation_signals=["GARBC / Regular Baptist roots; explore"],
        status="adjacent_explore",
        coord_source="existing plant-scout inventory",
        region="North Bay",
        note="Formerly First Baptist Church of Windsor. Adjacent / explore — not treated as like-minded coverage.",
    )
]

ALIASES = {
    "capilla calvario de napa": "iglesia biblica calvario de napa",
    "elk grove bible church (now redeemer bible church)": "redeemer bible church elk grove",
    "elk grove bible church": "redeemer bible church elk grove",
}


def text(el) -> str:
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def haversine(lat1, lon1, lat2, lon2) -> float:
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def norm_name(name: str) -> str:
    s = (name or "").casefold()
    s = s.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    s = s.replace("ñ", "n").replace("’", "'").replace("–", "-").replace("—", "-")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = ALIASES.get(s, s)
    for prefix in ("the ",):
        if s.startswith(prefix):
            s = s[len(prefix):]
    return s


def website_from_desc(desc: str) -> str:
    if not desc:
        return ""
    m = URL_RE.search(desc)
    return m.group(0).rstrip(".;,)") if m else ""


def clean_pastor(raw: str) -> str:
    if not raw:
        return ""
    s = re.sub(r"<[^>]+>", " ", raw)
    s = s.replace("&amp;", "&").replace("&nbsp;", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"^(lead\s+)?pastor\s*:?\s+", "", s, flags=re.I)
    s = re.sub(r"^senior pastor\s*:?\s+", "", s, flags=re.I)
    # stop at pipe / website / email
    s = re.split(r"\s*\|\s*|\s+https?://|\s+\S+@\S+", s, maxsplit=1)[0].strip()
    s = s.strip(" .;,-")
    labels = {
        "tbd", "n/a", "none", "pastor", "fellowship", "fellowship:",
        "denomination", "denomination:", "description", "description:",
        "website", "website:", "sending church", "start date",
    }
    if s.lower() in labels or s.lower().rstrip(":") in labels:
        return ""
    return s


def pastor_from_desc(desc: str) -> str:
    if not desc:
        return ""
    plain = re.sub(r"<br\s*/?>", "\n", desc, flags=re.I)
    plain = re.sub(r"<[^>]+>", " ", plain)
    plain = plain.replace("&amp;", "&").replace("&nbsp;", " ")
    # Prefer labelled fields; ignore empty placeholders like "Senior Pastor: <br>Fellowship:"
    for pat in (
        r"Senior Pastor:\s*([^\n|]+)",
        r"Spanish Pastor:\s*([^\n|]+)",
        r"(?<![A-Za-z])Pastor:\s*([^\n|]+)",
    ):
        m = re.search(pat, plain)
        if m:
            val = clean_pastor(m.group(1))
            if val:
                return val
    m = re.search(
        r"Pastor\s+([A-Z][A-Za-z.'’\-]+(?:\s+[A-Z][A-Za-z.'’\-]+){0,3})",
        plain,
    )
    if m:
        parts = []
        stop = {
            "senior", "pastor", "fellowship", "denomination", "website",
            "sundays", "sunday", "phone", "sending", "start", "description",
            "lead",
        }
        for word in m.group(1).split():
            if word.lower().rstrip(":") in stop:
                break
            parts.append(word)
        return clean_pastor(" ".join(parts))
    return ""


def parse_kml(source: Path | None) -> tuple[list[dict], bytes]:
    if source:
        raw = source.read_bytes()
    else:
        req = urllib.request.Request(
            KML_URL,
            headers={"User-Agent": "CoalitionCEC-PlantScout/1.0"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
    # Google sometimes wraps KML in a kmz-like zip; this endpoint is forcekml=1
    root = ET.fromstring(raw)
    pins = []
    doc = root.find("k:Document", NS)
    if doc is None:
        doc = root
    for folder in doc.findall("k:Folder", NS):
        layer = text(folder.find("k:name", NS))
        for pm in folder.findall("k:Placemark", NS):
            name = text(pm.find("k:name", NS))
            desc = text(pm.find("k:description", NS))
            ext = {}
            for data in pm.findall(".//k:Data", NS):
                ext[data.get("name") or ""] = text(data.find("k:value", NS))
            coord = text(pm.find(".//k:coordinates", NS))
            lon = lat = None
            if coord:
                parts = coord.split(",")
                if len(parts) >= 2:
                    lon, lat = float(parts[0]), float(parts[1])
            pins.append(
                {
                    "layer": layer,
                    "name": name,
                    "desc": desc,
                    "ext": ext,
                    "lon": lon,
                    "lat": lat,
                }
            )
    return pins, raw


def find_meta(pin: dict) -> dict | None:
    cands = [m for m in PIN_META if m["layer"] == pin["layer"] and m["pin"] == pin["name"]]
    if not cands:
        return None
    if len(cands) == 1 and "lat" not in cands[0]:
        return cands[0]
    if pin["lat"] is None:
        return cands[0]
    best, best_d = None, 1e9
    for m in cands:
        if "lat" in m:
            d = haversine(m["lat"], m["lon"], pin["lat"], pin["lon"])
        else:
            d = 0.0
        if d < best_d:
            best, best_d = m, d
    if best is not None and best_d <= 5.0:
        return best
    return best if len(cands) == 1 else None


def load_roster_enrichment() -> list[dict]:
    """Optional city/website/pastor hints from the Coalition church list."""
    candidates = [
        Path("/workspace/coalition-map-list/churches-by-region.md"),
        DIR.parent / "coalition-map-list" / "churches-by-region.md",
    ]
    path = next((p for p in candidates if p.exists()), None)
    if not path:
        return []
    rows = []
    line_re = re.compile(
        r"^- \[([^\]]+)\]\(([^)]+)\) — ([^·]+?)(?: \([^)]+\))? · (.+)$"
    )
    for line in path.read_text(encoding="utf-8").splitlines():
        m = line_re.match(line.strip())
        if not m:
            continue
        name, url, city, pastor = m.group(1), m.group(2), m.group(3).strip(), m.group(4).strip()
        city = re.sub(r", NV$", "", city).strip()
        rows.append({"name": name, "website": url, "city": city, "pastor": pastor})
    return rows


def enrich_pastor(church: dict, roster: list[dict], kml_pastor: str) -> str:
    # Prefer a non-empty KML Senior Pastor / description, else roster, else meta.
    if kml_pastor:
        return kml_pastor
    web = (church.get("website") or "").rstrip("/").lower()
    n = norm_name(church["name"])
    city = (church.get("city") or "").casefold()
    for r in roster:
        rweb = (r["website"] or "").rstrip("/").lower()
        if web and rweb and web == rweb and r["pastor"]:
            # same site can serve two campuses (Iglesia del Pueblo Tracy/Lodi)
            val = clean_pastor(r["pastor"])
            if not val:
                continue
            if "iglesia del pueblo" in n:
                if r["city"].casefold() == city:
                    return val
                continue
            return val
    for r in roster:
        val = clean_pastor(r["pastor"])
        if norm_name(r["name"]) == n and r["city"].casefold() == city and val:
            return val
    return clean_pastor(church.get("pastor") or "")


def build_churches(pins: list[dict], roster: list[dict]) -> tuple[list[dict], list[dict], list[str]]:
    warnings: list[str] = []
    skipped: list[dict] = []
    churches: list[dict] = []
    fortuna_seen = False

    for pin in pins:
        if pin["layer"] not in INCLUDE_LAYERS:
            continue
        if pin["lat"] is None or pin["lon"] is None:
            warnings.append(f"No coordinates for {pin['layer']}: {pin['name']}")
            continue
        meta = find_meta(pin)
        if meta and meta.get("skip"):
            skipped.append(
                {
                    "pin": pin["name"],
                    "layer": pin["layer"],
                    "reason": meta.get("skip_reason"),
                    "merge_into": meta.get("merge_into"),
                }
            )
            continue
        if pin["name"] == "First Baptist Church of Fortuna":
            if fortuna_seen:
                skipped.append(
                    {
                        "pin": pin["name"],
                        "layer": pin["layer"],
                        "reason": "Duplicate pin at the same Fortuna coordinates.",
                        "merge_into": "First Baptist Church of Fortuna",
                    }
                )
                continue
            fortuna_seen = True
        if meta is None:
            warnings.append(
                f"No metadata for {pin['layer']}: {pin['name']} "
                f"({pin['lat']},{pin['lon']}) — included with KML fields only. "
                "Add a PIN_META row."
            )
            meta = {
                "city": "",
                "website": website_from_desc(pin["desc"]),
                "region": "",
                "display": pin["name"],
            }

        kml_pastor = clean_pastor(
            pin["ext"].get("Senior Pastor") or pin["ext"].get("Pastor") or ""
        ) or pastor_from_desc(pin["desc"])
        status = (
            "plant_in_progress"
            if pin["layer"] == "Church Plants - In Progress"
            else "established"
        )
        church = {
            "name": meta.get("display") or pin["name"],
            "city": meta.get("city") or "",
            "state": meta.get("state") or ("NV" if (meta.get("city") or "").endswith(", NV") else "CA"),
            "pastor": meta.get("pastor") or "",
            "website": meta.get("website") or website_from_desc(pin["desc"]) or "",
            "lat": pin["lat"],
            "lon": pin["lon"],
            "affiliation_signals": ["CoalitionCEC map"],
            "status": status,
            "coord_source": "Coalition My Map KML",
            "region": meta.get("region") or "",
            "pin_name": pin["name"],
            "layer": pin["layer"],
            "home": bool(meta.get("home") or pin["name"] == HOME_BASE["name"]),
        }
        if meta.get("spanish"):
            church["spanish"] = True
        if meta.get("note"):
            church["note"] = meta["note"]
        church["pastor"] = enrich_pastor(church, roster, kml_pastor) or church["pastor"]
        # Normalize city "Minden, NV"
        if church["city"].endswith(", NV"):
            church["city"] = church["city"].replace(", NV", "").strip()
            church["state"] = "NV"
        churches.append(church)

    for adj in ADJACENT_SUPPLEMENTS:
        churches.append(dict(adj))

    churches.sort(key=lambda c: (c["name"].casefold(), c["city"].casefold()))
    return churches, skipped, warnings


def coverage_churches(churches: list[dict]) -> list[dict]:
    return [
        c
        for c in churches
        if c["status"] in {"established", "plant_in_progress"} and c.get("lat") is not None
    ]


def nearest(lat, lon, pool: list[dict]) -> tuple[dict | None, float]:
    best, best_d = None, 1e9
    for c in pool:
        d = haversine(lat, lon, c["lat"], c["lon"])
        if d < best_d:
            best, best_d = c, d
    return best, best_d


def nearby_count(lat, lon, pool: list[dict], radius=40.0) -> int:
    return sum(1 for c in pool if haversine(lat, lon, c["lat"], c["lon"]) <= radius)


def distance_score(miles: float, area: str) -> float:
    if area == "Davis":
        return 22  # forced high: Coalition "Needs a Church Planter" pin
    if miles >= 50:
        return 25
    if miles >= 40:
        return 24
    if miles >= 30:
        return 22
    if miles >= 25:
        return 18
    if miles >= 20:
        return 14
    if miles >= 15:
        return 10
    if miles >= 8:
        return 6
    return 2


def vacuum_score(nearby: int) -> float:
    if nearby <= 0:
        return 15
    if nearby == 1:
        return 12
    if nearby <= 5:
        return 8
    return 4


def refresh_gaps(gaps: list[dict], pool: list[dict]) -> tuple[list[dict], list[dict]]:
    kept, dropped = [], []
    for g in gaps:
        g = dict(g)
        church, dist = nearest(g["lat"], g["lon"], pool)
        if church is None:
            kept.append(g)
            continue
        g["nearest_church"] = church["name"]
        g["nearest_city"] = church["city"]
        g["distance_miles"] = round(dist, 1)
        g["nearby_like_minded_40mi"] = nearby_count(g["lat"], g["lon"], pool)
        g["distance_score"] = distance_score(g["distance_miles"], g["area"])
        g["vacuum_score"] = vacuum_score(g["nearby_like_minded_40mi"])
        parts = (
            g.get("pop_score", 0)
            + g["distance_score"]
            + g.get("growth_score", 0)
            + g["vacuum_score"]
            + g.get("napa_score", 0)
        )
        g["need_score"] = round(float(parts), 1)
        if g.get("distance_to_napa_miles") is None:
            g["distance_to_napa_miles"] = round(
                haversine(g["lat"], g["lon"], HOME_BASE["lat"], HOME_BASE["lon"]), 1
            )
        if g["area"] != "Davis" and g["distance_miles"] < COVERED_MILES:
            dropped.append(g)
            continue
        kept.append(g)
    kept.sort(key=lambda x: (-x["need_score"], x["area"]))
    return kept, dropped


def match_diff(old: list[dict], new: list[dict]) -> dict:
    old_left = list(old)
    new_left = list(new)
    paired = []

    def take(o_idx, n_idx):
        o = old_left.pop(o_idx)
        n = new_left.pop(n_idx)
        paired.append((o, n))

    # 1) same normalized name first. Old inventory sometimes colocated
    #    two churches at one pin, so coord-first matching swapped identities.
    for o in list(old_left):
        on = norm_name(o["name"])
        oi = old_left.index(o)
        hits = [j for j, n in enumerate(new_left) if norm_name(n["name"]) == on]
        if not hits:
            continue
        if len(hits) == 1:
            take(oi, hits[0])
            continue
        # Disambiguate same-name pins by city, then nearest coords
        ocity = (o.get("city") or "").casefold()
        city_hits = [j for j in hits if (new_left[j].get("city") or "").casefold() == ocity]
        use = city_hits or hits
        best_j, best_d = use[0], 1e9
        for j in use:
            d = haversine(o["lat"], o["lon"], new_left[j]["lat"], new_left[j]["lon"])
            if d < best_d:
                best_j, best_d = j, d
        take(oi, best_j)

    # 2) remaining close-coord matches (renames at the same place)
    for o in list(old_left):
        oi = old_left.index(o)
        best_j, best_d = None, 1e9
        for j, n in enumerate(new_left):
            d = haversine(o["lat"], o["lon"], n["lat"], n["lon"])
            if d < best_d:
                best_j, best_d = j, d
        if best_j is not None and best_d <= MOVED_MILES:
            take(oi, best_j)

    # 3) loose coord match (up to 25 mi) + similar name tokens, for big moves
    for o in list(old_left):
        oi = old_left.index(o)
        on = set(norm_name(o["name"]).split())
        best_j, best_d = None, 1e9
        for j, n in enumerate(new_left):
            nn = set(norm_name(n["name"]).split())
            if not on or not nn:
                continue
            overlap = len(on & nn) / len(on | nn)
            d = haversine(o["lat"], o["lon"], n["lat"], n["lon"])
            if overlap >= 0.5 and d < 25 and d < best_d:
                best_j, best_d = j, d
        if best_j is not None:
            take(oi, best_j)

    added = new_left
    removed = old_left
    renamed, moved, status_changed, otherwise = [], [], [], []
    for o, n in paired:
        d = haversine(o["lat"], o["lon"], n["lat"], n["lon"])
        name_changed = o["name"] != n["name"]
        moved_flag = d >= MOVED_MILES
        rec = {
            "from": o["name"],
            "to": n["name"],
            "city": n.get("city") or o.get("city"),
            "miles": round(d, 2),
            "old": (o["lat"], o["lon"]),
            "new": (n["lat"], n["lon"]),
            "old_status": o.get("status"),
            "new_status": n.get("status"),
            "old_pastor": o.get("pastor") or "",
            "new_pastor": n.get("pastor") or "",
        }
        if name_changed:
            renamed.append(rec)
        if moved_flag:
            moved.append(rec)
        if o.get("status") != n.get("status"):
            status_changed.append(rec)
        if not name_changed and not moved_flag and o.get("status") == n.get("status"):
            otherwise.append(rec)
    return {
        "added": added,
        "removed": removed,
        "renamed": renamed,
        "moved": moved,
        "status_changed": status_changed,
        "paired": paired,
    }


def map_payload(churches: list[dict]) -> list[dict]:
    out = []
    for c in churches:
        if c["status"] == "weak_public_presence":
            continue  # never plot Weak Presence
        out.append(
            {
                "name": c["name"],
                "city": c["city"],
                "lat": c["lat"],
                "lon": c["lon"],
                "pastor": c["pastor"],
                "website": c.get("website") or "",
                "status": c["status"],
                "home": bool(c.get("home")),
            }
        )
    return out


def map_gap_payload(gaps: list[dict]) -> list[dict]:
    out = []
    for i, g in enumerate(gaps, 1):
        out.append(
            {
                "rank": i,
                "area": g["area"],
                "lat": g["lat"],
                "lon": g["lon"],
                "need_score": g["need_score"],
                "population_est": g["population_est"],
                "nearest_church": g["nearest_church"],
                "distance_miles": g["distance_miles"],
                "opportunity_type": g["opportunity_type"],
            }
        )
    return out


def patch_map_html(template: str, churches: list[dict], gaps: list[dict], stamp: str) -> str:
    html = template
    ch_js = json.dumps(map_payload(churches), ensure_ascii=False)
    gp_js = json.dumps(map_gap_payload(gaps), ensure_ascii=False)
    html, n1 = re.subn(
        r"const churches = \[.*?\];",
        "const churches = " + ch_js + ";",
        html,
        count=1,
        flags=re.S,
    )
    html, n2 = re.subn(
        r"const gaps = \[.*?\];",
        "const gaps = " + gp_js + ";",
        html,
        count=1,
        flags=re.S,
    )
    html, n3 = re.subn(
        r"(?:First-pass scout|Updated)(?: ·)? [^<]+",
        f"Updated {stamp} PT",
        html,
        count=1,
    )
    if n1 != 1 or n2 != 1 or n3 != 1:
        raise RuntimeError(f"Failed to patch map HTML (churches={n1}, gaps={n2}, date={n3})")
    # Guardrails: styling / tiles must stay OSM, no Weak Presence legend
    if "tile.openstreetmap.org" not in html:
        raise RuntimeError("Map HTML lost OpenStreetMap tiles")
    if re.search(r"cartocdn|basemaps\.cartocdn", html, re.I):
        raise RuntimeError("Map HTML unexpectedly references CARTO tiles")
    if re.search(r"Weak presence|weak_public_presence", html):
        # status string may still appear if a church slipped in; payload already filters
        if "Weak presence" in html:
            raise RuntimeError("Map HTML still has a Weak presence legend")
    return html


def write_gaps_csv(path: Path, gaps: list[dict]) -> None:
    fields = [
        "rank",
        "area",
        "lat",
        "lon",
        "need_score",
        "population_est",
        "nearest_church",
        "nearest_city",
        "distance_miles",
        "distance_to_napa_miles",
        "opportunity_type",
        "nearby_like_minded_40mi",
        "pop_score",
        "distance_score",
        "growth_score",
        "vacuum_score",
        "napa_score",
        "notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for i, g in enumerate(gaps, 1):
            row = dict(g)
            row["rank"] = i
            w.writerow(row)


def write_gaps_ranked(path: Path, gaps: list[dict], stamp: str, n_churches: int) -> None:
    plants = [
        "ChristChurch of the Valley (Vacaville)",
        "Calvary Grace (Orangevale)",
        "Folsom Bible Church",
        "Trinity Church Benicia",
        "The Shepherd's Church (Folsom)",
        "Gospel Community Church (Livermore)",
    ]
    lines = [
        "# Ranked church-planting gap areas — Northern California",
        "",
        "**Home base:** Grace Church of Napa Valley (Napa, CA)  ",
        f"**Generated:** {stamp} (PT)  ",
        f"**Like-minded set:** Coalition My Map (Like-Minded + Church Plants + standalone Spanish congregations); {n_churches} coverage pins. See `churches.json`.  ",
        "**Gap radius:** ~18 miles primary; large cities (≥50k) flagged from ~12+ miles if no in-city church. Gaps with a like-minded church within 5 miles are dropped (except Davis, which stays as the Coalition “Needs a Church Planter” pin).",
        "",
        "## Scoring method (transparent)",
        "",
        "| Factor | Max pts | What it measures |",
        "|---|---:|---|",
        "| Population / metro size | 30 | Larger gap towns score higher |",
        "| Distance to nearest like-minded church | 25 | Miles beyond coverage; Davis forced high (map pin) |",
        "| Population growth / housing | 15 | Rough growth index 0–10 × 1.5 |",
        "| Like-minded vacuum (≤40 mi count) | 15 | Fewer nearby Coalition churches → higher |",
        "| Proximity to Napa (shepherding bonus) | 15 | Closer to home base → higher |",
        "| **Total** | **100** | |",
        "",
        "**Opportunity types**",
        "- **A_send_pastor** — plausible existing like-minded families / commute pattern; send pastor to gather a plant",
        "- **B_evangelism_first** — large population / thin gospel density; evangelism with future plant hope",
        "- **mixed_or_explore** — needs local intel",
        "",
        "**Not greenfield gaps**",
        f"- Plants in progress count as coverage: {', '.join(plants)}.",
        "- Adjacent / explore pins (such as Windsor Christian Church) are tracked separately and do not close gaps.",
        "- Attached Spanish ministries of an English church are not counted as a second coverage pin. Standalone Spanish congregations are counted as coverage.",
        "- **Davis** remains ranked even with nearby Sacramento churches, because of the Coalition “Needs a Church Planter” pin.",
        "",
        "---",
        "",
        "## Top ranked gaps",
        "",
    ]
    for i, g in enumerate(gaps, 1):
        lines += [
            f"### {i}. {g['area']} — need_score **{g['need_score']}**",
            "",
            f"- **Population (est.):** {g['population_est']:,}",
            f"- **Nearest like-minded:** {g['nearest_church']} ({g['nearest_city']}), {g['distance_miles']} mi",
            f"- **Like-minded within 40 mi:** {g['nearby_like_minded_40mi']}",
            f"- **Distance to Napa:** {g.get('distance_to_napa_miles', '')} mi",
            f"- **Opportunity type:** {g['opportunity_type']}",
            f"- **Score parts:** pop {g.get('pop_score', '')} + distance {g['distance_score']} + growth {g.get('growth_score', '')} + vacuum {g['vacuum_score']} + Napa {g.get('napa_score', '')}",
        ]
        if g.get("notes"):
            lines.append(f"- **Notes:** {g['notes']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def format_diff(diff: dict, dropped_gaps: list[dict], warnings: list[str], skipped: list[dict], stamp: str) -> str:
    lines = [f"# Plant scout sync report — {stamp} PT", ""]

    def church_line(c):
        return f"- {c['name']} — {c.get('city','')} ({c.get('status','')}) {c.get('lat')},{c.get('lon')}"

    lines.append(f"## Added ({len(diff['added'])})")
    lines += [church_line(c) for c in diff["added"]] or ["- (none)"]
    lines += ["", f"## Removed ({len(diff['removed'])})"]
    lines += [church_line(c) for c in diff["removed"]] or ["- (none)"]
    lines += ["", f"## Renamed ({len(diff['renamed'])})"]
    if diff["renamed"]:
        for r in diff["renamed"]:
            lines.append(f"- {r['from']} → {r['to']} ({r['city']})")
    else:
        lines.append("- (none)")
    lines += ["", f"## Moved ≥ {MOVED_MILES} mi ({len(diff['moved'])})"]
    if diff["moved"]:
        for r in diff["moved"]:
            lines.append(
                f"- {r['to']} ({r['city']}): {r['miles']} mi "
                f"from {r['old'][0]:.6f},{r['old'][1]:.6f} "
                f"to {r['new'][0]:.6f},{r['new'][1]:.6f}"
            )
    else:
        lines.append("- (none)")
    lines += ["", f"## Status changes ({len(diff['status_changed'])})"]
    if diff["status_changed"]:
        for r in diff["status_changed"]:
            lines.append(f"- {r['to']}: {r['old_status']} → {r['new_status']}")
    else:
        lines.append("- (none)")
    pastor_fixes = [
        r
        for r in (diff["renamed"] + diff["moved"] + [ {"from": a["name"], "to": b["name"], "old_pastor": a.get("pastor") or "", "new_pastor": b.get("pastor") or "", "city": b.get("city")} for a,b in diff["paired"] ])
        if False
    ]
    # pastor changes among paired
    lines += ["", "## Pastor updates"]
    pcount = 0
    for a, b in diff["paired"]:
        old_p, new_p = (a.get("pastor") or "").strip(), (b.get("pastor") or "").strip()
        if old_p != new_p:
            lines.append(f"- {b['name']} ({b.get('city')}): “{old_p}” → “{new_p}”")
            pcount += 1
    if pcount == 0:
        lines.append("- (none)")
    lines += ["", f"## Gaps now covered (< {COVERED_MILES} mi, dropped from ranked list)"]
    if dropped_gaps:
        for g in dropped_gaps:
            lines.append(
                f"- {g['area']}: nearest {g['nearest_church']} ({g['nearest_city']}), {g['distance_miles']} mi"
            )
    else:
        lines.append("- (none)")
    lines += ["", "## Skipped KML pins"]
    if skipped:
        for s in skipped:
            extra = f" (merged into {s['merge_into']})" if s.get("merge_into") else ""
            lines.append(f"- {s['pin']} [{s['layer']}]: {s.get('reason')}{extra}")
    else:
        lines.append("- (none)")
    if warnings:
        lines += ["", "## Warnings"]
        lines += [f"- {w}" for w in warnings]
    lines.append("")
    return "\n".join(lines)


def strip_internal(churches: list[dict]) -> list[dict]:
    out = []
    for c in churches:
        row = {
            "name": c["name"],
            "city": c["city"],
            "state": c.get("state") or "CA",
            "pastor": c.get("pastor") or "",
            "website": c.get("website") or "",
            "lat": c["lat"],
            "lon": c["lon"],
            "affiliation_signals": c.get("affiliation_signals") or ["CoalitionCEC map"],
            "status": c["status"],
            "coord_source": c.get("coord_source") or "Coalition My Map KML",
            "region": c.get("region") or "",
        }
        if c.get("home"):
            row["home"] = True
        if c.get("spanish"):
            row["spanish"] = True
        if c.get("note"):
            row["note"] = c["note"]
        out.append(row)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kml", type=Path, help="Local KML path (skip fetch)")
    ap.add_argument("--dry-run", action="store_true", help="Print diff; do not write files")
    args = ap.parse_args()

    stamp = date.today().isoformat()
    old_path = DIR / "churches.json"
    old_data = json.loads(old_path.read_text(encoding="utf-8")) if old_path.exists() else {"churches": []}
    old_churches = old_data.get("churches") or []

    pins, raw = parse_kml(args.kml)
    roster = load_roster_enrichment()
    churches, skipped, warnings = build_churches(pins, roster)

    pool = coverage_churches(churches)
    curated_in = json.loads((DIR / "gaps_curated.json").read_text(encoding="utf-8"))
    full_in = json.loads((DIR / "gaps_full.json").read_text(encoding="utf-8"))
    curated, dropped_curated = refresh_gaps(curated_in, pool)
    full, dropped_full = refresh_gaps(full_in, pool)
    # Re-rank already done; expose rank
    for i, g in enumerate(curated, 1):
        g["rank"] = i
    for i, g in enumerate(full, 1):
        g["rank"] = i

    coverage_only = [c for c in churches if c["status"] in {"established", "plant_in_progress"}]
    plants = [c["name"] for c in churches if c["status"] == "plant_in_progress"]

    new_data = {
        "meta": {
            "generated": stamp,
            "home_base": HOME_BASE["name"],
            "home_base_city": HOME_BASE["city"],
            "home_base_lat": HOME_BASE["lat"],
            "home_base_lon": HOME_BASE["lon"],
            "source": "CoalitionCEC Google My Map KML (Like-Minded + Church Plants + standalone Spanish)",
            "kml_url": KML_URL,
            "like_minded_definition": "CoalitionCEC circle OR TMS/9Marks/MacArthur-aligned (expository, elder-led, Doctrines of Grace, Solas, ACBC-friendly, complementarian, generally cessationist)",
            "count": len(churches),
            "coverage_count": len(coverage_only),
            "radius_miles_for_gap": 18,
            "confidence": "Synced from the live Coalition My Map; pastors/websites enriched from the Coalition church list when the KML field is empty.",
            "notes": (
                "Hartstone Bible Camp excluded. Attached Spanish ministries of an English church "
                "are not plotted as a second pin. No Weak Presence category. "
                "Windsor Christian Church is adjacent_explore and does not count as coverage. "
                "Patterson Bible Church is omitted unless it reappears on the My Map."
            ),
        },
        "churches": strip_internal(churches),
        "plants_in_progress": plants,
        "weak_presence_notes": [],
    }

    diff = match_diff(old_churches, new_data["churches"])
    report = format_diff(diff, dropped_curated, warnings, skipped, stamp)
    print(report)
    print(f"Inventory: {len(churches)} pins ({len(coverage_only)} coverage, "
          f"{sum(1 for c in churches if c['status']=='plant_in_progress')} plants, "
          f"{sum(1 for c in churches if c['status']=='adjacent_explore')} adjacent).")
    print(f"Ranked gaps: {len(curated)} (dropped {len(dropped_curated)} now covered).")

    if args.dry_run:
        print("\nDry run — no files written.")
        return 0

    (DIR / "live-map.kml").write_bytes(raw)
    (DIR / "churches.json").write_text(json.dumps(new_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (DIR / "gaps_curated.json").write_text(json.dumps(curated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (DIR / "gaps_full.json").write_text(json.dumps(full, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_gaps_csv(DIR / "gaps.csv", curated)
    write_gaps_ranked(DIR / "gaps-ranked.md", curated, stamp, len(coverage_only))
    (DIR / "last-sync-report.md").write_text(report, encoding="utf-8")

    template = (DIR / "map.html").read_text(encoding="utf-8")
    html = patch_map_html(template, churches, curated, stamp)
    for dest in (DIR / "map.html", DIR / "index.html", DIR / "public" / "index.html"):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")

    print(f"\nWrote churches.json, map.html, index.html, public/index.html, gaps.*, last-sync-report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
