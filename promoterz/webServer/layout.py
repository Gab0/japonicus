#!/bin/python

import dash_core_components as dcc
import dash_html_components as html
import datetime


def getLayout(app):
    inlineBlock = {"display": "inline-block"}
    headerWidgets = [
        html.Button("Refresh", id='refresh-button'),
        html.Div(
            [
                html.Div("Last refresh @ ", style=inlineBlock.update({"float": "left"})),
                html.Div(datetime.datetime.now(),
                         id='last-refresh', className="showTime",
                         style=inlineBlock.update({"float": "left"})),

                html.Div("%s Start time" % datetime.datetime.now(),
                         id='start-time', className="showTime",
                         style=inlineBlock.update({"float": "right"})),
                html.Br(),
                html.Center([
                    html.Div(app.epochInfo, id="current-epoch")
                    ])
            ], className="showTime")
    ]

    pageMenu = [
        html.Button("Evolution Statistics"),
        # html.Button("Evaluation Breaks", className="unimplemented"),
        # html.Button("View Settings", className="unimplemented"),
        # html.Button("Inspect Population", className="unimplemented")
    ]

    layout = html.Div(
        [
            # html.Link(rel='stylesheet', href='/static/promoterz_style.css'),
            html.Div(
                [
                    html.H2(
                        app.webpageTitle,
                        style={'padding-top': '20', 'text-align': 'center'},
                    ),
                    html.Div(headerWidgets),
                    html.Div(pageMenu),
                ]
            ),
            html.Div(children=app.WorldGraph, id='WorldGraphContainer'),
            html.Div(children=app.LocaleGraphs, id='LocaleGraphsContainer'),
        ],
        style={
            'width': '1100',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'font-family': 'overpass',
            'background-color': '#F3F3F3'
        },
    )

    return layout
