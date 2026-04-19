"""
Global Fishing Watch data utilities.

Fetches purse seiner fishing effort from the GFW 4wings API.
Results are cached in-process so the dashboard never hammers the API.
"""

import os
import requests
import streamlit as st

try:
    import streamlit as _st
    GFW_TOKEN = _st.secrets.get("GFW_TOKEN", os.environ.get("GFW_TOKEN", ""))
except Exception:
    GFW_TOKEN = os.environ.get("GFW_TOKEN", "")
_BASE = "https://gateway.api.globalfishingwatch.org/v3/4wings/report"

# California Current bounding box (lon, lat order for GeoJSON)
_CA_BOX = [[-126, 30], [-116, 30], [-116, 42], [-126, 42], [-126, 30]]

# GEA closure polygons in GeoJSON (lon, lat) order
CLOSURE_COORDS = {
    "Hidden Reef":    [[-119.174,33.769],[-119.099,33.769],[-119.099,33.690],[-119.174,33.690],[-119.174,33.769]],
    "W. SB Island":   [[-119.309,33.561],[-119.126,33.561],[-119.126,33.465],[-119.309,33.465],[-119.309,33.561]],
    "Potato Bank":    [[-119.883,33.350],[-119.761,33.350],[-119.761,33.183],[-119.883,33.183],[-119.883,33.350]],
    "107/118 Bank":   [[-119.688,33.092],[-119.612,33.144],[-119.528,33.058],[-119.605,33.006],[-119.688,33.092]],
    "Cherry Bank":    [[-119.490,32.848],[-119.330,32.949],[-119.296,32.912],[-119.456,32.810],[-119.490,32.848]],
    "Seamount 109":   [[-119.617,32.729],[-119.572,32.729],[-119.449,32.533],[-119.495,32.508],[-119.617,32.659],[-119.617,32.729]],
    "43-Fathom Spot": [[-118.001,32.700],[-117.833,32.700],[-117.833,32.612],[-117.838,32.603],[-118.001,32.603],[-118.001,32.700]],
    "Northeast Bank": [[-119.617,32.457],[-119.527,32.457],[-119.527,32.333],[-119.617,32.333],[-119.617,32.457]],
    "Sur Ridge":      [[-122.347,36.433],[-122.254,36.426],[-122.255,36.362],[-122.286,36.299],[-122.278,36.274],[-122.346,36.274],[-122.347,36.433]],
    "Cordell Bank":   [[-123.346,38.053],[-123.417,38.105],[-123.489,38.106],[-123.522,38.076],[-123.518,38.039],[-123.473,38.000],[-123.444,37.968],[-123.447,37.918],[-123.385,38.000],[-123.346,38.053]],
}

# Pre-collected data (no API calls needed at runtime)
CACHED_ANNUAL_EFFORT = {
    2012: 0.0, 2013: 0.0, 2014: 4.66, 2015: 0.0,
    2016: 164.28, 2017: 307.63, 2018: 198.02,
    2019: 108.41, 2020: 43.83, 2021: 0.0, 2022: 58.01,
}

CACHED_CLOSURE_EFFORT = {
    "Hidden Reef": 0.0, "W. SB Island": 0.0, "Potato Bank": 0.0,
    "107/118 Bank": 0.0, "Cherry Bank": 0.0, "Seamount 109": 0.0,
    "43-Fathom Spot": 0.0, "Northeast Bank": 0.0,
    "Sur Ridge": 0.0, "Cordell Bank": 0.0,
}


def _gfw_headers():
    return {"Authorization": f"Bearer {GFW_TOKEN}", "Content-Type": "application/json"}


def _fetch_effort(coords, year):
    """Single API call: annual purse seiner hours inside a polygon."""
    r = requests.post(
        _BASE,
        params={
            "datasets[0]": "public-global-fishing-effort:latest",
            "date-range": f"{year}-01-01,{year}-12-31",
            "filters[0]": "geartype IN ('purse_seines')",
            "spatial-aggregation": "true",
            "spatial-resolution": "HIGH",
            "temporal-resolution": "YEARLY",
            "format": "JSON",
            "group-by": "GEARTYPE",
        },
        headers=_gfw_headers(),
        json={"geojson": {"type": "Feature", "properties": {}, "geometry": {
            "type": "Polygon", "coordinates": [coords]
        }}},
        timeout=15,
    )
    if r.status_code != 200:
        return 0.0
    hours = 0.0
    for e in (r.json().get("entries") or []):
        for ds_data in e.values():
            for row in (ds_data or []):
                hours += row.get("hours", 0)
    return round(hours, 2)


@st.cache_data(ttl=3600)
def get_annual_effort():
    """Returns {year: fishing_hours} for purse seiners in CA Current."""
    if not GFW_TOKEN:
        return CACHED_ANNUAL_EFFORT
    try:
        result = {}
        for yr in range(2012, 2023):
            result[yr] = _fetch_effort(_CA_BOX, yr)
        return result
    except Exception:
        return CACHED_ANNUAL_EFFORT


@st.cache_data(ttl=3600)
def get_closure_effort():
    """Returns {closure_name: total_fishing_hours_2016_2022}."""
    if not GFW_TOKEN:
        return CACHED_CLOSURE_EFFORT
    try:
        result = {}
        for name, coords in CLOSURE_COORDS.items():
            total = sum(_fetch_effort(coords, yr) for yr in range(2016, 2023))
            result[name] = round(total, 2)
        return result
    except Exception:
        return CACHED_CLOSURE_EFFORT
