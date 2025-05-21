import folium
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import seaborn as sns
import matplotlib.pyplot as plt

# --- SETTINGS ---
CSV_PATH = "address-coordinates.csv"
UNI_COORDS = [53.2803265, -6.1520283]
UNIVERSITY_LAT = 53.2834   
UNIVERSITY_LON = -6.1511

# --- HELPER FUNCTION: Convert lat/lon strings ---
def parse_coord(coord_str):
    coord_str = coord_str.strip().replace("°", "").replace("N", "").replace("W", "").strip()
    value = float(coord_str)
    if 'W' in coord_str or '-' in coord_str:
        return -abs(value)
    return value

# --- HELPER FUNCTION: Calculate Haversine distance ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    return R * c  # in kilometers

# --- LOAD DATA ---
df = pd.read_csv(CSV_PATH)

# Clean and convert lat/lon
df['latitude'] = df['latitude'].apply(parse_coord)
df['longitude'] = df['longitude'].apply(parse_coord)

# Create base map centered on university
m = folium.Map(location=UNI_COORDS, zoom_start=11, tiles="CartoDB positron")

# Marker for university
folium.Marker(
    location=UNI_COORDS,
    popup="University",
    icon=folium.Icon(color="blue", icon="university", prefix="fa")
).add_to(m)

# --- PLOT STUDENTS ---
for _, row in df.iterrows():
    lat, lon = row['latitude'], row['longitude']
    label = row.get('label', f"{lat:.4f}, {lon:.4f}")
    distance_km = haversine(lat, lon, UNI_COORDS[0], UNI_COORDS[1])

    # Choose line color based on distance
    if distance_km < 5:
        color = "green"
    elif distance_km < 15:
        color = "orange"
    else:
        color = "red"

    # Line from student to university
    folium.PolyLine(
        locations=[[lat, lon], UNI_COORDS],
        color=color,
        weight=2,
        opacity=0.6,
        tooltip=f"{label} — {distance_km:.1f} km"
    ).add_to(m)

    # Student marker
    folium.CircleMarker(
        location=[lat, lon],
        radius=5,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(f"{label}<br>{distance_km:.1f} km", max_width=250)
    ).add_to(m)

# --- SAVE MAP ---
m.save("student_commute_map.html")


# --- Calculate distances ---
df['distance_km'] = df.apply(
    lambda row: haversine(UNIVERSITY_LAT, UNIVERSITY_LON, row['latitude'], row['longitude']),
    axis=1
)

# --- Stats summary ---
print("Distance Statistics (in km):")
print(df['distance_km'].describe())

# --- Plotting ---
sns.set(style="whitegrid")

# Histogram
plt.figure(figsize=(10, 6))
sns.histplot(df['distance_km'], bins=20, kde=True, color='skyblue')
plt.axvline(df['distance_km'].mean(), color='red', linestyle='--', label=f"Mean: {df['distance_km'].mean():.2f} km")
plt.title("Distribution of Student Distances to University")
plt.xlabel("Distance (km)")
plt.ylabel("Number of Students")
plt.legend()
plt.tight_layout()
plt.show()

# Boxplot
plt.figure(figsize=(8, 2))
sns.boxplot(x=df['distance_km'], color='lightgreen')
plt.title("Distance Boxplot")
plt.xlabel("Distance (km)")
plt.tight_layout()
plt.show()

print("✅ Map saved to student_commute_map.html")

# Create bins and labels
bin_edges = [0, 5, 10, 15, 20, 30, 50, 75, 100, 150, 200]
bin_labels = [f"{bin_edges[i]}–{bin_edges[i+1]} km" for i in range(len(bin_edges)-1)]
df['distance_bin'] = pd.cut(df['distance_km'], bins=bin_edges, labels=bin_labels, include_lowest=True)

# Count values per bin
bin_counts = df['distance_bin'].value_counts().sort_index()
total = bin_counts.sum()
bin_percentages = (bin_counts / total * 100).round(1)

# Create bar plot
plt.figure(figsize=(12, 6))
barplot = sns.barplot(x=bin_counts.index, y=bin_counts.values, palette="Blues_d")
plt.title("Number of Students by Distance Category")
plt.xlabel("Distance from University")
plt.ylabel("Number of Students")

# Annotate bars with counts and percentages
for i, count in enumerate(bin_counts):
    percent = bin_percentages.iloc[i]
    plt.text(i, count + 1, f"{count}\n({percent}%)", ha='center', va='bottom', fontsize=9)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Optional: print table
summary_table = pd.DataFrame({
    "Distance Range": bin_counts.index,
    "Student Count": bin_counts.values,
    "Percentage": bin_percentages.values
})
print("\nSummary of Students by Distance Range:")
print(summary_table.to_string(index=False))
