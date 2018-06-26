#!/bin/python
from . import gekkoTrigger
from . import exchangeMonitor

from dateutil import parser as dateparser
import datetime
import csv
import re
import random
from subprocess import Popen, PIPE
import pytoml
import os
import time


def stopGekko():
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
    for Bot in runningBots:
        print(Bot)
        if 'trader' in Bot.keys() and Bot["trader"] == "tradebot":
            botCurrentStrategy = Bot["strat"]
            allBotStrategies.append(botCurrentStrategy)

        if "firstCandle" in Bot.keys():
            fC = dateparser.parse(Bot["firstCandle"]["start"])
            lC = dateparser.parse(Bot["lastCandle"]["start"])

            delta = (lC - fC).seconds
            print(delta)
            runningTime = delta
            runningTimes.append(runningTime)

    return runningTimes, allBotStrategies


def getParameterSettingsPath(parameterName):
    N = os.path.join('strategy_parameters',
                     parameterName) + '.toml'
    return N


def checkGekkoRunningBots(exchange, ranker):
    runningBots = gekkoTrigger.getRunningWatchers()

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

    currentPortfolioValue = exchangeMonitor.getUserBalance()
    print(currentPortfolioValue)

    currentPortfolioStatistics = {
        'TIME': str(datetime.datetime.now()),
        'BALANCE': currentPortfolioValue,
        'AVERAGE_PRICE': exchangeMonitor.getAveragePrices()
    }

    wBalances.writerow(currentPortfolioStatistics)

    if runningBots:
        runningTimes, runningBotStrategies = interpreteRunningBotStatistics(runningBots)

        if runningTimes and runningBotStrategies:
            averageRunningTime = sum(runningTimes) / len(runningTimes)
            runningTimeHours = averageRunningTime / 3600
            markzeroTime = datetime.timedelta(minutes=averageRunningTime)
            predictedStartTime = datetime.datetime.now() - markzeroTime
            targetMinimumRunningHours = exchange.conf.strategyRunTimePeriodHours

            # if
            if runningTimeHours > targetMinimumRunningHours:
                print("Rebooting gekko trading bots.")

                # APPLY LAST SCORE TO STRATEGIES;
                Strategies = exchangeMonitor.loadStrategyRankings()

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
                    currentScore = makeBalanceScore(currentPortfolioStatistics)

                    botRunScore = currentScore / pastCorrespondingScore * 100
                    normalizedBotRunScore = botRunScore / runningTimeHours

                    runningStrategy = None
                    for Strat in Strategies:
                        equalStrats = True
                        strategyParameters = pytoml.load(open(
                            getParameterSettingsPath(Strat.parameters)))
                        print(runningBotStrategies[-1])
                        comparateParameters = runningBotStrategies[-1]['params']
                        for param in comparateParameters.keys():
                            if type(param) == dict:
                                continue
                            if param not in strategyParameters.keys():
                                equalStrats = False
                                break
                            if strategyParameters[param] != comparateParameters[param]:
                                equalStrats = False
                                break
                        if equalStrats:
                            runningStrategy = Strat
                            break
                    if runningStrategy:
                        print("Runnnig strategy found at scoreboard.")
                        runningStrategy.profits.append(normalizedBotRunScore)
                    else:
                        print("Running strategy not found at scoreboard.")

                Strategy = ranker.selectStrategyToRun(selectorSigma)

                stopGekko()
                time.sleep(60)
                gekkoTrigger.launchBatchTradingBots(
                    assetCurrencyPairs,
                    [Strategy.strategy],
                    parameterName=Strategy.parameters
                )

                # WRITE NEW STRATEGY SCORES;
                exchangeMonitor.saveStrategyRankings(Strategies)
            else:
                print("Target runtime not reached.")
    else:
        Strategies = exchangeMonitor.loadStrategyRankings()
        print("Launching bots on idle gekko instance.")
        assetCurrencyPairs, Strategy = ranker.selectStrategyToRun(selectorSigma)
        gekkoTrigger.launchBatchTradingBots(
            assetCurrencyPairs,
            [Strategy.strategy],
            parameterName=Strategy.parameters
        )
