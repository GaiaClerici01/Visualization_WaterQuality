from dash import Dash, html, dcc, Output, Input
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd

# TODO
# implememt exagon map: https://plotly.com/python/hexbin-mapbox/
# on click on am exagon a graph showing only the data regarding that exagon should appear (create a comparison between exagon)
# graph should show all elememnts on click change the element shown in the map
# LATER: try to do a layered map to see if there's a corlleation between industrial area and water quality bweing bad

# Load data
df_sites = pd.read_csv('monitoringSite.csv')
df_data22 = pd.read_csv('./aggregatedDataPerYear/aggregateddata2022.csv')
df_data22['year'] = 2022
df_data21 = pd.read_csv('./aggregatedDataPerYear/aggregateddata2021.csv')
df_data21['year'] = 2021
df_data20 = pd.read_csv('./aggregatedDataPerYear/aggregateddata2020.csv')
df_data20['year'] = 2020
df_data19 = pd.read_csv('./aggregatedDataPerYear/aggregateddata2019.csv')
df_data19['year'] = 2019
df_data = pd.concat([df_data19, df_data20, df_data21, df_data22])

df_geo = pd.merge(df_sites, df_data, on='monitoringSiteIdentifier')

# Extract unique indicators
df_elements = df_geo[['eeaIndicator']].drop_duplicates()

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
           [
                dbc.Col(
                    dcc.Graph(id='map_graph'),
                    width={"size": 8},
                ),
                dbc.Col([
                    dbc.Row(
                       dcc.Dropdown(
                            id='element_filter',
                            options=[
                                {'label': i, 'value': i} for i in df_elements['eeaIndicator']
                            ],
                            value='Nitrate',
                            clearable=False,
                            style={
                                "margin-bottom": "10px",
                                "margin-top": "10px",
                                "width": "90%",  # Adjust width
                                "margin-left": "auto",
                                "margin-right": "auto"
                            }
                        )
                    ),
                    dbc.Row(
                        dcc.Graph(id='line_graph'),
                    ),
                ],),
            ]
        )
    ]
)

# Callback to update the animated map
@app.callback(
    Output('map_graph', 'figure'),
    Input('element_filter', 'value')
)
def update_map(selected_element):
    filtered_data = df_geo[df_geo['eeaIndicator'] == selected_element]

    # Create the map figure
    years = sorted(filtered_data['year'].unique())

    # Traces for the initial year
    initial_data = filtered_data[filtered_data['year'] == years[0]]
    hovertemplate = '<b>%{text}</b><br>Value: %{z:.2f}<extra></extra>'
    #TODO understand which trace is better
    traces = [
        go.Scattermapbox(
            lat=initial_data['lat'],
            lon=initial_data['lon'],
            mode='markers',
            marker=dict(
                size=8,
                color=initial_data['resultMeanValue'],
                colorscale='matter',
                cmin=filtered_data['resultMeanValue'].min(),
                cmax=filtered_data['resultMeanValue'].max(),
            ),
            text=initial_data['waterBodyName'],
            name=str(years[0]),
            hovertemplate=hovertemplate
        ),
        go.Densitymapbox(
            lat=initial_data['lat'],
            lon=initial_data['lon'],
            z=initial_data['resultMeanValue'],
            radius=8,
            opacity=0.7,
            colorscale='matter',
            colorbar=dict(title="Sample value"),
            zmin=filtered_data['resultMeanValue'].min(),
            zmax=filtered_data['resultMeanValue'].max(),
            text=initial_data['waterBodyName'],
            name=f"Density {years[0]}",
            hovertemplate=hovertemplate
        )
    ]

    # Frames for each year
    frames = [
        go.Frame(
            data=[
                go.Scattermapbox(
                    lat=filtered_data[filtered_data['year'] == year]['lat'],
                    lon=filtered_data[filtered_data['year'] == year]['lon'],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=filtered_data[filtered_data['year'] == year]['resultMeanValue'],
                        colorscale='matter',
                        cmin=filtered_data['resultMeanValue'].min(),
                        cmax=filtered_data['resultMeanValue'].max(),
                    ),
                    text=filtered_data[filtered_data['year'] == year]['waterBodyName']
                ),
                go.Densitymapbox(
                    lat=filtered_data[filtered_data['year'] == year]['lat'],
                    lon=filtered_data[filtered_data['year'] == year]['lon'],
                    z=filtered_data[filtered_data['year'] == year]['resultMeanValue'],
                    radius=8,
                    opacity=1,
                    colorscale='matter',
                    zmin=filtered_data['resultMeanValue'].min(),
                    zmax=filtered_data['resultMeanValue'].max(),
                    text=filtered_data[filtered_data['year'] == year]['waterBodyName'],
                )
            ],
            name=str(year)
        )
        for year in years
    ]

    # Configure map layout
    layout = go.Layout(
    mapbox=dict(
        style="carto-darkmatter",
        center={"lat": 42.5, "lon": 12.5},  # Focus on Italy
        zoom=5,
    ),
    margin={"r": 3, "t": 6, "l": 3, "b": 0},
    height=700,
    sliders=[
        {
            "active": 0,
            "pad": {"t": 50, "l": 20, "b":10},  # Adds padding above the slider for the buttons
            "x": 0.1,  # Adjust the position of the slider to fit the buttons
            "y": -0.05,
            "len": 0.8,  # Adjust the length of the slider line
            "steps": [
                {
                    "method": "animate",
                    "args": [[str(year)], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate"}],
                    "label": str(year)
                }
                for year in years
            ],
            "currentvalue": {
                "visible": True,
                "prefix": "Year: ",  # Label for the current value
                "xanchor": "center",
                "font": {"size": 14},
            },
        }
    ],
    updatemenus=[
        {
            "type": "buttons",
            "x": 0.57,  # Position the buttons next to the slider
            "y": 0.05,  # Align the buttons at the beginning of the slider
            "direction": "left",
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                    "label": "▶",  
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                    "label": "⏸",
                    "method": "animate"
                }
            ],
            "showactive": True,
            "pad": {"r": 10, "t": 50},  # Adjust padding for aesthetics
        }
    ]   
    )


    # Build and return the figure
    fig = go.Figure(data=traces, layout=layout, frames=frames)
    return fig

# Callback per aggiornare il grafico temporale
@app.callback(
    Output('line_graph', 'figure'),
    Input('element_filter', 'value')
)
def update_line_graph(selected_element):
    filtered_data = df_geo[df_geo['eeaIndicator'] == selected_element]
    
    line_fig = go.Figure()
    filtered_data = filtered_data.groupby('phenomenonTimeReferenceYear')['resultMeanValue'].mean().reset_index()

    line_fig.add_trace(go.Scatter(
        x=filtered_data['phenomenonTimeReferenceYear'],
        y=filtered_data['resultMeanValue'],
        mode='lines+markers',
        line=dict(color='blue')
    ))

    line_fig.update_layout(
        title="Annual trend",
        xaxis_title="Year",
        yaxis_title="Value",
    )

    return line_fig

if __name__ == '__main__':
    app.run(debug=True)
