#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import datetime
import numpy as np
import pandas as pd
import json
import os

import quantmod as qm

import flask
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from flask_caching import Cache

#from plotInfo import plotEvolutionSummary

import gekkoWrapper
import Settings
import coreFunctions
import evolution_bayes

gsettings = Settings.getSettings()['global']
settings = Settings.getSettings()['bayesian']

MA_SMA, MA_EMA, MA_WMA, MA_DEMA, MA_TEMA, MA_TRIMA, MA_KAMA, MA_MAMA, MA_T3 = range(9)
rename = {
        "DEMA": {
                "long": "timeperiod",
                },
        "MACD": {
                "short": "fastperiod",
                "long": "slowperiod",
                "signal": "signalperiod",
                },
        "PPO": {
                "short": "fastperiod",
                "long": "slowperiod",
                "signal": "signalperiod",
                },
        "RSI": {
                "interval": "timeperiod",
                },
        "StochRSI": {
                "interval": "timeperiod",
                },
        "CCI": {
                "interval": "timeperiod",
                },
        }
indicators = rename.keys()

def talib_dict(params):
    # dict key rename
    newparams = {}
    for k in rename.keys():
        newparams[k] = {}
        if k == "STOCHRSI":
            k = "StochRSI"
        for old, new in rename[k.upper()].items():
            newparams[k.upper()][new] = params[k].pop(old)
    # add matype
    newparams["PPO"]["matype"] = MA_EMA
    #newparams["STOCHRSI"]["matype"] = MA_EMA

    return newparams

