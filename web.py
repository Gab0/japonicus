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
    columns = ['id', 'avg', 'std', 'min', 'max']
    filename = os.path.join(gsettings["save_dir"], filename)
    df = pd.read_csv(filename, names=columns)
    return df

def run_server():
    # Setup the app
    server = flask.Flask(__name__)
    #server.secret_key = os.environ.get('secret_key', 'secret')
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
                    'gekkoJaponicus Evolution Statistics Over Time',
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
        style={
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
        fig = {
            'data': [
                {'x': df["id"], 'y': df["avg"], 'type': 'line', 'name': 'Average profit', 'color':'rgb(22, 96, 167)'},
                {'x': df["id"], 'y': df["std"], 'type': 'line', 'name': 'Deviation'},
                {'x': df["id"], 'y': df["min"], 'type': 'line', 'name': 'Minimum profit'},
                {'x': df["id"], 'y': df["max"], 'type': 'line', 'name': 'Maximum profit'},
            ],
            'layout': {
                'title': 'Evolution Data Visualization'
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
        #app.server.run()
    else: # this way it integrates with main interface without child procs across pipes,
        return app

if __name__ == '__main__':
    run_server()

