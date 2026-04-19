import os
import requests
try:
    import toml
    secrets = toml.load(".streamlit/secrets.toml")
    token = secrets.get("GFW_TOKEN", "")
except:
    token = os.environ.get("GFW_TOKEN", "")

# We will test grabbing grid data
_BASE = "https://gateway.api.globalfishingwatch.org/v3/4wings/report"
_CA_BOX = [[-126, 30], [-116, 30], [-116, 42], [-126, 42], [-126, 30]]
year = 2022
r = requests.post(
    _BASE,
    params={
        "datasets[0]": "public-global-fishing-effort:latest",
        "date-range": f"{year}-01-01,{year}-12-31",
        "filters[0]": "geartype IN ('purse_seines')",
        "spatial-aggregation": "false",
        "spatial-resolution": "HIGH",
        "temporal-resolution": "YEARLY",
        "format": "JSON",
        "group-by": "GEARTYPE",
    },
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"geojson": {"type": "Feature", "properties": {}, "geometry": {
        "type": "Polygon", "coordinates": [_CA_BOX]
    }}},
)
print("Status:", r.status_code)
data = r.json()
entries = data.get("entries", [])
print("Number of entries:", len(entries))
if entries:
    first_entry = entries[0]
    keys = list(first_entry.keys())
    print("Keys in first entry:", keys)
    for ds_data in first_entry.values():
        if ds_data and len(ds_data) > 0:
            print("First few rows of first dataset:", ds_data[:3])
