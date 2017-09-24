#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import pandas as pd
import os

import flask
import dash
from dash.dependencies import Input, Output, Event
import dash_core_components as dcc
import dash_html_components as html
from flask_caching import Cache

import Settings

gsettings = Settings.getSettings()['global']
settings = Settings.getSettings()['bayesian']

def load_evolution_logs(filename="evolution_gen.csv"):
    columns = ['id', 'avg', 'std', 'min', 'max', 'dateRange']
    filename = os.path.join(gsettings["save_dir"], filename)
    df = pd.read_csv(filename, names=columns)
    return df

def run_server():
    # Setup the app
    server = flask.Flask(__name__)
    #server.secret_key = os.environ.get('secret_http://localhost:500/key', 'secret')
    app = dash.Dash(__name__, server=server, csrf_protect=False)

    app.scripts.config.serve_locally = False
    dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'

    # Add caching
    cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})
    timeout = 60 * 60  # 1 hour

    # Controls

    # Layout
    app.layout = html.Div(
        [
            html.Div([
                html.H2(
                    'japonicus Evolution Statistics',
                    style={'padding-top': '20', 'text-align': 'center'}
                ),
                html.Div([
                    dcc.Interval(id='my-interval'),
                    dcc.RadioItems(id='set-time',
                        value=5000,
                        options=[
                            {'label': 'Every 5 seconds', 'value': 5000},
                            {'label': 'Off', 'value': 60*60*1000} # or just every hour
                        ]),
                    ]),
                html.Div(id='display-time'),
                ]),
            dcc.Graph(id='output')
        ],
        style={#Traces>Color
            'width': '1100',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'font-family': 'overpass',
            'background-color': '#F3F3F3'
        }
    )

    @app.callback(
        Output('display-time', 'children'),
        events=[Event('my-interval', 'interval')])
    def display_time():
        return str(datetime.datetime.now())


    @app.callback(
        Output('my-interval', 'interval'),
        [Input('set-time', 'value')])
    def update_interval(value):
        return value

    @cache.memoize(timeout=timeout)
    @app.callback(
        Output('output', 'figure'),
        events=[Event('my-interval', 'interval')])
    def update_graph():
        print('Loading')
        df = load_evolution_logs()
        annotations = []
        for W in range(len(df['dateRange'])):
            DR = df['dateRange'][W]
            if DR != 'None':
                annotations.append({
                    'xref':'axis',
                    'yref':'paper',
                    'xanchor': 'left',
                    'yanchor': 'bottom',
                    'font': {
                        'family': 'Arial',
                        'size': 12,
                        'color': 'rgb(37,37,37)'
                    },
                    'x': W,
                    'y': 1 if not len(annotations) % 2 else 0.93, # avoid label overlap;
                    'text': DR
                })

        fig = {
            'data': [
                {'x': df["id"], 'y': df["avg"],
                 'type': 'line', 'name': 'Average profit',
                  'line': {'color': 'rgb(188, 189, 34)'}},

                {'x': df["id"], 'y': df["std"],
                 'type': 'line', 'name': 'Deviation',
                 'line': {'color': 'rgb(100, 11, 182)'}},

                {'x': df["id"], 'y': df["min"],
                 'type': 'line', 'name': 'Minimum profit',
                 'line': {'color': 'rgb(186, 3, 34)'}},

                {'x': df["id"], 'y': df["max"],
                 'type': 'line', 'name': 'Maximum profit',
                 'line': {'color': 'rgb(45, 111, 45)'}}
            ],
            'layout': {
                'title': 'Evolution Data Over Time',
                'annotations': annotations
            }
        }
        return fig


    # External css

    external_css = ["https://fonts.googleapis.com/css?family=Overpass:400,400i,700,700i",
                    "https://cdn.rawgit.com/plotly/dash-app-stylesheets/c6a126a684eaaa94a708d41d6ceb32b28ac78583/dash-technical-charting.css"]

    for css in external_css:
        app.css.append_css({"external_url": css})

    # Run the Dash app
    if __name__ == '__main__':
        app.server.run(debug=True)

    else: # this way it integrates with main interface without child procs across pipes,
        return app

if __name__ == '__main__':
    run_server()

