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
                        #dcc.Graph(id='box_graph'),
                        dcc.Graph(id='violin_graph'),
                    ),
                ],),
            ]
        )
    ]
)

@app.callback(
    Output('map_graph', 'figure'),
    Input('element_filter', 'value'),
)
def update_map(selected_element):
    filtered_data = df_geo[df_geo['eeaIndicator'] == selected_element]
    element_score = float(df_elementScore.loc[df_elementScore['Element'] == selected_element, 'Score'].iloc[0])

    # Calculate the step size for 5 evenly spaced ticks between 0 and element_score
    step = element_score / 5

    # Create 5 ticks from 0 to element_score
    ticks = [i * step for i in range(5)]  # Creates 5 values: [0, step, 2*step, 3*step, 4*step]

    # Create labels for the ticks
    tick_labels = [f"{tick:.1f}" for tick in ticks]  # Format tick labels to 1 decimal point
    
    # Add '>element_score' as the last label
    tick_labels.append(f">{element_score:.1f}")  # Append '>element_score' as the last label

    # Define color scale (default pastel colors)
    color_scale = [
        'rgb(100, 150, 255)',  # Light Blue (low values)
        'rgb(180, 100, 255)',  # Soft Purple (medium values)
        'rgb(255, 100, 100)'   # Soft Red (high values)
    ]
    
    # Reverse the color scale if the selected element is "Secchi Depth"
    if selected_element == 'Secchi depth':
        color_scale = color_scale[::-1]  # Reverse the color scale

    # Create the hexbin map
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
        color_continuous_scale=color_scale,  # Apply reversed or normal color scale
        range_color=[0, element_score],  # Set the color range from 0 to element_score
        animation_frame="year",
    )

    # Update the layout to add a custom colorbar
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 2, "l": 8, "b": 2},  # Remove extra margins
        coloraxis_colorbar=dict(
            title="Mean Value",
            tickvals=ticks + [element_score],  # Include element_score as the final tick
            ticktext=tick_labels,  # Use the custom labels (including '>element_score')
        )
    )

    return fig


'''
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
'''

@app.callback(
    Output('violin_graph', 'figure'),
    Input('element_filter', 'value')
)
def update_violin_graph(selected_element):
    filtered_data = df_geo[df_geo['eeaIndicator'] == selected_element]
    
    # Get the element score (threshold value)
    element_score = float(df_elementScore.loc[df_elementScore['Element'] == selected_element, 'Score'].iloc[0])
    
    # Define a set of blue shades (lighter to darker)
    blue_shades = [
        'rgb(173, 216, 230)',  # Light Blue
        'rgb(100, 149, 237)',  # Cornflower Blue
        'rgb(70, 130, 180)',   # Steel Blue
        'rgb(0, 0, 205)'       # Medium Blue
    ]
    
    # Create the violin plot with blue shades
    violin_fig = px.violin(
        filtered_data,
        x='phenomenonTimeReferenceYear',
        y='resultMeanValue',
        color='phenomenonTimeReferenceYear',  # Color by year or other dimension
        color_discrete_sequence=blue_shades,  # Apply custom blue shades
        box=True,
        points="all",  # Show all points
        title="Annual Distribution",
        labels={'phenomenonTimeReferenceYear': 'Year', 'resultMeanValue': 'Value'},
    )

    # Remove the color legend (since the x-axis already represents the years)
    violin_fig.update_layout(
        showlegend=False,  # Hide the legend
        shapes=[dict(
                type="line",
                x0=0,
                x1=1,
                y0=element_score,
                y1=element_score,
                line=dict(
                    color="black",  # Black line for the threshold
                    width=2,
                    dash="dash"
                ),
                xref="paper",  # Use paper coordinates for x-axis
                yref="y"  # Use the y-axis for vertical positioning
            )],
        annotations=[dict(
                x=1.10,  # Move text to the right of the plot
                y=element_score,  # Position the text at the threshold line
                xref="paper",  # Use paper coordinates for x-axis
                yref="y",  # Use the y-axis for positioning vertically
                text=f": {element_score}",
                showarrow=False,
                font=dict(size=12, color="red"),
                align="left",
                valign="bottom",
            )]
    )

    return violin_fig



if __name__ == '__main__':
    app.run(debug=True)
