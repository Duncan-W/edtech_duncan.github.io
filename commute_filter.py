import pandas as pd

# Load the data
df = pd.read_csv("SPRADDR.csv")

# Filter by address type
df = df[df['SPRADDR_ATYP_CODE'] == 'TA']

# Convert FROM_DATE to datetime (allowing dd/mm/yyyy and optional time)
df['SPRADDR_FROM_DATE'] = pd.to_datetime(df['SPRADDR_FROM_DATE'], dayfirst=True, errors='coerce')

# Filter for dates after 1st Jan 2024
df = df[df['SPRADDR_FROM_DATE'] >= pd.Timestamp('2024-01-01')]

# Keep only columns 6 to 13 (Python is 0-indexed)
df = df.iloc[:, 5:12]

# Save the filtered rows with only selected columns
df.to_csv("SPRADDR_filtered.csv", index=False)

print(f"Filtered {len(df)} rows saved to SPRADDR_filtered.csv with only address columns.")
