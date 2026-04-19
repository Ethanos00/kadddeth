import pandas as pd
import matplotlib.pyplot as plt
import os

df = pd.read_csv('cufes.csv')

# Drop null coordinates
df = df.dropna(subset=['start_latitude', 'start_longitude'])

# Filter by standard california current bounds from constants to avoid extreme outliers messing up the plot scale
df = df[
    (df["start_latitude"] >= 25.0) & (df["start_latitude"] <= 50.0) &
    (df["start_longitude"] >= -135.0) & (df["start_longitude"] <= -110.0)
]

plt.figure(figsize=(10, 12))
plt.scatter(df['start_longitude'], df['start_latitude'], s=1, alpha=0.3, c='blue')

# add some context
plt.title('Geographic Distribution of CUFES Data Points (1996 - 2022)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True, linestyle='--', alpha=0.6)

# Provide some basic coastline approximation or just let the data define the coast
plt.tight_layout()

output_path = '/Users/dylan/.gemini/antigravity/brain/4713c49f-dc1f-4aac-a051-46cd23f4cc86/cufes_distribution.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f'Saved to {output_path}')
