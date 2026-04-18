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


def build_habitat_map(
    grid_df: pd.DataFrame,
    theme_name: str = "Dark",
    show_closures: bool = True,
    layer_name: str = "Habitat Suitability",
) -> folium.Map:
    """
    Build a complete habitat map with heatmap + closure overlays.

    This is the main entry point for map construction.
    """
    m = create_base_map(theme_name)
    m = add_habitat_layer(m, grid_df, name=layer_name)
    if show_closures:
        m = add_closure_polygons(m, theme_name)
    folium.LayerControl(collapsed=False).add_to(m)
    return m
