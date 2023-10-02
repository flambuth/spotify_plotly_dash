import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

def spotify_dataframe(spotify_csv=None):
    '''
    Returns a dataframe of Spotify Top 200 charts for each day between Jan2017-Jul2021
    Converts the stream count column to an integer type.
    '''
    if spotify_csv == None:
        spotify_csv = pd.read_csv('charts.csv')
    spotify_df = spotify_csv[spotify_csv.chart == 'top200']
    spotify_df['streams'] = spotify_df['streams'].astype(int)
    return spotify_df



def regional_top_streams(df):
    '''
    Accepts a spotify charts dataframe and returns a dataframe grouped by region and artists, suming the 
    stream count across all songs
    '''
    reg_art_groups = df.groupby(['region','artist'])['streams'].sum().reset_index()
    return reg_art_groups

def regional_art_count(df):
    '''
    Accepts a spotify charts dataframe and returns a dataframe grouped by region, with a count of unique 
    artists in each region's charts
    '''
    reg_art_groups = df.groupby('region')['artist'].nunique().reset_index()
    return reg_art_groups

def personal_top_art_df(
    sp_df,
    personal_artist_list,
):
    '''
    Returns two dataframes that are filtered down to the artists found in the top200 charts that are found in the second 
    parameter: personal_artist_list
    
    
    df is grouped by region, counting unique artists in each region
    df2 is drouped by region and artists, summing the streams of all songs for each artist in each region
    '''
    sp_df['is_in_mine'] = sp_df['artist'].isin(personal_artist_list)
    df_mine = sp_df[sp_df.is_in_mine]

    df = regional_art_count(df_mine)
    df2 = regional_top_streams(df_mine)
    
    return df, df2

def write_dfs_to_csv(personal_artist_list):
    '''
    Calls functions that transform the 2 gb Spotify CSV into the three smaller CSVs that feed the input
    of the three plotly figures used in the dashboard
    '''
    sp_df = spotify_dataframe()
    sp_df.to_csv('charts200.csv')
    
    my_art_counts, my_stream_counts = personal_top_art_df(
        sp_df,
        personal_artist_list
    )
    
    my_art_counts.to_csv('my_arts.csv')
    my_stream_counts.to_csv('my_streams.csv')

    world_stream_counts = regional_top_streams(sp_df)
    world_stream_counts.to_csv('world_streams.csv')
    
def world_top_fig(region):
    try:
        df = pd.read_csv('world_streams.csv')
    except FileNotFoundError:
        df = regional_top_streams(spotify_dataframe())
        
    #parameter connects the filtering of the fig
    df = df[df.region == region]
    #I use 10 to fit into my dashboard's layout, and my server's memory
    df = df.sort_values(by='streams', ascending=False).head(10)
    
    #I set the orientation to horizontal
    fig = px.bar(
        df[::-1], 
        x="streams", 
        y="artist",
        orientation='h',
        template='plotly_dark'
        )
    #My style choices.
    fig.update_layout(
            title={
                'text':f"Top 10 Artists Total Streams in <b>{region}</b>",
                'font': {'size': 12, 'family': 'Arial', 'color': 'wheat',},
            })
    fig.update_traces(marker_color= '#015030')
    fig.update_layout(
        yaxis_title=None,
        xaxis_title=None)
    return fig



def personal_stream_fig(region=None):
    df = pd.read_csv('my_streams.csv')

    #you might want to comment this out if the artists you are looking at are smaller in value. 
    df = df[df.streams > 5000]

    if region == None:
        region = 'Belgium'
    
    # Filter to the selected region
    df = df[df.region == region]

    # I cut off the vertical bars for artists that have over 500k streams.
    df['color'] = df['streams'] > 500000
    df = df.sort_values(by='streams', ascending=True)
    

    fig = px.bar(
        df,
        x='artist',
        y='streams',
        color='color',
        color_discrete_map={True: 'green', False: 'lightgreen'},
        template='plotly_dark',
    )

    fig.add_annotation(
        text="Green bars have more than 500k streams. Hover over to get their total",
        xref="paper",
        yref="paper",
        x=0.3,
        y=1.18,
        showarrow=False,
        font=dict(size=12, color="white"),  
    )
    fig.update_layout(
        title={
            'text': f"My Favorite Artists' Total Streams in <b>{region}</b>'s Top 200",
            'font': {'size': 22, 'family': 'Arial', 'color': 'wheat',}
        }
    )
    # y-axis ticks to show only 0, midpoint, and 500k. I cut off visual for over 500k
    fig.update_yaxes(
        tickvals=[0, 250000, 500000],  
        range=[0, 500000]
    )

    # I explain the legend in the Dash.html
    fig.update_layout(
        showlegend=False,
        yaxis_title=None,
        xaxis_title=None)
    
    return fig

def personal_world_fig():
    df = pd.read_csv('my_arts.csv')
    fig = go.Figure(go.Choropleth(
    locations=df['region'],  
    locationmode='country names',
    z=df['artist'],  
    colorscale='Greens',)
                   )

    #Layout
    fig.update_geos(
        visible=False, resolution=50,
        showcountries=True,
    )
    fig.update_layout(
        geo=dict(  
            showcoastlines=True, coastlinecolor="Black",
            showland=True, landcolor="dimgrey",
                ),
        margin={"r": 90, "t": 0, "l": 20, "b": 0, 'pad':4},
        title_text='Que pongo?'
    )

    fig.update_layout(
        template="plotly_dark",
        #xaxis_title=None
        )
    return fig
