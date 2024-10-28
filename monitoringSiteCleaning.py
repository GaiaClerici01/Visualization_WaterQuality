import pandas as pd

df = pd.read_csv('waterbase_s_wise_spatialobject_deriveddata_full.csv', delimiter= ";", on_bad_lines='skip', index_col=False)

df = df[['countryCode', 'monitoringSiteIdentifier', 'waterBodyIdentifier', 'waterBodyName', 'specialisedZoneType', 'lon', 'lat', 'statusCode']]

# Drop rows with missing values
df = df.dropna()

df = df[df['countryCode'] == 'IT']
# Filter rows with statusCode == 'stable'
df = df[df['statusCode'] == 'stable']

# Filter for valid specialized zones
df = df[df['specialisedZoneType'] != 'transitionalWaterBody']
df = df[df['specialisedZoneType'] != 'territorialWaters']

df.to_csv('monitoringSite.csv', index=False)
