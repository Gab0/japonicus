#!/bin/python
import os
import re
import datetime

import flask
import dash
from dash.dependencies import Input, Output, Event

import dash_core_components as dcc

from flask_caching import Cache
from evaluation.gekko.statistics import epochStatisticsNames, periodicStatisticsNames

from . import graphs
from . import layout

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def run_server(webpageTitle):
    # Setup the app
    server = flask.Flask(__name__)
    app = dash.Dash(__name__, server=server, csrf_protect=False)

    app.scripts.config.serve_locally = False
    app.css.config.serve_locally = False

    dcc._js_dist[0]['external_url'] =\
        'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'

    # Add caching
    cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})
    timeout = 60 * 60  # 1 hour

    # Update function bindings;
    app.updateLocaleStatsGraph = graphs.updateLocaleStatsGraph
    app.updateWorldGraph = graphs.updateWorldGraph

    # Graphics initialization;
    app.WorldGraph = graphs.newGraphic("World Topology")
    app.GraphicList = []

    def newGraphic(name):
        app.GraphicList.append(graphs.newGraphic(name))

    app.newGraphic = newGraphic
    app.layout = layout.getLayout(webpageTitle)

    app.config['suppress_callback_exceptions'] = True

    # event triggers
    onRefreshClick = Event('refresh', 'click')
    onInterval = Event('my-interval', 'interval')

    # update graph methods
    @app.callback(Output('display-time', 'children'),
                  events=[onRefreshClick])
    def display_time():
        return str(datetime.datetime.now())

    @app.callback(Output('my-interval', 'interval'),
                  [Input('set-time', 'value')])
    def update_interval(value):
        return value


    @cache.memoize(timeout=timeout)
    @app.callback(Output('WorldGraph', 'children'),
                  events=[onRefreshClick])
    def updateGGraphs():
        return app.WorldGraph

    @cache.memoize(timeout=timeout)
    @app.callback(Output('LocaleGraphs', 'children'),
                  events=[onRefreshClick])
    def updateLGraphs():
        return app.GraphicList



    @server.route('/static/<path:path>')
    def send_css(path):
        return flask.send_from_directory(os.path.dirname(__file__), path)


    # load external css
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    externalCssListPath = os.path.join(currentDirectory,
                                       "external_css_list.txt")

    with open(externalCssListPath) as cssListFile:
        external_css = cssListFile.read().split("\n")
        external_css = list(filter(None, external_css))

    print(external_css)
    for css in external_css:
        app.css.append_css({"external_url": css})

    D = os.getcwd() + '/'
    D = re.sub(D, '', os.path.dirname(__file__))
    localCSS = os.path.join('static',
                            "promoterz_style.css")
    print(localCSS)
    # app.css.append_css({"relative_package_path": localCSS})


    # launch DASH APP
    return app
