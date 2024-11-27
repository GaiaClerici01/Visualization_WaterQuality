from dash import Dash, html, dcc, Output, Input
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
import dash_bootstrap_components as dbc
import pandas as pd

# TODO
# implememt exagon map: https://plotly.com/python/hexbin-mapbox/
# on click on am exagon a graph showing only the data regarding that exagon should appear (create a comparison between exagon)
# graph should show all elememnts on click change the element shown in the map
# IDEA: how can we show actual quality?
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

df_elementScore = pd.read_csv('elementScore.csv')

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
                        dcc.Graph(id='box_graph'),
                    ),
                ],),
            ]
        )
    ]
)

# Callback to update the animated map
@app.callback(
    Output('map_graph', 'figure'),
    Input('element_filter', 'value'),
)
def update_map(selected_element):
    filtered_data = df_geo[df_geo['eeaIndicator'] == selected_element]
    element_score = int(df_elementScore.loc[df_elementScore['Element'] == selected_element, 'Score'].iloc[0])

    # Calculate global min and max of hexagon averages
    global_min = filtered_data['resultMeanValue'].min()
    global_max = filtered_data['resultMeanValue'].max()

    fig = ff.create_hexbin_mapbox(
        data_frame=filtered_data,
        lat="lat",  # Ensure these column names match your dataset
        lon="lon",
        nx_hexagon=20,  # Adjust based on your dataset
        opacity=0.5,
        labels={"color": "Mean value"},
        min_count=1,
        show_original_data=True,
        original_data_marker=dict(size=2, opacity=0.3, color="blue"),
        mapbox_style="carto-positron",
        color="resultMeanValue",
        agg_func=np.mean,
        color_continuous_scale="matter",
        range_color=[global_min, element_score],
        animation_frame="year",
    )
    ticks = np.arange(0, element_score + 1, 5).tolist()

    # Replace the last tick label with '>element_score'
    tick_labels = [str(tick) for tick in ticks]
    tick_labels[-1] = f">{element_score}"

    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 2, "l": 8, "b": 2} , # Remove extra margins
        coloraxis_colorbar=dict(
            title="Mean Value",
            tickvals=ticks,      # Use the tick positions
            ticktext=tick_labels # Use the custom labels
        )
    )
    
    return fig

@app.callback(
    Output('box_graph', 'figure'),
    Input('element_filter', 'value')
)
def update_line_graph(selected_element):
    filtered_data = df_geo[df_geo['eeaIndicator'] == selected_element]
    
    box_fig = px.box(
        filtered_data,
        x='phenomenonTimeReferenceYear',
        y='resultMeanValue',
        color='phenomenonTimeReferenceYear',
        title="Annual distribution",
        labels={'phenomenonTimeReferenceYear': 'Year', 'resultMeanValue': 'Value'},
    )

    return box_fig

if __name__ == '__main__':
    app.run(debug=True)
