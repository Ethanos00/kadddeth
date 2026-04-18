import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import contextily as cx
import matplotlib.pyplot as plt
def ddm_to_dd(deg, dec_min):
    """Converts Degrees Decimal Minutes to Decimal Degrees."""
    return deg + (dec_min / 60)

# 1. Define the Vertices (Negative Longitude for West)
# Format: (Lat_Deg, Lat_Min, Lon_Deg, Lon_Min)

gea_data = {
    "Hidden Reef": [
        (33, 46.14, 119, 10.45), (33, 46.14, 119, 5.96),
        (33, 41.40, 119, 5.96), (33, 41.40, 119, 10.45)
    ],
    "West of Santa Barbara Island": [
        (33, 33.64, 119, 18.54), (33, 33.64, 119, 7.57),
        (33, 27.90, 119, 07.57), (33, 27.90, 119, 18.54)
    ],
    "Potato Bank": [
        (33, 21.00, 119, 53.00), (33, 21.00, 119, 45.67),
        (33, 11.00, 119, 45.67), (33, 11.00, 119, 53.00)
    ],
    "107/118 Bank": [
        (33, 05.51, 119, 41.29), (33, 08.64, 119, 36.71),
        (33, 03.50, 119, 31.69), (33, 00.36, 119, 36.27)
    ],
    "Cherry Bank": [
        (32, 50.86, 119, 29.40), (32, 56.96, 119, 19.82),
        (32, 54.69, 119, 17.78), (32, 48.59, 119, 27.35)
    ],
    "Seamount 109": [
        (32, 43.75, 119, 37.00), (32, 43.75, 119, 34.29),
        (32, 31.95, 119, 26.94), (32, 30.47, 119, 29.71),
        (32, 39.54, 119, 37.00)
    ],
    "43-Fathom Spot": [
        (32, 42.00, 118, 00.05), (32, 42.00, 117, 50.00),
        (32, 36.70, 117, 50.00), (32, 36.18, 117, 50.27),
        (32, 36.18, 118, 00.05)
    ],
    "Northeast Bank": [
        (32, 27.39, 119, 37.00), (32, 27.39, 119, 31.60),
        (32, 20.00, 119, 31.60), (32, 20.00, 119, 37.00)
    ],
    "Sur Ridge": [
        (36, 26.00, 122, 20.81), (36, 25.55, 122, 15.23),
        (36, 21.71, 122, 15.32), (36, 17.95, 122, 17.13),
        (36, 16.42, 122, 16.69), (36, 16.41, 122, 20.76)
    ],
    "Cordell Bank": [
        (38, 03.18, 123, 20.77), (38, 06.29, 123, 25.03),
        (38, 06.34, 123, 29.32), (38, 04.57, 123, 31.30),
        (38, 02.32, 123, 31.07), (38, 00.00, 123, 28.40),
        (37, 58.10, 123, 26.66), (37, 55.07, 123, 26.81),
        (38, 00.00, 123, 23.08)
    ]
}

polygons = []
names = []

for name, coords in gea_data.items():
    # Convert all vertices for this polygon
    dd_coords = [( -ddm_to_dd(c[2], c[3]), ddm_to_dd(c[0], c[1]) ) for c in coords]
    polygons.append(Polygon(dd_coords))
    names.append(name)

# 2. Create the GeoDataFrame
closures_gdf = gpd.GeoDataFrame({'name': names, 'geometry': polygons}, crs="EPSG:4326")

# 3. Export for your main project
# closures_gdf.to_file("gea_closures.gpkg", driver="GPKG")
print(closures_gdf.head())
# Complete dataset extracted from [90 FR 57719, Dec. 12, 2025]


# 1. Load your closures
closures = gpd.read_file("gea_closures.gpkg")

# 2. Convert to Web Mercator (Required for the basemap to align)
closures_wm = closures.to_crs(epsg=3857)

# 3. Create the plot
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the closures with a thick border so they stand out against the terrain
closures_wm.plot(ax=ax, edgecolor='red', facecolor='none', linewidth=2, zorder=5)

# 4. Add the background (Terrain or Street view)
# cx.providers.CartoDB.Positron is clean for reports; 
# cx.providers.Esri.WorldImagery gives you the actual satellite view.
cx.add_basemap(ax, source=cx.providers.CartoDB.Positron) # type: ignore[attr-defined]

ax.set_title("GEA Closures overlaid on California Coast", fontsize=15)
ax.set_axis_off() # Hides the messy coordinate numbers

plt.show()