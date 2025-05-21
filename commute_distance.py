import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# Load CSV
df = pd.read_csv("SPRADDR_tiny.csv")

# Filter for term addresses only
df = df[df["SPRADDR_ATYP_CODE"] == "TA"]

# Combine address parts into a single address string
def combine_address(row):
    parts = [
        row["SPRADDR_STREET_LINE1"],
        row["SPRADDR_STREET_LINE2"],
        row["SPRADDR_STREET_LINE3"],
        row["SPRADDR_CITY"]
    ]
    return ', '.join([str(p) for p in parts if pd.notna(p)])

df['SPRADDR_FROM_DATE'] = pd.to_datetime(df['SPRADDR_FROM_DATE'], dayfirst=True, errors='coerce')

# Filter to only addresses added in 2024
df = df[df['SPRADDR_FROM_DATE'] >= pd.Timestamp('2024-01-01')]

df["full_address"] = df.apply(combine_address, axis=1)

# Initialize geocoder
geolocator = Nominatim(user_agent="iadt_commute_calc")

# Define campus coordinates
campus_coords = (53.2803265, -6.1520283)



# Geocode addresses and calculate distances
distances = []
for addr in df["full_address"]:
    try:
        location = geolocator.geocode(addr, timeout=10)
        if location:
            student_coords = (location.latitude, location.longitude)
            distance_km = geodesic(student_coords, campus_coords).km
            distances.append(distance_km)
        else:
            distances.append(None)
    except Exception as e:
        print(f"Error with address: {addr} — {e}")
        distances.append(None)
    time.sleep(1)  # to avoid rate-limiting

df["distance_km"] = distances

# Basic stats
print(df["distance_km"].describe())

# Save to CSV
df.to_csv("SPRADDR_with_distances.csv", index=False)
