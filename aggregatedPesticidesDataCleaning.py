import pandas as pd
from decimal import *

# Intake raw file
df = pd.read_csv('aggregateddata_pesticides_full.csv', delimiter= ";", on_bad_lines='skip', index_col=False)

# Limit columns to process
df = df[['monitoringSiteIdentifier', 'eeaIndicator', 'phenomenonTimeReferenceYear', 'resultMeanValue', 'resultNumberOfSamples', 'exceedanceQualityStandard', 'lon', 'lat', 'monitoringSiteStatusCode']]

# Drop rows with missing values
df = df.dropna()

# Filter rows with statusCode == 'stable'
df = df[df['monitoringSiteStatusCode'] == 'stable']

# Remove unneeded filter columns
df = df[['monitoringSiteIdentifier', 'eeaIndicator', 'phenomenonTimeReferenceYear', 'resultMeanValue', 'resultNumberOfSamples','exceedanceQualityStandard']]

# Format year (cast to int)
df['phenomenonTimeReferenceYear'] = df['phenomenonTimeReferenceYear'].astype(int)

# Format scientific notation to decimal
df['resultMeanValue'] = df['resultMeanValue'].round(6)
df['resultNumberOfSamples'] = df['resultNumberOfSamples'].astype(int)
df['exceedanceQualityStandard'] = df['exceedanceQualityStandard'].astype(int)

# Run through year range to create a .csv per year
max_year = max(df['phenomenonTimeReferenceYear'])
min_year = min(df['phenomenonTimeReferenceYear']) if min(df['phenomenonTimeReferenceYear']) > 2000 else 2000

for year in range(min_year, max_year +1):
    df_year = df[df['phenomenonTimeReferenceYear'] == year]
    df_year.to_csv(f'pesticides_{year}.csv', index=False)