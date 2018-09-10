#!/bin/python
import os
import re
import datetime

import flask
import dash
from dash.dependencies import Input, Output, Event

import dash_core_components as dcc
import dash_html_components as html

from flask_caching import Cache
from evaluation.gekko.statistics import epochStatisticsNames, periodicStatisticsNames

from . import graphs
from . import layout

import functools
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def run_server(webpageTitle):
    # Setup the app
    server = flask.Flask(__name__)
    app = dash.Dash(__name__, server=server, csrf_protect=False)

    app.scripts.config.serve_locally = False
    app.css.config.serve_locally = False

    app.webpageTitle = webpageTitle

    timeout = 60 * 60  # 1 hour

    app.startTime = datetime.datetime.now()

    # Graph Update function bindings;
    app.updateLocaleGraph = graphs.updateLocaleGraph
    app.updateWorldGraph = graphs.updateWorldGraph
    app.updateEvalBreakGraph = graphs.updateEvalbreakGraph

    # Graphics initialization and input points against World;
    # why is this placeholder required? ;(
    app.WorldGraph = dcc.Graph(id='WorldGraph', figure={})
    app.LocaleGraphs = []
    app.EvalBreakGraph = []

    app.resultParameters = []
    app.epochInfo = ""
    app.layout = functools.partial(layout.getLayout, app)

    app.config['suppress_callback_exceptions'] = False

    # event triggers
    onRefreshClick = Input('refresh-button', 'n_clicks')
    onInterval = Event('my-interval', 'interval')

    """
    # update graph methods
    @app.callback(Output('last-refresh', 'children'),
                  [Input('refresh-button', 'n_clicks')])
    def display_time(w):
        print("Refreshing graphical interface graphics.")
        return str(datetime.datetime.now())

    @app.callback(Output('WorldGraph', 'children'),
                  [Input('refresh-button', 'n_clicks')])
    def updateGGraphs(w):
        return [app.WorldGraph]

    @app.callback(Output('LocaleGraphs', 'children'),
                  [Input('refresh-button', 'n_clicks')])
    def updateLGraphs(w):
        return [app.GraphicList]
    """

    # SELECT PAGE;
    @app.callback(dash.dependencies.Output('page-content', 'children'),
                  [dash.dependencies.Input('url', 'pathname')])
    def display_page(pathname):
        if re.findall("evalbreak", str(pathname)):
            return layout.getEvalbreak(app)
        if re.findall("results", str(pathname)):
            return layout.getResults(app)
        else:
            return layout.getCommon(app)

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

    for css in external_css:
        app.css.append_css({"external_url": css})

    # launch DASH APP
    return app
