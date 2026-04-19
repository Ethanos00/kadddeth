"""
Map construction utilities for the Anchovy Conservation Dashboard.

Provides helpers to build Folium maps with habitat heatmap layers
and closure polygon overlays.
"""

import folium
from folium.plugins import HeatMap
import pandas as pd
from utils.constants import (
    MAP_CENTER, MAP_ZOOM,
    FOLIUM_GRADIENT, CLOSURE_STYLE, CLOSURE_REGIONS, THEMES,
)


def create_base_map(theme_name: str = "Dark") -> folium.Map:
    """Create a Folium base map with the appropriate tile layer for the theme."""
    theme = THEMES[theme_name]
    tiles = theme["map_tiles"]

    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles=tiles,
        control_scale=True,
        prefer_canvas=True,
    )
    return m


def add_habitat_layer(
    m: folium.Map,
    grid_df: pd.DataFrame,
    threshold: float = 0.1,
    name: str = "Habitat Suitability",
) -> folium.Map:
    """
    Add a heatmap layer showing habitat suitability.

    Parameters
    ----------
    m : folium.Map
        Base map to add layer to.
    grid_df : pd.DataFrame
        Must have columns: lat, lon, suitability.
    threshold : float
        Minimum suitability to include a point (filters visual noise).
    name : str
        Layer name for the layer control.
    """
    filtered = grid_df[grid_df["suitability"] >= threshold]
    heat_data = filtered[["lat", "lon", "suitability"]].values.tolist()

    HeatMap(
        heat_data,
        name=name,
        min_opacity=0.3,
        max_zoom=10,
        radius=20,
        blur=15,
        gradient=FOLIUM_GRADIENT,
    ).add_to(m)

    return m


def add_closure_polygons(
    m: folium.Map,
    theme_name: str = "Dark",
) -> folium.Map:
    """Add approximate closure region polygons to the map."""
    closure_group = folium.FeatureGroup(name="Conservation Closures")

    for name, info in CLOSURE_REGIONS.items():
        coords = info["coords"]
        closure_type = info["type"]

        # Color by type
        type_colors = {
            "GEA": ("#f59e0b", "#fbbf24"),
            "MPA": ("#6366f1", "#818cf8"),
            "CCA": ("#f59e0b", "#fbbf24"),
            "RCA": ("#10b981", "#34d399"),
        }
        fill, border = type_colors.get(closure_type, ("#6366f1", "#818cf8"))

        tooltip_html = f"<b>{name}</b><br>Type: {closure_type}"

        folium.Polygon(
            locations=coords,
            tooltip=tooltip_html,
            fill=True,
            fill_color=fill,
            fill_opacity=0.15,
            color=border,
            weight=2,
            dash_array="5, 5",
        ).add_to(closure_group)

    closure_group.add_to(m)
    return m


def add_fishing_pressure_layer(
    m: folium.Map,
    closure_effort: dict,
    annual_effort: dict,
    spatial_effort: list = None,
) -> folium.Map:
    """
    Add fishing pressure layer: circle markers at each GEA closure showing
    detected purse seiner hours inside (2016–2022), plus dot markers for the
    approximate coastal fishing zone where the fleet actually operates.
    """
    fishing_group = folium.FeatureGroup(name="Fishing Pressure (Purse Seiners)")

    # GEA closure centres (lat, lon)
    closure_centres = {
        "Hidden Reef":    (33.730, -119.137),
        "W. SB Island":   (33.513, -119.218),
        "Potato Bank":    (33.267, -119.822),
        "107/118 Bank":   (33.075, -119.608),
        "Cherry Bank":    (32.879, -119.393),
        "Seamount 109":   (32.619, -119.533),
        "43-Fathom Spot": (32.651, -117.917),
        "Northeast Bank": (32.395, -119.572),
        "Sur Ridge":      (36.354, -122.301),
        "Cordell Bank":   (38.012, -123.443),
    }

    max_hours = max(closure_effort.values()) if any(v > 0 for v in closure_effort.values()) else 1

    for name, (lat, lon) in closure_centres.items():
        hours = closure_effort.get(name, 0)
        # Green = no fishing detected; orange = some fishing detected
        color = "#22c55e" if hours == 0 else "#f97316"
        radius = 6 if hours == 0 else max(6, 6 + 14 * (hours / max_hours))

        tooltip = (
            f"<b>{name}</b><br>"
            f"Purse seiner effort 2016–2022: <b>{hours:.1f} hrs</b><br>"
            f"{'✅ No fishing detected inside closure' if hours == 0 else '⚠️ Fishing detected inside closure'}"
        )
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=2,
            tooltip=folium.Tooltip(tooltip, sticky=True),
        ).add_to(fishing_group)

    # Spatial fishing locations from GFW (high-res grid points)
    if spatial_effort:
        max_spatial = max([p.get('hours', 0) for p in spatial_effort]) if spatial_effort else 1
        for p in spatial_effort:
            hours = p.get('hours', 0)
            if hours > 0:
                lat = p.get('lat')
                lon = p.get('lon')
                # Scale radius: base 2 + scaled by relative intensity
                radius = 2 + (8 * (hours / max_spatial))
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=radius,
                    color="#f97316",
                    fill=True,
                    fill_color="#f97316",
                    fill_opacity=0.6,
                    weight=0.5,
                    tooltip=folium.Tooltip(
                        f"<b>Fishing Details (High-Res Grid)</b><br>"
                        f"Location: {lat:.2f}, {lon:.2f}<br>"
                        f"Effort: <b>{hours:.1f} hrs</b>",
                        sticky=True,
                    ),
                ).add_to(fishing_group)

    fishing_group.add_to(m)
    return m


def build_habitat_map(
    grid_df: pd.DataFrame,
    theme_name: str = "Dark",
    show_closures: bool = True,
    show_fishing: bool = False,
    closure_effort: dict = None,
    annual_effort: dict = None,
    spatial_effort: list = None,
    layer_name: str = "Habitat Suitability",
) -> folium.Map:
    """Build a complete habitat map with heatmap + closure overlays + optional fishing layer."""
    m = create_base_map(theme_name)
    m = add_habitat_layer(m, grid_df, name=layer_name)
    if show_closures:
        m = add_closure_polygons(m, theme_name)
    if show_fishing and closure_effort is not None:
        m = add_fishing_pressure_layer(m, closure_effort, annual_effort or {}, spatial_effort)
    folium.LayerControl(collapsed=False).add_to(m)
    return m
