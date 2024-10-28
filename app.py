from dash import Dash, html, dcc
import plotly.express as px
import geopandas as gpd
import dash_bootstrap_components as dbc
import pandas as pd

#Keep this code for future animation
'''df = px.data.gapminder()
df = df[df['continent'] == 'Europe']
#If we want latitude and longitude of points remove locations and write "lat=geo_df.geometry.y, lon=geo_df.geometry.x"
fig = px.scatter_geo(df, locations="iso_alpha", color="continent", hover_name="country",
               animation_frame="year", projection="natural earth")
'''
df = pd.read_csv('monitoringSite.csv')
fig = px.scatter_geo(df, lat="lat", lon="lon", hover_name="waterBodyName", projection="natural earth", color="specialisedZoneType")
fig.update_geos(scope = 'europe', resolution=50, fitbounds="locations")
fig.update_layout(height=500, margin={"r":0,"t":0,"l":0,"b":0})

#Create the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(
    [
        dbc.Row(dbc.Col(
            html.Div("Water quality in Europe", 
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
        )),
        dbc.Row([
            dbc.Col(
                html.Div(dcc.Graph(figure=fig)),
                width={"size": 9}
            ),
            dbc.Col(
                html.Div("here graphs"),
                width={"size": 2}
            )
        ])
    ]
)

if __name__ == '__main__':
    app.run(debug=True)