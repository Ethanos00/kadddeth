"""
Real data module for the Anchovy Conservation Dashboard.

Loads the trained XGBoost model and CUFES CSV data, then produces
habitat suitability grids from actual model predictions instead of
synthetic mock data.  All results are cached so re-runs within the
same Streamlit session are instant.
"""

import os
import pickle
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon
from utils.constants import (
    LAT_MIN, LAT_MAX, LON_MIN, LON_MAX,
    GRID_RESOLUTION, YEAR_MIN, YEAR_MAX,
    CLOSURE_REGIONS,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH = os.path.join(_BASE_DIR, "anchovy_xgb_model.pkl")

# Handle both capitalizations (macOS is case-insensitive, Linux is not)
_CSV_PATH = next(
    (os.path.join(_BASE_DIR, n) for n in ("Cufes.csv", "cufes.csv")
     if os.path.exists(os.path.join(_BASE_DIR, n))),
    os.path.join(_BASE_DIR, "Cufes.csv"),  # fallback path (will fail gracefully)
)
_HAS_DATA = os.path.exists(_CSV_PATH) and os.path.exists(_MODEL_PATH)

# ---------------------------------------------------------------------------
# Lazy-loaded singletons
# ---------------------------------------------------------------------------
_model = None
_cufes_df = None

MODEL_FEATURES = [
    "month", "start_latitude", "start_longitude",
    "start_temperature", "start_salinity",
]


def _load_model():
    """Load the XGBoost model (once)."""
    global _model
    if _model is None:
        with open(_MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
    return _model


def _load_cufes() -> pd.DataFrame:
    """Load and pre-process the CUFES CSV (once)."""
    global _cufes_df
    if _cufes_df is not None:
        return _cufes_df

    df = pd.read_csv(_CSV_PATH)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month

    # Drop rows missing any model feature
    df = df.dropna(subset=MODEL_FEATURES)

    # Clip to region of interest
    df = df[
        (df["start_latitude"] >= LAT_MIN)
        & (df["start_latitude"] <= LAT_MAX)
        & (df["start_longitude"] >= LON_MIN)
        & (df["start_longitude"] <= LON_MAX)
    ].copy()

    _cufes_df = df
    return _cufes_df


# ---------------------------------------------------------------------------
# Public API — drop-in replacements for mock_data functions
# ---------------------------------------------------------------------------

def generate_habitat_grid(year: int) -> pd.DataFrame:
    """
    Produce a 0.5° habitat suitability grid for *year* using the real
    XGBoost model evaluated on CUFES sample locations.

    Falls back to mock data if Cufes.csv or the model file are absent.
    Returns DataFrame with columns: lat, lon, suitability.
    """
    if not _HAS_DATA:
        from utils.mock_data import generate_habitat_grid as _mock_grid
        return _mock_grid(year)

    model = _load_model()
    df = _load_cufes()

    year_df = df[df["year"] == year].copy()

    # Build the full output grid (every 0.5° cell)
    lats = np.arange(LAT_MIN, LAT_MAX, GRID_RESOLUTION)
    lons = np.arange(LON_MIN, LON_MAX, GRID_RESOLUTION)
    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")
    lat_flat = lat_grid.ravel()
    lon_flat = lon_grid.ravel()
    grid_out = pd.DataFrame({"lat": lat_flat, "lon": lon_flat, "suitability": 0.0})

    if year_df.empty:
        return grid_out

    # Predict suitability for every sample
    X = year_df[MODEL_FEATURES].values
    probs = model.predict_proba(X)[:, 1]  # P(class=1)
    year_df = year_df.assign(prob=probs)

    # Bin each sample into its 0.5° grid cell
    year_df = year_df.assign(
        lat_bin=np.floor(year_df["start_latitude"] / GRID_RESOLUTION) * GRID_RESOLUTION,
        lon_bin=np.floor(year_df["start_longitude"] / GRID_RESOLUTION) * GRID_RESOLUTION,
    )

    # Average probability per cell
    cell_avg = (
        year_df.groupby(["lat_bin", "lon_bin"])["prob"]
        .mean()
        .reset_index()
        .rename(columns={"lat_bin": "lat", "lon_bin": "lon", "prob": "suitability"})
    )

    # Merge onto the full grid
    grid_out = grid_out.set_index(["lat", "lon"])
    cell_avg = cell_avg.set_index(["lat", "lon"])
    grid_out.update(cell_avg)
    grid_out = grid_out.reset_index()

    return grid_out


def generate_scenario_grid(scenario_delta: float) -> pd.DataFrame:
    """
    Generate habitat suitability under a warming scenario.

    Falls back to mock data if Cufes.csv or the model file are absent.
    """
    if not _HAS_DATA:
        from utils.mock_data import generate_scenario_grid as _mock_scenario
        return _mock_scenario(scenario_delta)

    model = _load_model()
    df = _load_cufes()

    # Use most recent year as baseline
    baseline_year = int(df["year"].max())
    baseline_df = df[df["year"] == baseline_year].copy()

    if baseline_df.empty:
        # Fallback to generating an empty grid
        lats = np.arange(LAT_MIN, LAT_MAX, GRID_RESOLUTION)
        lons = np.arange(LON_MIN, LON_MAX, GRID_RESOLUTION)
        lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")
        return pd.DataFrame({
            "lat": lat_grid.ravel(),
            "lon": lon_grid.ravel(),
            "suitability": 0.0,
        })

    # Apply temperature delta
    X = baseline_df[MODEL_FEATURES].copy()
    X["start_temperature"] = X["start_temperature"] + scenario_delta

    probs = model.predict_proba(X.values)[:, 1]
    baseline_df = baseline_df.assign(prob=probs)

    # Bin and average
    baseline_df = baseline_df.assign(
        lat_bin=np.floor(baseline_df["start_latitude"] / GRID_RESOLUTION) * GRID_RESOLUTION,
        lon_bin=np.floor(baseline_df["start_longitude"] / GRID_RESOLUTION) * GRID_RESOLUTION,
    )
    cell_avg = (
        baseline_df.groupby(["lat_bin", "lon_bin"])["prob"]
        .mean()
        .reset_index()
        .rename(columns={"lat_bin": "lat", "lon_bin": "lon", "prob": "suitability"})
    )

    # Full grid
    lats = np.arange(LAT_MIN, LAT_MAX, GRID_RESOLUTION)
    lons = np.arange(LON_MIN, LON_MAX, GRID_RESOLUTION)
    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing="ij")
    grid_out = pd.DataFrame({
        "lat": lat_grid.ravel(),
        "lon": lon_grid.ravel(),
        "suitability": 0.0,
    })
    grid_out = grid_out.set_index(["lat", "lon"])
    cell_avg = cell_avg.set_index(["lat", "lon"])
    grid_out.update(cell_avg)
    grid_out = grid_out.reset_index()

    return grid_out


def _build_closure_polygons():
    """Build Shapely polygons for each closure region (cached)."""
    polys = []
    for name, info in CLOSURE_REGIONS.items():
        coords = info["coords"]
        # Folium uses (lat, lon); Shapely uses (lon, lat)
        poly = Polygon([(c[1], c[0]) for c in coords])
        polys.append(poly)
    return polys


_closure_polys = None


def _get_closure_polys():
    global _closure_polys
    if _closure_polys is None:
        _closure_polys = _build_closure_polygons()
    return _closure_polys


def generate_coverage_timeseries() -> pd.DataFrame:
    """
    Compute real incidental coverage for each year:
    % of suitable-habitat cells whose 0.5° box intersects any closure polygon.

    Uses a suitability threshold of 0.2 (appropriate for a probability model
    where few cells exceed 0.5).
    """
    from shapely.geometry import box as shapely_box

    polys = _get_closure_polys()
    years = list(range(YEAR_MIN, YEAR_MAX + 1))
    coverage = []

    for y in years:
        grid = generate_habitat_grid(y)
        high = grid[grid["suitability"] >= 0.2]
        if len(high) == 0:
            coverage.append(0.0)
            continue

        inside = 0
        for _, row in high.iterrows():
            cell = shapely_box(
                row["lon"], row["lat"],
                row["lon"] + GRID_RESOLUTION, row["lat"] + GRID_RESOLUTION,
            )
            if any(poly.intersects(cell) for poly in polys):
                inside += 1

        pct = (inside / len(high)) * 100.0
        coverage.append(round(pct, 1))

    return pd.DataFrame({"year": years, "coverage_pct": coverage})


def compute_scenario_coverage(scenario_delta: float) -> float:
    """
    Return incidental coverage % for a warming scenario grid.
    """
    from shapely.geometry import box as shapely_box

    polys = _get_closure_polys()
    grid = generate_scenario_grid(scenario_delta)
    high = grid[grid["suitability"] >= 0.2]

    if len(high) == 0:
        return 0.0

    inside = 0
    for _, row in high.iterrows():
        cell = shapely_box(
            row["lon"], row["lat"],
            row["lon"] + GRID_RESOLUTION, row["lat"] + GRID_RESOLUTION,
        )
        if any(poly.intersects(cell) for poly in polys):
            inside += 1

    return round((inside / len(high)) * 100.0, 1)
