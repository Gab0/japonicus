#!/bin/python
import time
from evaluation.gekko.API import httpPost
from evaluation.gekko.dataset import epochToString
import requests
import json
import TOMLutils


from . import exchangeMonitor



def runTradingBot(botSpecifications, Strategy=None, parameterName=None, TradingBot=False):
    URL = "http://localhost:3000/api/startGekko"

    if not Strategy:
        Strategy = botSpecifications['STRATEGY']

    print("Starting bot running %s for %s/%s at %s." % (
        Strategy,
        botSpecifications['ASSET'],
        botSpecifications['CURRENCY'],
        botSpecifications['EXCHANGE']))

    traderParameters = {
        "tradingAdvisor": {
            "enabled": 'true',
            "method": Strategy,
            "candleSize": options.candleSize,
            "historySize": 40
        }
    }

    watchSettings = getWatchSettings(botSpecifications)
    traderParameters.update(getTraderBaseParameters())
    traderParameters.update(watchSettings)

    if TradingBot:
        traderParameters['type'] = "tradebot"
        traderParameters['trader'] = {'enabled': 'true'}
    else:
        traderParameters['type'] = "paper trader"
        traderParameters['paperTrader'] = {
            "feeMaker": 0.25,
            "feeTaker": 0.25,
            "feeUsing": "maker",
            "slippage": 0.05,
            "simulationBalance": {
                "asset": 0,
                "currency": 100
            },
            "reportRoundtrips": 'true',
            "enabled": 'true'
        }

    commonPath = 'strategy_parameters/%s.toml'
    if parameterName:
        parameterPath = commonPath % parameterName
    else:
        parameterPath = commonPath % Strategy

    strategySettings = TOMLutils.preprocessTOMLFile(
        parameterPath)
    strategySettings = TOMLutils.TOMLToParameters(strategySettings)
    traderParameters[Strategy] = strategySettings

    watcherSettings = getWatcherBaseParameters()
    watcherSettings.update(watchSettings)

    ExistingWatcher = checkWatcherExists(watchSettings)
    if not ExistingWatcher:
        print("Creating watcher for %s!" %
              watchSettings['watch']['exchange'])
        Watcher = httpPost(URL, watcherSettings)
        time.sleep(4)
    else:
        print("Watcher for %s-%s exists! Creating none." %
              (watchSettings['watch']['exchange'],
              watchSettings['watch']['asset']))
        Watcher = None
        traderParameters

    Trader = httpPost(URL, traderParameters)

    return Watcher, Trader


def getTraderBaseParameters():
    Request = {
        "market": {
            "type": "leech",
            "from": epochToString(time.time())
        },
        "mode": "realtime",
        "adviceWriter" : {
            "enabled": 'true',
            "muteSoft": 'false'
            },
        "adviceLogger": {
            "enabled": 'true',
            "muteSoft": 'false'
            },
        
        "candleWriter": {
            "enabled": 'false',
            "adapter": "sqlite"
        },
        "type": "paper trader",
        "performanceAnalyzer": {
            "riskFreeReturn": 2,
            "enabled": 'true'
        },
        "valid": 'true'
    }
    return Request


def getWatchSettings(coinInfo):
    W = {
        "watch": {
            "exchange": coinInfo["EXCHANGE"],
            "currency": coinInfo["CURRENCY"].upper(),
            "asset": coinInfo["ASSET"].upper()
        }
    }
    return W


def checkWatcherExists(Watch):
    Watchers = getRunningWatchers()
    Watch = Watch['watch']
    checkKeys = ['asset', 'currency', 'exchange']
    for W in Watchers:
        if 'strat' in W.keys():
            continue
        FOUND = True
        for C in checkKeys:
            if W['watch'][C] != Watch[C]:
                FOUND = False
                break

        if FOUND:
            return W['id']

    return False


def getRunningWatchers():
    try:
        W = requests.get('http://localhost:3000/api/gekkos')
    except requests.exceptions.ConnectionError:
        print("Gekko is not running.")
        return []
    W = json.loads(W.text)
    return W


def getWatcherBaseParameters():
    Request = {
        "candleWriter": {
            "enabled": "false",
            "adapter": "sqlite"
        },
        "type": "market watcher",
        "mode": "realtime"
    }
    return Request


def launchBatchTradingBots(assetCurrencyPairs, Stratlist, parameterName=None):
    for assetCurrencyPair in assetCurrencyPairs:
        for Strategy in Stratlist:
            w, t = runTradingBot(assetCurrencyPair, Strategy,
                                 parameterName=parameterName, TradingBot=True)


