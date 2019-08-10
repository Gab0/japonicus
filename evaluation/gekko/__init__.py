#!/bin/python
import os
import subprocess

from .import API
from .import dataset
from .import backtest
from .import datasetOperations
from .statistics import *
import pathlib

import promoterz


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


def showBacktestResult(backtestResult, dataset=None):
    messageBackbone = ''.join([
        'Test on random candles...  ',
        'relativeProfit: %.3f \t',
        'nbTrades: %.1f\t',
        'sharpe: %.2f'
    ])

    message = messageBackbone % (
        backtestResult['relativeProfit'],
        backtestResult['trades'],
        backtestResult['sharpe']
    )

    if dataset:
        message += "\n\t\t%s\t%s" % (dataset.textDaterange(),
                                     dataset.textSpecifications())

    return message


def parseDatasetInfo(purpose, candlestickDataset):
    textdaterange = datasetOperations.dateRangeToText(
        candlestickDataset.daterange)
    print()
    Text = "\n%s candlestick dataset %s\n" % (purpose, textdaterange)
    Text += candlestickDataset.textSpecifications() + '\n'
    return Text


def showPrimaryInfo(Logger, evolutionDatasets, evaluationDatasets):
    for evolutionDataset in evolutionDatasets:
        Logger.log(
            parseDatasetInfo("evolution", evolutionDataset),
            target="Header"
        )
    if evaluationDatasets:
        for evaluationDataset in evaluationDatasets:
            Logger.log(
                parseDatasetInfo("evaluation", evaluationDataset),
                target="Header"
            )



class GekkoEvaluationPool(promoterz.evaluationPool.EvaluationPool):
    #def __init__(self, World, Urls, poolsize, individual_info):
    #    pass

    def ejectURL(self, Index):
        self.Urls.pop(Index)
        self.lasttimes.pop(Index)
        self.lasttimesperind.pop(Index)
        self.poolsizes.pop(Index)

    def distributeIndividuals(self, tosimulation):
        nb_simulate = len(tosimulation)
        sumtimes = sum(self.lasttimes)
        # stdtime = sum(self.lasttimes)/len(self.lasttimes)
        std = nb_simulate / len(self.Urls)
        # stdTPI = sum(self.lasttimesperind)/len(self.lasttimesperind)
        #print(stdTPI)
        if sumtimes:
            vels = [1 / x for x in self.lasttimes]
            constant = nb_simulate / sum(vels)
            proportions = [max(1, x * constant) for x in vels]
        else:
            proportions = [std for x in self.Urls]
        proportions = [int(round(x)) for x in proportions]
        pC = lambda x: random.randrange(0, len(x))
        pB = lambda x: x.index(min(x))
        pM = lambda x: x.index(max(x))
        while sum(proportions) < nb_simulate:
            proportions[pB(proportions)] += 1
            print('+')
        while sum(proportions) > nb_simulate:
            proportions[pM(proportions)] -= 1
            print('-')
        print(proportions)
        assert (sum(proportions) == nb_simulate)
        distribution = []
        L = 0
        for P in proportions:
            distribution.append(tosimulation[L: L + P])
            L = L + P
        return distribution


EvaluationPool = GekkoEvaluationPool


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
    # FIX THIS;
    if False and not os.path.isfile(GekkoPath):
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


