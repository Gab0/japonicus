#!/bin/python

import dash_core_components as dcc

from evaluation.gekko.statistics import epochStatisticsNames, periodicStatisticsNames


def updateWorldGraph(app, WORLD):
    environmentData = [
        {
        }
    ]
    populationGroupData = [
        {
            'x': [locale.position[0]],
            'y': [locale.position[1]],
            'type': 'scatter',
            'name': locale.name,
            'showscale': False,
            'mode': 'markers',
            'marker': {
                'symbol': 'square'
            }

        } for locale in WORLD.locales
    ]

    fig = {
        'data': populationGroupData,
        'layout': {
            'title': "World Topology"
        }
    }


    G = dcc.Graph(id="WorldGraph", figure=fig)
    #app.layout.get("WorldGraphContainer").children = [G]
    app.WorldGraph = G
    return G


def updateLocaleGraph(app, LOCALE):

    GraphName = LOCALE.name
    print('Loading %s' % GraphName)
    Statistics = LOCALE.EvolutionStatistics
    ID = [s for s in GraphName if s.isdigit()]
    annotations = []


    oldLocaleGraph = None
    for lidx, localeGraph in enumerate(app.LocaleGraphs):
        if localeGraph.id == LOCALE.name:
            oldLocaleGraph = lidx
            break

    statisticsNames = {}
    statisticsNames.update(epochStatisticsNames)
    statisticsNames.update(periodicStatisticsNames)

    annotationFontDescription = {
        'family': 'Arial',
        'size': 12,
        'color': 'rgb(37,37,37)'
    }

    """
    for Statistic in Statistics:
        if 'dateRange' in Statistic.keys():
            if Statistic['dateRange']:
                for R, dateRange in enumerate(Statistic['dateRange']):
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
    """

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
        'max', 'evaluationScore',
        'evaluationScoreOnSecondary'
    ]

    DATA = [
            {
                'x': [Statistic['id'] for Statistic in Statistics],
                'y': [Statistic[statNames[S]] for Statistic in Statistics],
                'type': 'line',
                'name': statisticsNames[statNames[S]],
                'line': {'color': 'rgb%s' % str(colorSequence[S])},
            }
            for S in range(len(statNames))
        ]

    fig = {
        'data': DATA,
        'layout': {
            'title': 'Evolution at %s' % GraphName,
            'annotations': annotations
        },
    }

    G = dcc.Graph(figure=fig, id=LOCALE.name)
    if oldLocaleGraph is not None:
        app.LocaleGraphs[oldLocaleGraph] = G
    else:
        app.LocaleGraphs.append(G)

    return G

