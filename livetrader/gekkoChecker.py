#!/bin/python

from . import gekkoTrigger

try:
    from . import assetAllocator
except Exception:
    pass

from dateutil import parser as dateparser
import datetime
import csv
import re
import random
from subprocess import Popen, PIPE

import pytoml
import os
import time
import json


def calculateMostIndicatedAssets(exchange):
    candlestickData = exchange.getPriceHistory()
    Assets = assetAllocator.selectMostProbableAssets(candlestickData)
    Assets = [{'EXCHANGE': exchange.name,
               'ASSET': a.split('/')[0],
               'CURRENCY': a.split('/')[1]} for a in Assets]
    return Assets


def stopGekkoBots():
    PS = ['ps', 'aux']

    runningProcs = Popen(PS,
                         stdout=PIPE, stderr=PIPE)
    runningProcs = runningProcs.stdout.read().decode('utf-8').split('\n')
    killPIDs = []

    for proc in runningProcs:
        if 'gekko/core' in proc:
            PID = re.findall("\d\d\d+", proc)[0]
            killPIDs.append(PID)

    print(killPIDs)

    for PID in killPIDs:
        N = Popen(['kill', '-9', PID], stdout=PIPE)
        N.communicate()


def interpreteRunningBotStatistics(runningBots):
    allBotStrategies = []
    runningTimes = []

    for B in runningBots.keys():
        Bot = runningBots[B]

        if Bot["config"]["type"] == 'tradebot':
            botCurrentStrategy = Bot["config"]["tradingAdvisor"]["method"]
            allBotStrategies.append(botCurrentStrategy)

        elif Bot["config"]["type"] == 'market watcher':
            fC = dateparser.parse(Bot["events"]["initial"]["candle"]["start"])
            lC = dateparser.parse(Bot["events"]["latest"]["candle"]["start"])
            delta = (lC - fC).seconds

            runningTime = delta
            runningTimes.append(runningTime)

        else:
            print("Odd runningBot found:")
            print(json.dumps(Bot, indent=2))

    return runningTimes, allBotStrategies


def getParameterSettingsPath(parameterName):
    N = os.path.join('strategy_parameters',
                     parameterName) + '.toml'
    return N


def operateStrategyScores(exchange, ranker,
                          Balances, runningTimeHours,
                          currentPortfolioStatistics, runningBotStrategies):
    print("Rebooting gekko trading bots.")

    markzeroTime = datetime.timedelta(minutes=runningTimeHours*3600)
    predictedStartTime = datetime.datetime.now() - markzeroTime
    # APPLY LAST SCORE TO STRATEGIES;
    ranker.loadStrategyRankings()

    def makeBalanceScore(entry):
        return (float(entry['BALANCE']) /
                float(entry['AVERAGE_PRICE']))

    pastCorrespondingScore = None
    for row in Balances:
        balanceDate = dateparser.parse(row['TIME'])
        timeDelta = predictedStartTime - balanceDate
        minuteDelta = abs(timeDelta.seconds) / 60
        if minuteDelta < 60:
            pastCorrespondingScore = makeBalanceScore(row)

    if pastCorrespondingScore is not None:
        currentScore =\
            makeBalanceScore(currentPortfolioStatistics)

        botRunScore = currentScore / pastCorrespondingScore * 100
        normalizedBotRunScore = botRunScore / runningTimeHours

        runningStrategy = None
        for Strategy in ranker.Strategies:
            equalStrats = True
            strategyParameters = pytoml.load(open(
                getParameterSettingsPath(Strategy.parameters)))
            print(runningBotStrategies[-1])
            comparateParameters =\
                runningBotStrategies[-1]['params']
            for param in comparateParameters.keys():
                if type(param) == dict:
                    continue
                if param not in strategyParameters.keys():
                    equalStrats = False
                    break
                if strategyParameters[param] !=\
                   comparateParameters[param]:
                    equalStrats = False
                    break
            if equalStrats:
                runningStrategy = Strategy
                break

        if runningStrategy:
            print("Runnnig strategy found at scoreboard.")
            runningStrategy.profits.append(normalizedBotRunScore)
        else:
            print("Running strategy not found at scoreboard.")

    # WRITE NEW STRATEGY SCORES;
    ranker.saveStrategyRankings()


def checkGekkoRunningBots(exchange, ranker, options):
    runningBots = gekkoTrigger.getRunningGekkos()

    BalancesFields = ['TIME', 'BALANCE', 'AVERAGE_PRICE']

    selectorSigma = exchange.conf.strategySelectorSigma
    allPairs = exchange.getAssets()
    assetCurrencyPairs = exchange.parseAssets(allPairs)

    try:
        Balances = csv.DictReader(open('balances.csv'))
    except FileNotFoundError:
        print("Balances file not found.")
        Balances = []

    Balances = [row for row in Balances]
    wBalances = csv.DictWriter(open('balances.csv', 'w'),
                               fieldnames=BalancesFields)
    wBalances.writeheader()
    for N in Balances:
        wBalances.writerow(N)

    currentPortfolioValue = exchange.getUserBalance()
    print("Net weight %.2f USD" % currentPortfolioValue)

    currentPortfolioStatistics = {
        'TIME': str(datetime.datetime.now()),
        'BALANCE': currentPortfolioValue,
        'AVERAGE_PRICE': exchange.getAveragePrices()
    }

    wBalances.writerow(currentPortfolioStatistics)

    if runningBots:
        runningTimes, runningBotStrategies =\
            interpreteRunningBotStatistics(runningBots)

        if runningTimes and runningBotStrategies:
            averageRunningTime = sum(runningTimes) / len(runningTimes)
            runningTimeHours = averageRunningTime / 3600

            targetMinimumRunningHours =\
                exchange.conf.strategyRunTimePeriodHours

            # if target running time is reached;
            if runningTimeHours > targetMinimumRunningHours:
                operateStrategyScores(exchange, ranker,
                                      Balances, runningTimeHours,
                                      currentPortfolioStatistics,
                                      runningBotStrategies)

                Strategy = ranker.selectStrategyToRun(selectorSigma)

                stopGekkoBots()
                time.sleep(60)

                selectedAssetCurrencyPairs = calculateMostIndicatedAssets(exchange)
                gekkoTrigger.launchBatchTradingBots(
                    selectedAssetCurrencyPairs,
                    [Strategy.strategy],
                    options
                )

            else:
                print("Target runtime not reached.")
    else:
        ranker.loadStrategyRankings()
        print("Launching bots on idle gekko instance.")
        Strategy = ranker.selectStrategyToRun(selectorSigma)
        selectedAssetCurrencyPairs = calculateMostIndicatedAssets(exchange)
        print(assetCurrencyPairs)
        print(selectedAssetCurrencyPairs)
        gekkoTrigger.launchBatchTradingBots(
            selectedAssetCurrencyPairs,
            [Strategy.strategy],
            options
        )
