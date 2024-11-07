from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import plotly.graph_objs as go
import geopandas as gpd
import dash_bootstrap_components as dbc
import pandas as pd

#Keep this code for future animation
'''df_geo = px.data.gapminder()
df_geo = df_geo[df_geo['continent'] == 'Europe']
#If we want latitude and longitude of points remove locations and write "lat=geo_df.geometry.y, lon=geo_df.geometry.x"
fig = px.scatter_geo(df_geo, locations="iso_alpha", color="continent", hover_name="country",
               animation_frame="year", projection="natural earth")
'''
df_sites = pd.read_csv('monitoringSite.csv')
df_data = pd.read_csv('aggregateddata.csv')
df_geo = pd.merge(df_sites, df_data, on='monitoringSiteIdentifier')
df_elements = df_geo[['eeaIndicator']]
df_elements = df_elements.drop_duplicates()
df_graph = df_geo[['eeaIndicator', 'phenomenonTimeReferenceYear', 'resultMeanValue']]
df_graph = df_graph.drop_duplicates()

fig = px.scatter_geo(df_geo, lat="lat", lon="lon", hover_name="waterBodyName", projection="natural earth", color="resultMeanValue", color_continuous_scale='deep', range_color=[0, 50])
fig.update_geos(scope = 'europe', resolution=50, fitbounds="locations")
fig.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})

#Create the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    "Water quality in Europe", 
                    style={
                        "text-align": "center",
                        "margin": "6px",
                        "color": "rgb(0, 0, 153)",
                        "font-size":"25px",
                        "padding-bottom": "6px",
                        "border-bottom-width": "2px",
                        "border-bottom-color": "rgb(0, 0, 153)",
                        "border-bottom-style": "solid"}
                ),
                width={"size": 12},
            )
        ),
        dbc.Row(
            dbc.Col(
                dcc.Dropdown(
                    id='element_filter', 
                    options=[{'label': i, 'value': i} for i in df_elements['eeaIndicator']], 
                    value='Nitrate', 
                    clearable=False,
                    style={
                        'margin-bottom': '2'
                    }
                )
            )
        ),
        dbc.Row([
            dbc.Col(
                html.Div(dcc.Graph(figure=fig)),
                width={"size": 8}
            ),
            dbc.Col(
                html.Div(dcc.Graph(figure=go.Figure(data=[go.Scatter(x=df_graph['phenomenonTimeReferenceYear'], y=df_graph['resultMeanValue'])]))),
                width={"size": 4}
            )
        ])
    ]
)

if __name__ == '__main__':
    app.run(debug=True)