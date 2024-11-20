from dash import Dash, html, dcc, Output, Input
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd

# Ask Gareth: Animation with go? What do we do about outliers?


#Keep this code for future animation
'''df_geo = px.data.gapminder()
df_geo = df_geo[df_geo['continent'] == 'Europe']
#If we want latitude and longitude of points remove locations and write "lat=geo_df.geometry.y, lon=geo_df.geometry.x"
fig = px.scatter_geo(df_geo, locations="iso_alpha", color="continent", hover_name="country",
               animation_frame="year", projection="natural earth")
'''
df_sites = pd.read_csv('monitoringSite.csv')
df_data22 = pd.read_csv('aggregateddata2022.csv')
df_data22['year'] = 2022
df_data21 = pd.read_csv('aggregateddata2021.csv')
df_data21['year'] = 2021
df_data = [df_data21, df_data22]
df_data = pd.concat(df_data)

df_geo = pd.merge(df_sites, df_data, on='monitoringSiteIdentifier')

# Extract unique indicators and calculate weighted mean for density map
df_elements = df_geo[['eeaIndicator']].drop_duplicates()
df_weighted_mean = df_geo.groupby('eeaIndicator')['resultMeanValue'].mean()

# Create the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    "Water Quality in Italy",
                    style={
                        "text-align": "center",
                        "margin": "6px",
                        "color": "rgb(0, 0, 153)",
                        "font-size": "25px",
                        "padding-bottom": "6px",
                        "border-bottom-width": "2px",
                        "border-bottom-color": "rgb(0, 0, 153)",
                        "border-bottom-style": "solid",
                    },
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
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='map_graph'),
                    width={"size": 8},
                ),
                dbc.Col(
                    dcc.Graph(id='line_graph'),
                    width={"size": 4},
                ),
            ]
        ),
    ]
)

# Callback to update the density mapbox with weighted mean coloring
@app.callback(
    Output('map_graph', 'figure'),
    Input('element_filter', 'value')
)
def update_map(selected_element):
    filtered_data = df_geo[df_geo['eeaIndicator'] == selected_element]
    hovertemplate = '%{text}<br>Value: %{z} </span><extra></extra>'

    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        lat=filtered_data['lat'],
        lon=filtered_data['lon'],
        marker=dict(
            size=5,
            color=filtered_data['resultMeanValue'],
            colorscale='matter',
            cmin=filtered_data['resultMeanValue'].min(),
            cmax=filtered_data['resultMeanValue'].max(),
        ),
        opacity=0.7,  # Adjust opacity as needed
    ))

    # Create the density mapbox using weighted mean for coloring
    fig.add_trace(go.Densitymapbox(
        lat=filtered_data['lat'],
        lon=filtered_data['lon'],
        text=filtered_data['waterBodyName'],
        z=filtered_data['resultMeanValue'],
        radius=8,
        opacity=1,  # Adjust opacity as needed
        colorscale="matter",
        colorbar=dict(title="Sample value"),
        zmin=filtered_data['resultMeanValue'].min(),
        zmax=filtered_data['resultMeanValue'].max(),
        hovertemplate=hovertemplate
    ))
    

    # Configure the map
    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center={"lat": 42.5, "lon": 12.5},  # Focus on Italy
            zoom=5,
        ),
        margin={"r": 3, "t": 6, "l": 3, "b": 0},
        height=500,
    )
     

    return fig

# Callback per aggiornare il grafico temporale
@app.callback(
    Output('line_graph', 'figure'),
    Input('element_filter', 'value')
)
def update_line_graph(selected_element):
    filtered_data = df_geo[df_geo['eeaIndicator'] == selected_element]
    
    line_fig = go.Figure()

    line_fig.add_trace(go.Scatter(
        x=filtered_data['phenomenonTimeReferenceYear'],
        y=filtered_data['resultMeanValue'],
        mode='lines+markers',
        line=dict(color='blue')
    ))

    line_fig.update_layout(
        title="Trend nel tempo",
        xaxis_title="Anno",
        yaxis_title="Valore medio",
        height=500
    )

    return line_fig

if __name__ == '__main__':
    app.run(debug=True)