#!/bin/python

import dash_core_components as dcc
import dash_html_components as html
import datetime


def getLayout(webpageTitle):
    headerWidgets = [
        html.Button("Refresh", id='refresh'),
        html.Div(
            [
                html.Div(datetime.datetime.now(),
                         id='display-time', className="showTime"),
                html.Div("Running since %s" % datetime.datetime.now(),
                         id='running-since', className="showTime")
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
            html.Link(rel='stylesheet', href='/static/promoterz_style.css'),
            html.Div(
                [
                    html.H2(
                        webpageTitle,
                        style={'padding-top': '20', 'text-align': 'center'},
                    ),
                    html.Div(headerWidgets),
                    html.Div(pageMenu),
                    html.Div(id='WorldGraph'),
                    html.Div(id='LocaleGraphs'),
        ])],
        style={
            'width': '1100',
            'margin-left': 'auto',
            'margin-right': 'auto',
            'font-family': 'overpass',
            'background-color': '#F3F3F3'
        },
    )

    return layout
