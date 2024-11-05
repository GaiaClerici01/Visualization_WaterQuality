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

# Filter on year (cast to int) to limit file size for github
df['phenomenonTimeReferenceYear'] = df['phenomenonTimeReferenceYear'].astype(int)
df = df[df['phenomenonTimeReferenceYear'] >= 2020]

# Format scientific notation to decimal
df['resultMeanValue'] = df['resultMeanValue'].round(6)
df['resultNumberOfSamples'] = df['resultNumberOfSamples'].astype(int)

# Output sliced file
df.to_csv('aggregateddata.csv', index=False)