def run_server():

    # Setup the app
    server = flask.Flask(__name__)
    #server.secret_key = os.environ.get('secret_key', 'secret')
    app = dash.Dash(__name__, server=server, csrf_protect=False)

    app.scripts.config.serve_locally = False
    dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'

    # Setup config
    responses, configs = get_json()
    def setup_config(filename=None):
        if filename != None and filename in responses:
            config_filename = filename.replace("response", "config")
            res = load_json(filename)
            gekko_config = load_json(config_filename)
        else:
            res = load_json(responses[-1])
            gekko_config = load_json(configs[-1])
        filename = gsettings['configFilename']
        configjs = Settings.get_configjs(filename)
        config = {k:v for k,v in configjs.items() if k in indicators}
        config2 = {k:v for k,v in gekko_config["gekkoConfig"].items() if k in indicators}
        config.update(config2.copy())
        strategy = gekko_config["gekkoConfig"]["tradingAdvisor"]["method"]
        return strategy, config, res

        # Setup chart
    def setup_chart(res):
        candles = pd.DataFrame.from_dict(res['candles'])
        candles["start"] = pd.to_datetime(candles["start"])
        candles.index = candles["start"]
        trades = pd.DataFrame.from_dict(res['trades'])
        trades["start"] = pd.to_datetime(trades["date"])
        trades["color"] = 'rgba(0, 0, 0, 0.)'
        trades["symbol"] = 'triangle-down'
        trades.loc[trades.action.str.match("buy"), "color"] = 'rgba(255, 182, 193, .5)'
        trades.loc[trades.action.str.match("sell"), "color"] = 'rgba(182, 193, 255, .5)'
        trades.loc[trades.action.str.match("buy"), "symbol"] = 'triangle-up'
        trade_scatter = dict(
                        x=trades["start"],
                        y=trades["price"],
                        name=trades["action"],
                        mode="markers",
                        marker = dict(
                            symbol = trades["symbol"],
                            size = 15,
                            color = trades["color"],
                            showscale=True,
                        )
                        )
        return candles, trade_scatter

    strategy, config, res = setup_config()
    candles, trade_scatter = setup_chart(res)

    # Add caching
    cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})
    timeout = 60 * 60  # 1 hour

    # Controls
    src = dict(
        index = 'start',
        op = 'open',
        hi = 'high',
        lo = 'low',
        cl = 'close',
        aop = None,
        ahi = None,
        alo = None,
        acl = None,
        vo = 'volume',
        di = None,
    )

    logs = responses
    logs = [dict(label=str(log), value=str(log))
               for log in logs]

    # Dynamic binding
    functions = dir(qm.ta)[9:-4]
    functions = [dict(label=str(function[4:]), value=str(function))
                 for function in functions]

    # Layout
    app.layout = html.Div(
        [
            html.Div([
                html.H2(
                    'gekkoJaponicus Charts',
                    style={'padding-top': '20', 'text-align': 'center'}
                ),
                html.Div([
                        html.Label('Select log:'),
                        dcc.Dropdown(
                            id='dropdown',
                            options=logs,
                            value=str(responses[0]),
                        )],
                    style={
                        'width': '510', 'display': 'inline-block',
                        'padding-left': '40', 'margin-bottom': '20'}
                ),
                html.Div([
                        html.Label('Select technical indicators:'),
                        dcc.Dropdown(
                            id='multi',
                            options=functions,
                            multi=True,
                            value=["add_"+strategy.upper()],
                        )],
                    style={
                        'width': '510', 'display': 'inline-block',
                        'padding-right': '40', 'margin-bottom': '20'}
                ),
            ]),
            html.Div([
                    html.Label('Specify parameters of technical indicators:'),
                    dcc.Input(
                        id='arglist',
                        style={'height': '32', 'width': '1020'},
                        value=json.dumps(config),
                    )],
                id='arg-controls',
                style={'display': 'none'}
            ),
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


    @app.callback(Output('arg-controls', 'style'), [Input('multi', 'value')])
    def display_control(multi):
        if not multi:
            return {'display': 'none'}
        else:
            return {'margin-bottom': '20', 'padding-left': '40'}


    @cache.memoize(timeout=timeout)
    @app.callback(Output('output', 'figure'), [Input('dropdown', 'value'),
                                               Input('multi', 'value'),
                                               Input('arglist', 'value')])
    def update_graph_from_dropdown(dropdown, multi, arglist):

        # Get Quantmod Chart
        print('Loading')
        strategy, config, res = setup_config(dropdown)
        candles, trade_scatter = setup_chart(res)
        ch = qm.Chart(candles, src=src)

        # Get functions and arglist for technical indicators
        if arglist:
            for function in multi:
                try:
                    config = talib_dict(json.loads(arglist))
                    indicator = function.split("_")[1]
                    newargs = config[indicator]
                    # Dynamic calling
                    fn = getattr(qm, function)
                    fn(ch, **newargs)
                except Exception as e:
                    print(e)
                    getattr(qm, function)(ch)
                    pass
        else:
            for function in multi:
                # Dynamic calling
                getattr(qm, function)(ch)

        fig = ch.to_figure(width=1100)

        # hack figure
        index = 0
        for i in range(len(fig["layout"].keys())):
            axis = "yaxis"+str(i)
            if axis in fig["layout"]:
                index = i + 1
        yrange = [candles["low"].min(), candles["high"].max()]
        fig["layout"]["yaxis"]["range"] = yrange
        fig["layout"]["yaxis"+str(index)] = fig["layout"]["yaxis2"]
        fig["layout"]["plot_bgcolor"] = 'rgba(0, 0, 0, 0.00)'
        trade_scatter["yaxis"] = "y1"
        fig["data"].append(trade_scatter)

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

def get_json():
    files1 = os.path.join(gsettings["save_dir"], '*_response.json')
    files2 = os.path.join(gsettings["save_dir"], '*_config.json')
    response_files = list(filter(os.path.isfile, glob.glob(files1)))
    response_files.sort(key=lambda x: -os.path.getmtime(x))
    config_file = list(filter(os.path.isfile, glob.glob(files2)))
    config_file.sort(key=lambda x: -os.path.getmtime(x))
    return response_files, config_file

def load_json(filename):
    f = open(filename, "r")
    result = json.loads(f.read())
    f.close
    return result

def create_first_chart():
    print("log file not found: try to fetch")
    strategy = settings["Strategy"]
    deltaDays = settings['deltaDays']
    filename = gsettings['configFilename']
    configjs = Settings.get_configjs(filename)
    watch = settings["watch"]
    dateset = gekkoWrapper.getAvailableDataset(watch)
    daterange = coreFunctions.getRandomDateRange(dateset, deltaDays=deltaDays)
    config = evolution_bayes.compressing_flatten_dict(configjs[strategy], strategy)
    config["watch"] = watch
    gekko_config = gekkoWrapper.createConfig(config, daterange)
    res = evolution_bayes.EvaluateRaw(watch, daterange, configjs[strategy], strategy)
    score = res['report']['relativeProfit']

    filename = "_".join([watch["exchange"], watch["currency"], watch["asset"], strategy, datetime.datetime.now().strftime('%Y%m%d_%H%M%S'), str(score)])
    save_dir = gsettings["save_dir"]
    json_filename = os.path.join(save_dir, filename) + "_config.json"
    json2_filename = os.path.join(save_dir, filename) + "_response.json"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    f = open(json_filename, "w")
    f.write(json.dumps(gekko_config, indent=2))
    f.close()
    print("Saved: " + json_filename)
    f = open(json2_filename, "w")
    f.write(json.dumps(res, indent=2))
    f.close()
    print("Saved: " + json2_filename)

if __name__ == '__main__':
    res, config = get_json()
    if len(res) > 0 and len(config) > 0:
        run_server()
    else:
        create_first_chart()
        run_server()
