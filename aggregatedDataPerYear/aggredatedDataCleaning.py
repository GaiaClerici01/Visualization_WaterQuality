import pandas as pd
from decimal import *

# Intake raw file
df = pd.read_csv('aggregateddata_full.csv', delimiter= ";", on_bad_lines='skip', index_col=False)

# Limit columns to process
df = df[['monitoringSiteIdentifier', 'eeaIndicator', 'phenomenonTimeReferenceYear', 'resultMeanValue', 'resultNumberOfSamples', 'lon', 'lat', 'monitoringSiteStatusCode']]

# Drop rows with missing values
df = df.dropna()

# Filter rows with statusCode == 'stable'
df = df[df['monitoringSiteStatusCode'] == 'stable']

# Remove unneeded filter columns
df = df[['monitoringSiteIdentifier', 'eeaIndicator', 'phenomenonTimeReferenceYear', 'resultMeanValue', 'resultNumberOfSamples']]

# Format year (cast to int)
df['phenomenonTimeReferenceYear'] = df['phenomenonTimeReferenceYear'].astype(int)

# Format scientific notation to decimal
df['resultMeanValue'] = df['resultMeanValue'].round(6)
df['resultNumberOfSamples'] = df['resultNumberOfSamples'].astype(int)

# Run through year range to create a .csv per year
max_year = max(df['phenomenonTimeReferenceYear'])
min_year = min(df['phenomenonTimeReferenceYear']) if min(df['phenomenonTimeReferenceYear']) > 2000 else 2000

for year in range(min_year, max_year +1):
    df_year = df[df['phenomenonTimeReferenceYear'] == year]
    df_year.to_csv(f'aggregateddata{year}.csv', index=False)