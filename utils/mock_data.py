"""
Mock data generators for the Anchovy Conservation Dashboard.

Produces synthetic habitat suitability grids, incidental coverage time-series,
and scenario-modified grids. All generators are deterministic (seeded) so the
UI is reproducible during development. Once the real ML pipeline is connected,
replace calls to these functions with actual model outputs.
"""

import numpy as np
import pandas as pd
from utils.constants import (
    LAT_MIN, LAT_MAX, LON_MIN, LON_MAX,
    GRID_RESOLUTION, YEAR_MIN, YEAR_MAX,
    KEY_EVENTS,
)

_RNG = np.random.default_rng(42)


def _coastal_proximity(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """
    Rough proxy for distance to shore.  Higher values = closer to coast.
    Uses a simplistic polynomial approximation of the California coastline.
    """
    # Very rough coastline longitude as a function of latitude
    coast_lon = -117.0 - 0.15 * (lat - 32.0) - 0.005 * (lat - 32.0) ** 2
    dist = np.abs(lon - coast_lon)
    proximity = np.exp(-dist / 2.0)
    return proximity


def generate_habitat_grid(year: int) -> pd.DataFrame:
    """
    Generate a 0.5° habitat suitability grid for a given year.

    Returns a DataFrame with columns: lat, lon, suitability (0-1).
    Suitability is higher near the coast and influenced by a pseudo-
    temperature cycle and random noise.
    """
    lats = np.arange(LAT_MIN, LAT_MAX, GRID_RESOLUTION)
    lons = np.arange(LON_MIN, LON_MAX, GRID_RESOLUTION)
    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")
    lat_flat = lat_grid.ravel()
    lon_flat = lon_grid.ravel()

    # Base suitability from coastal proximity
    base = _coastal_proximity(lat_flat, lon_flat)

    # Latitudinal preference peaking around 33–36°N
    lat_pref = np.exp(-0.5 * ((lat_flat - 34.5) / 3.0) ** 2)

    # Year-dependent modulation (simulate crash 2009-2011)
    year_effect = 1.0
    if 2009 <= year <= 2011:
        year_effect = 0.15 + 0.1 * (year - 2009)
    elif 2012 <= year <= 2015:
        year_effect = 0.5 + 0.1 * (year - 2012)
    elif year >= 2016:
        year_effect = 0.7 + 0.02 * min(year - 2016, 5)

    # Combine
    suitability = base * lat_pref * year_effect
    noise = _RNG.normal(0, 0.05, size=suitability.shape)
    suitability = np.clip(suitability + noise, 0.0, 1.0)

    return pd.DataFrame({
        "lat": lat_flat,
        "lon": lon_flat,
        "suitability": suitability,
    })


def generate_scenario_grid(scenario_delta: float) -> pd.DataFrame:
    """
    Generate habitat suitability under a warming scenario.

    Uses 2024 as baseline, then shifts the latitudinal preference northward
    proportional to the temperature delta.
    """
    lats = np.arange(LAT_MIN, LAT_MAX, GRID_RESOLUTION)
    lons = np.arange(LON_MIN, LON_MAX, GRID_RESOLUTION)
    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")
    lat_flat = lat_grid.ravel()
    lon_flat = lon_grid.ravel()

    base = _coastal_proximity(lat_flat, lon_flat)

    # Shift peak latitude northward under warming
    peak_lat = 34.5 + scenario_delta * 1.5
    lat_pref = np.exp(-0.5 * ((lat_flat - peak_lat) / 3.0) ** 2)

    # Slight overall reduction under extreme warming
    warming_penalty = max(0.0, 1.0 - 0.1 * scenario_delta)

    suitability = base * lat_pref * 0.8 * warming_penalty
    noise = _RNG.normal(0, 0.04, size=suitability.shape)
    suitability = np.clip(suitability + noise, 0.0, 1.0)

    return pd.DataFrame({
        "lat": lat_flat,
        "lon": lon_flat,
        "suitability": suitability,
    })


def generate_coverage_timeseries() -> pd.DataFrame:
    """
    Generate a synthetic time-series of incidental coverage (% of
    high-suitability habitat inside any closure) from 1997 to 2024.
    """
    years = list(range(YEAR_MIN, YEAR_MAX + 1))
    coverage = []
    for y in years:
        # Base coverage drifts slowly
        base = 18.0 + 0.3 * (y - YEAR_MIN)
        # Crash period — habitat contracts to areas that happen to be less covered
        if 2009 <= y <= 2011:
            base *= 0.6
        elif 2012 <= y <= 2014:
            base *= 0.8
        # Warm blob slightly increases coverage (habitat moves inshore near MPAs)
        if 2015 <= y <= 2016:
            base *= 1.15
        noise = _RNG.normal(0, 1.5)
        coverage.append(np.clip(base + noise, 5.0, 45.0))

    return pd.DataFrame({
        "year": years,
        "coverage_pct": coverage,
    })


def compute_scenario_coverage(scenario_delta: float) -> float:
    """
    Return a single coverage % for a warming scenario.
    As habitat shifts north, overlap with southern closures decreases.
    """
    base_coverage = 25.0
    shift_penalty = scenario_delta * 4.5
    noise = _RNG.normal(0, 0.8)
    return round(np.clip(base_coverage - shift_penalty + noise, 5.0, 40.0), 1)
