import os, requests, toml
try:
    token = toml.load(".streamlit/secrets.toml").get("GFW_TOKEN", "")
except:
    token = ""
r = requests.post(
    "https://gateway.api.globalfishingwatch.org/v3/4wings/report",
    params={
        "datasets[0]": "public-global-fishing-effort:latest",
        "date-range": "1996-01-01,2022-12-31",
        "filters[0]": "geartype IN ('purse_seines')",
        "spatial-aggregation": "false",
        "spatial-resolution": "HIGH",
        "temporal-resolution": "YEARLY",
        "format": "JSON",
        "group-by": "GEARTYPE",
    },
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"geojson": {"type": "Feature", "properties": {}, "geometry": {
        "type": "Polygon", "coordinates": [[[-126, 30], [-116, 30], [-116, 42], [-126, 42], [-126, 30]]]
    }}},
)
data = r.json()
entries = data.get("entries", [])
if entries:
    ds_data = list(entries[0].values())[0] if entries[0].values() else []
    print("Number of points:", len(ds_data))
    
    # Also sum hours per year to see data distribution
    by_year = {}
    for row in ds_data:
        yr = row.get("date")
        by_year[yr] = by_year.get(yr, 0) + 1
    print("Points per year:", by_year)
