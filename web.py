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
from evaluation.gekko.statistics import epochStatisticsNames, periodicStatisticsNames
import Settings

gsettings = Settings.getSettings()['Global']
settings = Settings.getSettings()['bayesian']


def load_evolution_logs(filename=None):
    FileList = os.listdir(gsettings["save_dir"])
    filename = os.path.join(gsettings["save_dir"], filename)
    df = pd.read_csv(filename, names=columns)
    return df


def update_graph(GraphName, Statistics):
    print('Loading')
    ID = [s for s in GraphName if s.isdigit()]
    '''
    try:
        df = load_evolution_logs(filename="evolution_gen_Locale%s.csv" % ''.join(ID))
        
    except:
        print("Failure to read evolution data.")
        return None
    '''
    df = pd.DataFrame(Statistics)
    annotations = []

    sNa = epochStatisticsNames
    sNb = periodicStatistcsNames
    statisticNames = { k: sNa.get(k,0) + sNb.get(k,0) for k in set(sNa) | set(sNb) }
    for W in range(len(df['dateRange'])):
        DR = df['dateRange'][W]
        if DR != None:
            annotations.append(
                {
                    'xref': 'axis',
                    'yref': 'paper',
                    'xanchor': 'left',
                    'yanchor': 'bottom',
                    'font': {'family': 'Arial', 'size': 12, 'color': 'rgb(37,37,37)'},
                    'x': W,
                    'y': 1 if not len(annotations) %
                    2 else 0.93,  # avoid label overlap;
                    'text': DR,
                }
            )
    colorSequence = [
        (188, 189, 34),
        (100, 11, 182),
        (186, 3, 34),
        (45, 111, 45),
        (66, 128, 66),
        (128, 66, 66),
    ]
    statNames = [
        'avg', 'std', 'min', 'max', 'evaluationScore', 'evaluationScoreOnSecondary'
    ]
    DATA = [
        {
            'x': df['id'],
            'y': df[statNames[S]],
            'type': 'line',
            'name': statisticsNames[statNames[S]],
            'line': {'color': 'rgb%s' % str(colorSequence[S])},
        }
        for S in range(len(statNames))
    ]
    fig = {
        'data': [
            {
                'x': [0, df["id"]],
                'y': [0],
                'type': 'line',
                'name': 'markzero',
                'line': {'color': 'rgb(0,0,0)'},
            }
        ] +
        DATA,
        'layout': {'title': 'Evolution at %s' % GraphName, 'annotations': annotations},
    }
    return fig


def newGraphic(name):
    G = dcc.Graph(id=name)
    G.Active = True
    return G


def run_server():
    # Setup the app
    server = flask.Flask(__name__)
    app = dash.Dash(__name__, server=server, csrf_protect=False)
    app.scripts.config.serve_locally = False
    dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'
    # Add caching
    cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})
    timeout = 60 * 60  # 1 hour
    # Controls
    app.update_graph = update_graph
    # Layout
    app.GraphicList = []
    app.newGraphic = lambda name: app.GraphicList.append(newGraphic(name))
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.H2(
                        'japonicus Evolution Statistics',
                        style={'padding-top': '20', 'text-align': 'center'},
                    ),
                    html.Div(
                        [
                            dcc.Interval(id='my-interval'),
                            dcc.RadioItems(
                                id='set-time',
                                value=5000,
                                options=[
                                    {'label': 'Every 60 seconds', 'value': 60000},
                                    {'label': 'Every 15 seconds', 'value': 15000},
                                    {
                                        'label': 'Every hour', 'value': 60 * 60 * 1000
                                    },  # or just every hour
                                ],
                            ),
                        ]
                    ),
                    html.Div(id='display-time'),
                ]
            ),
            html.Div(id='Graphs'),
        ],
        style={'width': '1100', 'margin-left': 'auto', 'margin-right': 'auto', 'font-family': 'overpass', 'background-color': '#F3F3F3'},
        # Traces>Color
    )
    app.config['suppress_callback_exceptions'] = True

    @app.callback(
        Output('display-time', 'children'), events=[Event('my-interval', 'interval')]
    )
    def display_time():
        return str(datetime.datetime.now())

    @app.callback(Output('my-interval', 'interval'), [Input('set-time', 'value')])
    def update_interval(value):
        return value

    @cache.memoize(timeout=timeout)
    @app.callback(
        Output('Graphs', 'children'), events=[Event('my-interval', 'interval')]
    )
    def updateGraphs():
        '''
        for F in range(len(app.GraphicList)):
            if app.GraphicList[F].Active:
                app.GraphicList[F].__setattr__('figure', update_graph(app.GraphicList[F].id))
        '''
        return app.GraphicList

    # External css
    external_css = [
        "https://fonts.googleapis.com/css?family=Overpass:400,400i,700,700i",
        "https://cdn.rawgit.com/plotly/dash-app-stylesheets/c6a126a684eaaa94a708d41d6ceb32b28ac78583/dash-technical-charting.css",
    ]
    for css in external_css:
        app.css.append_css({"external_url": css})
    # Run the Dash app
    if __name__ == '__main__':
        app.server.run(debug=True, host='0.0.0.0')
    else:  # this way it integrates with main interface without child procs across pipes,
        return app


if __name__ == '__main__':
    run_server()
