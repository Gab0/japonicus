#!/bin/python

import dash_core_components as dcc
import dash_html_components as html
import datetime


allStyle = {
            'width': '1100',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'font-family': 'overpass',
            'background-color': '#F3F3F3'
        }


def getLayout(app):
    layout = html.Div([
        dcc.Location(id='url', refresh=False),
        getHeader(app),
        html.Div(id='page-content')
    ])
    return layout


def getHeader(app):
    # this is a mess;
    inlineBlock = {"display": "inline-block"}
    headerWidgets = [
        html.Button("Refresh", id='refresh-button'),
        html.Div(
            [
                html.Div("Last refresh @ ", style=inlineBlock.update({"float": "left"})),
                html.Div(datetime.datetime.now(),
                         id='last-refresh', className="showTime",
                         style=inlineBlock.update({"float": "left"})),

                html.Div("%s Start time" % app.startTime,
                         id='start-time', className="showTime",
                         style=inlineBlock.update({"float": "right"})),
                html.Br(),
                html.Center([
                    html.Div(app.epochInfo, id="current-epoch")
                    ])
            ], className="showTime")
    ]

    pageMenu = [
        html.A(html.Button("Evolution Statistics"), href="/"),
        html.A(html.Button("Evaluation Breaks"), href="/evalbreak"),
        # html.Button("View Settings", className="unimplemented"),
        # html.Button("Inspect Population", className="unimplemented")
    ]



    # html.Link(rel='stylesheet', href='/static/promoterz_style.css'),
    header = html.Div(
        [
            html.H2(
                app.webpageTitle,
                style={'padding-top': '20', 'text-align': 'center'},
            ),
            html.Div(headerWidgets),
            html.Div(pageMenu),
        ],
        style=allStyle)

    return header


def getCommon(app):
    return html.Div([
        html.Div(children=app.WorldGraph, id='WorldGraphContainer'),
        html.Div(children=app.LocaleGraphs, id='LocaleGraphsContainer')
    ], style=allStyle)


def getEvalbreak(app):
    return html.Div([
        html.Div(children=app.EvalBreakGraph, id='EvalBreakContainer')
    ], style=allStyle)
