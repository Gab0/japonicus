#!/bin/python

import dash_core_components as dcc

from evaluation.gekko.statistics import epochStatisticsNames, periodicStatisticsNames


def updateWorldGraph(localeList):
    environmentData = [
        {
        }
    ]
    populationGroupData = [
        {
            'x': [locale.position[0]],
            'y': [locale.position[1]],
            'type': 'scatter',
            'name': locale.name

        } for locale in localeList
    ]

    fig = {
        'data': populationGroupData,
        'layout': {
            'title': "World Topology"
        }
    }

    fig = {
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }

    return fig


def updateLocaleStatsGraph(GraphName, Statistics):
    print('Loading')
    ID = [s for s in GraphName if s.isdigit()]

    annotations = []

    statisticsNames = {}
    statisticsNames.update(epochStatisticsNames)
    statisticsNames.update(periodicStatisticsNames)

    annotationFontDescription = {
        'family': 'Arial',
        'size': 12,
        'color': 'rgb(37,37,37)'
    }
    if 'dateRange' in Statistics.keys():
        if Statistics['dateRange']:
            for R, dateRange in enumerate(Statistics['dateRange']):
                if dateRange is not None:
                    annotations.append(
                        {
                            'xref': 'axis',
                            'yref': 'paper',
                            'xanchor': 'left',
                            'yanchor': 'bottom',
                            'font': annotationFontDescription,
                            'x': R,
                            'y': 1 if not len(annotations) %
                            2 else 0.93,  # avoid label overlap;
                            'text': dateRange,
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
        'avg', 'std', 'min',
        'max', 'evaluationScore', 'evaluationScoreOnSecondary'
    ]
    DATA = [
        {
            'x': Statistics['id'],
            'y': Statistics[statNames[S]],
            'type': 'line',
            'name': statisticsNames[statNames[S]],
            'line': {'color': 'rgb%s' % str(colorSequence[S])},
        }
        for S in range(len(statNames))
    ]
    fig = {
        'data': [
            {
                'x': [0, Statistics["id"]],
                'y': [0],
                'type': 'line',
                'name': 'markzero',
                'line': {'color': 'rgb(0,0,0)'},
            }
        ] +
        DATA,
        'layout': {
            'title': 'Evolution at %s' % GraphName,
            'annotations': annotations
        },
    }



    fig = {
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }

    return fig


def newGraphic(name):
    G = dcc.Graph(id=name)
    G.Active = True
    return G


