import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from funcs import *
#################################################

#This should be executed before operating this dashboard. 
#write_dfs_to_csv(my_art_list)

#LAYOuts
#I set up a div with just the peronsal bar graph, then a second div that has two graphs sharing a row
#I call these in my actual app.layout
graph1 = html.Div(
dcc.Graph(
    id="my_bar_plot",
    figure=personal_stream_fig('Belgium'),
    config={'displayModeBar': False}
),
style={'border-radius': '15px', 'overflow': 'hidden', 'margin-bottom': '10px', 'border': '3px solid #238a6b'}
)

row_with_graphs = dbc.Row([
dbc.Col(
    html.Div(
        dcc.Graph(
            id='the_world_plot',
            figure=personal_world_fig(),
            config={'displayModeBar': False}
        ),
        style={'border-radius': '15px', 'overflow': 'hidden', 'margin-top': '10px', 'border': '3px solid #238a6b'}
    ),
    width={'size': 10, 'offset': -1}  
),
dbc.Col(
    html.Div(
        dcc.Graph(
            id='hbar_plot',
            figure=world_top_fig('Belgium'),  
            config={'displayModeBar': False}
        ),
        style={'border-radius': '15px', 'overflow': 'hidden', 'margin-top': '10px', 'border': '3px solid #238a6b'}
    ),
    width={'size': 2, 'offset': 0}  
)
])

# Create the Dash app instance. A dash can work as a temporary flask server.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# THe stack of HTM Divs that make the HTML content displayed on a web browser
app.layout = html.Div(
        style={'backgroundColor': 'black'},
        children=[
            html.Div(
                [
                    html.H1("My Spotify Tastes Around The World", style={'textAlign': 'center', 'color':'#238a6b'}),
                    html.P("World Data is represented by daily top200 Spotify charts between 2017-2021.", style={'textAlign': 'center', 'color':'wheat'}),
                ],
                style={'background-color': '#111111', 'border-radius': '15px', 'padding': '19px', 'margin-bottm': '20px', 'border': '2px solid #238a6b'},
            ),
            
            
            # Use dbc.Container to wrap both Plotly figures
            dbc.Container([
            graph1,
            html.H1(id='selected-country-display', style={'textAlign': 'center', 'color': 'white'}),
            html.H4(children="Each green country can be clicked on to see artists' Spotify presence there", style={'color': 'wheat', 'textAlign': 'center'}),
            html.P(children="Map color intensity is a measure of unique artists I like found in each region's Top 200 charts between 2017-2021", style={'color': 'white', 'textAlign': 'center'}),
            row_with_graphs,
        ], fluid=True),  # Set fluid=True to make the container responsive
            
            html.Div(id='selected-country', style={'display': 'none'}),
        ]
    )

#Callbacks are used to transfer values between elements in the dashboard

#The clickData on the world updates a variable that two other figures use as an input.
@app.callback(
    Output('selected-country', 'children'),
    Input('the_world_plot', 'clickData')
)
def update_selected_country(clickData):
    if clickData is not None and 'points' in clickData:
        selected_country = clickData['points'][0]['location']
        return selected_country
    return 'Belgium'  # Default value if no country is selected


#The two bar charts react to the first callback
@app.callback(
    Output('my_bar_plot', 'figure'),
    Output('hbar_plot', 'figure'),
    Input('selected-country', 'children')
)
def update_graph(selected_country):
    if not selected_country:
        selected_country = 'Belgium'  # Default value if no country is selected

    fig_bar_chart = personal_stream_fig(selected_country)
    fig_hbar = world_top_fig(selected_country)

    return fig_bar_chart, fig_hbar

#The output of the first callback modifys the big H1 test in the center of the HTML divs
@app.callback(
    Output('selected-country-display', 'children'),
    Input('selected-country', 'children')
)
def update_selected_country_display(selected_country):
    return selected_country

#this line instantiates the flask server that runs on localhost:8050
if __name__ == '__main__':
    app.run_server(debug=True)

