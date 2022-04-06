from dash import html, Input, Output, State
from dash import dcc, dash_table
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

from flask import Flask, request,jsonify
from flask_cors import CORS

from datetime import date,  datetime, timedelta
import pandas as pd
import numpy as np
import copy 

from controls import MPAA, GENRES, GENRES_COLORS
import helper

MPAA_options = [ {"label": str(MPAA[rating]), "value": str(rating)} for rating in MPAA ]
GENRES_options = [ {"label": str(GENRES[genre]), "value": str(genre)} for genre in GENRES ]

global BO_data
BO_data = pd.read_csv('data/boxoffice2017_2019.csv', encoding = 'ISO-8859-1')
BO_data['MPAA'].fillna('Not Rated', inplace=True)
BO_data['genres'].fillna('Unknown', inplace=True)
data_numeric=BO_data[['domestic_revenue','world_revenue','opening_revenue','opening_theaters','budget','release_days']].replace('[\$,]', '', regex=True).astype(float)
data_numeric['domestic_revenue_log'] = np.log10(data_numeric['domestic_revenue'])
data_numeric['world_revenue_log'] = np.log10(data_numeric['world_revenue'])
data_numeric['opening_revenue_log'] = np.log10(data_numeric['opening_revenue'])
data_numeric['budget_log'] = np.log10(data_numeric['budget'])
data_numeric['genres'] = BO_data['genres']
data_numeric['MPAA'] = BO_data['MPAA']
data_numeric['title'] = BO_data['title']
data_numeric['distributor'] = BO_data['distributor']

# data_numeric.drop(['domestic_revenue', 'world_revenue','opening_revenue','budget'], axis=1, inplace=True)


server = Flask(__name__)
app = dash.Dash(__name__, server=server,
                title="Box Office Data Explorer",
                update_title='Updating...',
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
CORS(server) 

plot_layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=50, r=30, b=100, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
)


app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        # Headersection
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("logo.png"),
                            id="plotly-image",
                            style={
                                "height": "80px",
                                "width": "auto",
                                "marginBottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "2017-2019 Box Office Data Analytics",
                                    style={"marginBottom": "0px"},
                                )

                            ]
                        )
                    ],
                    className="one-third column",
                    id="title",
                ),

            ],
            id="header",
            className="row flex-display",
            style={"marginBottom": "25px"},
        ),
        html.Div([ dcc.Loading(id="loading-1", type="default", children=html.Div(id="loading-output"))]), 
        
        html.Div([
        # FilterSection
        html.Div(
            [

                html.H3("MPAA", className="control_label"),
                html.P("Filter Movies by MPAA rating:", className="control_label"),
                dcc.Dropdown(
                    id="mpaa_rating",
                    options=MPAA_options,
                    multi=True,
                    value=list(MPAA.keys()),
                    className="dcc_control",
                ),
                html.H3("Genres", className="control_label"),
                html.P("Filter Movies by Genres:", className="control_label"),
                dcc.Dropdown(
                    id="genres",
                    options=GENRES_options,
                    multi=True,
                    value=list(GENRES.keys()),
                    className="dcc_control",
                ),

            ],
            className="pretty_container four columns",
            id="cross-filter-options"
        ),
        # ContentSection
        html.Div([
                html.Div(
                        [html.H3('Do certain genres make better return?', className="control_label"), 
                        dcc.Graph(id="budget_revenue_scatterplot")],
                        ),
                html.Div([
                    html.H3('Which studio made the best return?'),
                    html.P('We look at which studio makes the best return by looking at their world-wide revenue to budget ratio'),
                    dcc.Graph(id="studio_world_revenue_piechart", className="pretty_container five columns",),
                    dcc.Graph(id="studio_world_revenue_histogram", className="pretty_container five columns",)
                ])],
                # id="right-column",
                style={"display": "flex", "flexDirection": "column"},
                className="pretty_container eight columns",
                ),
         
        ],
        style={"display": "flex", "flexDirection": "row"})
    ],
    id="page-content",
    style={"display": "flex", "flexDirection": "column"},
)


#----------------------------------------
# Call back section
#----------------------------------------
@app.callback(
    Output("budget_revenue_scatterplot", "figure"),
    [Input('mpaa_rating', 'value'),
    Input('genres', 'value')])
def make_budget_revenue_scatterplot(mpaa_rating, genres):
    layout_aggregate = copy.deepcopy(plot_layout)
    data_numericf = helper.filter_movies_by_ratings(data_numeric, mpaa_rating)

    fig = go.Figure()
    for genre in genres:
        
        data_numericff = helper.filter_movies_by_genre(data_numericf, [GENRES[genre]])
        fig.add_trace(
            go.Scatter(mode="markers",
                x=data_numericff["budget"], 
                y=(data_numericff['opening_revenue']),
                name = genre,
                text=data_numericff['title'],
                marker=dict(
                color=GENRES_COLORS[genre], 
                colorscale='Viridis',
                line_width=1, 
                )
                ))

    fig.update_xaxes(type="log", title_text='Budget')
    fig.update_yaxes(type="log", title_text='Opening Revenue')
    # fig.update_layout(title_text='2017-2019 Movie Budget VS Opening Revenue')
    return fig


@app.callback(
    Output("studio_world_revenue_piechart", "figure"),
    [Input('mpaa_rating', 'value'),
    Input('genres', 'value')])
def make_distributor_pie_graph(mpaa_rating, genres):
    layout_aggregate = copy.deepcopy(plot_layout)
    data_numericf = helper.filter_movies_by_ratings(data_numeric, mpaa_rating)

    distributors= data_numericf.groupby(['distributor']).sum()
    distributors = distributors[distributors['budget']>0]

    distributors['return'] = distributors['world_revenue']/distributors['budget']
    distributors = distributors.sort_values('world_revenue', ascending=False)

    data = [dict(type = 'pie',
                labels=distributors.head(10).index.tolist(), 
                values=distributors.head(10)['world_revenue'],
                name = 'Pie Chart',
                hole=0.5,
                showlegend=True,
                legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1)
                )
                ]


    figure = dict(data=data,layout=layout_aggregate )
    
    return figure

@app.callback(
    Output("studio_world_revenue_histogram", "figure"),
    [Input('mpaa_rating', 'value'),
    Input('genres', 'value')])
def make_distributor_histogram(mpaa_rating, genres):
    layout_aggregate = copy.deepcopy(plot_layout)
    data_numericf = helper.filter_movies_by_ratings(data_numeric, mpaa_rating)

    distributors= data_numericf.groupby(['distributor']).sum()
    distributors = distributors[distributors['budget']>0]
    distributors['return'] = distributors['world_revenue']/distributors['budget']
    distributors = distributors.sort_values('return', ascending=False)

    data = [dict(type = 'bar',
                x=distributors.head(10).index.tolist(), 
                y=distributors.head(10)['return'])
                ]

    layout_aggregate['yaxis'] = dict(
        title='World Revenue/Budget Ratio',
        titlefont_size=16,
        tickfont_size=14,)
    figure = dict(data=data,layout=layout_aggregate )

    
    return figure

if __name__ == '__main__':
    
    app.run_server(debug=False)

