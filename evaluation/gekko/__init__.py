#!/bin/python
import os
import subprocess

from .import API
from .import dataset
from .import backtest
from .statistics import *
import pathlib


class GekkoEvaluator():
    def __init__(self):
        pass


SettingsFiles = [
    "generation",
    "Global",
    "dataset",
    #"indicator",
    "backtest",
    "evalbreak"
]


def ResultToIndividue(result, individue):
    individue.fitness.values = (result['relativeProfit'], result['sharpe'])
    individue.trades = result['trades']
    individue.averageExposure = result['averageExposure'] / 3600000


def showIndividue(evaldata):
    return "~ bP: %.3f\tS: %.3f\tnbT:%.3f" % (
        evaldata['relativeProfit'], evaldata['sharpe'], evaldata['trades']
    )


def validateSettings(settings):
    # LOCATE & VALIDATE RUNNING GEKKO INSTANCES FROM CONFIG URLs;
    possibleInstances = settings['Global']['GekkoURLs']
    validatedInstances = []
    for instance in possibleInstances:
        Response = API.checkInstance(instance)
        if Response:
            validatedInstances.append(instance)
            print("found gekko @ %s" % instance)
        else:
            print("unable to locate %s" % instance)

    if validatedInstances:
        settings['Global']['GekkoURLs'] = validatedInstances

    else:
        print("Aborted: No running gekko instances found.")
        return False

    GekkoPath = settings['Global']['gekkoPath'] + '/gekko.js'
    GekkoPath = GekkoPath.replace("$HOME", str(pathlib.Path.home()))
    if not os.path.isfile(GekkoPath):
        print(
            "Aborted: gekko.js not found" + 
            "on path specified @Settings.py;\n%s" % GekkoPath)
        return False

    return True


# DEPRECATED;
def launchGekkoChildProcess(settings):
    gekko_args = [
        'node',
        '--max-old-space-size=8192',
        settings['global']['gekkoPath'] + '/web/server.js',
    ]
    gekko_server = subprocess.Popen(gekko_args,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
    return gekko_server


