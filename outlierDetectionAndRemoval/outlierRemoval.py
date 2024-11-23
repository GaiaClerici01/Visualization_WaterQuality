import pandas as pd
from decimal import *
from scipy.stats import zscore

# Intake raw file
df = pd.read_csv('../aggregatedDataPerYear/aggregateddata2022.csv')

df_sites = pd.read_csv('../monitoringSite.csv')

df_geo = pd.merge(df_sites, df, on='monitoringSiteIdentifier')
df_elements = df_geo[['eeaIndicator']].drop_duplicates()

# Function to filter outliers using the IQR method
def remove_outliers_iqr(data, column):
    Q1 = data[column].quantile(0.25)  # First quartile
    Q3 = data[column].quantile(0.75)  # Third quartile
    IQR = Q3 - Q1  # Interquartile range
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

# Process each element
for element in df_elements['eeaIndicator']:
    df_final = df_geo[df_geo['eeaIndicator'] == element]
    df_final = remove_outliers_iqr(df_final, 'resultMeanValue')
    df_geo = df_geo[df_geo['eeaIndicator'] != element]
    df_geo = pd.concat([df_geo, df_final])

df_geo.to_csv('aggregatedData2022.csv', index=False)