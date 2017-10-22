#!/bin/python

from subprocess import run
from subprocess import Popen, PIPE
import random
from copy import deepcopy
import operator
from functools import reduce
from urllib import request, parse
import json
import requests
import datetime

gekkoURLs = ['http://localhost:3000']
gekkoDIR = 'TBD'

def getURL(path):
    return random.choice(gekkoURLs)+path

def initializeGekko(): # not used yet.
    CMD = ['node', gekkoDIR + '/gekko', '--ui']
    D = Popen(CMD, stdin=PIPE, stdout=PIPE, stderr=PIPE)

def httpPost(URL, data={}):
    Request = requests.post(URL, json=data)
    try:
        Response = json.loads(Request.text)
    except Exception as e:
        print("Error: config failure")
        print(URL)
        print(data)
        raise e

    return Response
    
def getAllScanset():
    URL = getURL('/api/scansets')

    RESP = httpPost(URL)

    return RESP['datasets']

def getAvailableDataset(exchange_source=None):

    DataSetPack = getAllScanset()

    scanset = []
    for s in DataSetPack:
        for k in "exchange currency asset".split(" "):
            if exchange_source and s[k] != exchange_source[k]:
                continue
            scanset.append(s)

    if len(scanset) == 0:
        raise "scanset not available: {}".format(watch)

    for EXCHANGE in scanset:
        ranges = EXCHANGE['ranges']
        range_spans = [x['to']-x['from'] for x in ranges]
        LONGEST = range_spans.index(max(range_spans))
        EXCHANGE['max_span'] = range_spans[LONGEST]
        EXCHANGE['max_span_index'] = LONGEST

    exchange_longest_spans = [x['max_span'] for x in scanset]
    best_exchange = exchange_longest_spans.index(max(exchange_longest_spans))

    LongestDataset = scanset[best_exchange]['ranges'][scanset[best_exchange]['max_span_index']]

    return LongestDataset

def loadHostsFile():
    pass


def runBacktest(TradeSetting, DateRange, candleSize=10, gekko_config=None):
    gekko_config = createConfig(TradeSetting, DateRange, candleSize, gekko_config)
    url = getURL('/api/backtest')
    result = httpPost(url, gekko_config)
    # sometime report is False(not dict)
    if type(result['report']) is bool:
        print("Warning: report not found, probable Gekko fail!")
        print(DateRange)
        #print(TradeSetting)
        #print(result)
        #print(URL)
        #print(CONFIG)

        # So rare that has no impact;
        return 0, 0

    rProfit = result['report']['relativeProfit']
    nbTransactions = result['report']['trades']
    return rProfit, nbTransactions

def firePaperTrader(TradeSetting, Exchange, Currency, Asset):
    
    TradeMethod = list(TradeSetting.keys())[0]
    true = True
    false= False

    URL = random.choice(gekkoURLs)+'/api/startGekko'
    CONFIG = {
        "market":{
            "type":"leech",
            "from":"2017-09-13T15:42:00Z" # TIME ATM;
        },
        "mode":"realtime",
        "watch":{
            "exchange": Exchange,
            "currency": Currency,
            "asset": Asset
        },
        "tradingAdvisor":{
            "enabled":true,
            "method":TradeMethod,
            "candleSize":60,
            "historySize":10},
        TradeMethod: TradeSetting[TradeMethod],
        "paperTrader":{
            "fee":0.25,
            "slippage":0.05,
            "simulationBalance":{
                "asset":1,
                "currency":100
            },
            "reportRoundtrips":true,
            "enabled":true
        },
        "candleWriter":{
            "enabled":true,
            "adapter":"sqlite"
        },
        "type":
        "paper trader",
        "performanceAnalyzer":{
            "riskFreeReturn":2,
            "enabled":true},
        "valid":true
    }
    
    RESULT = httpPost(URL,CONFIG)
    print(RESULT)
    
def createConfig(TradeSetting, DateRange, candleSize=10, gekko_config=None):
    if "watch" in TradeSetting:
        watch = TradeSetting["watch"]
        del TradeSetting["watch"]
    else:
        watch = {
                "exchange": "poloniex",
                "currency": "USDT",
                "asset": "BTC"
        }
    TradeMethod = list(TradeSetting.keys())[0]
    true = True
    false= False

    CONFIG = {
        "gekkoConfig": {
            "debug":false,
            "info":false,
            "watch": watch,
            "paperTrader": {
                "fee": 0.25, # declare deprecated 'fee' so keeps working w/ old gekko;
                "feeMaker": 0.15,
                "feeTaker": 0.25,
                "feeUsing": 'maker',
                "slippage":0.05,
                "simulationBalance": {
                    "asset":1,
                    "currency":100
                },
                "reportRoundtrips":true,
                "enabled":true
            },
            "tradingAdvisor": {
                "enabled":true,
                "method": TradeMethod,
                "candleSize": candleSize, # candleSize: smaller = heavier computation + better possible results;
                "historySize":10
            },
            TradeMethod: TradeSetting[TradeMethod],
             "backtest": {
                 "daterange": DateRange
             },
             "performanceAnalyzer": {
                 "riskFreeReturn":2,
                 "enabled":true
             },
            "valid":true
        },
            "data": {
                "candleProps": ["id", "start", "open", "high", "low", "close", "vwp", "volume", "trades"],
                "indicatorResults":true,
                "report":true,
                "roundtrips":false,
                "trades":true
            }
    }
    if gekko_config == None:
        gekko_config = CONFIG
    return gekko_config


def getCandles(DateRange, size=100):
    URL = "http://localhost:3000/api/getCandles"
    CONFIG = {
        "watch": {
            "exchange": "poloniex",
            "currency": "BTC",
            "asset": "ETH"
            },
        "daterange": DateRange,
        "adapter": "sqlite",
        "sqlite": {
            "path": "plugins/sqlite",

            "dataDirectory": "history",
            "version": 0.1,

            "dependencies": [{
                "module": "sqlite3",
                "version": "3.1.4"
                }]
            },
        "candleSize": size
    }

    RESULT = httpPost(URL, CONFIG)
    return RESULT


def Evaluate(constructPhenotype, candleSize, DateRange, Individual):
    # IndividualToSettings(IND, STRAT) is a function that depends on GA algorithm,
    # so should be provided;
    Settings = constructPhenotype(Individual)
    #print(Settings)


    Profit, nbTransaction = runBacktest(Settings, DateRange, candleSize=candleSize)
    return Profit,

def getDateRange(Limits, deltaDays=3):
    DateFormat="%Y-%m-%d %H:%M:%S"

    epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime(DateFormat)
    deltams=deltaDays * 24 * 60 * 60

    DateRange = {
        "from": "%s" % epochToString(Limits['to']-deltams),
        "to": "%s" % epochToString(Limits['to'])
    }
    return DateRange

def getRandomDateRange(Limits, deltaDays, testDays=0):

    FLms = Limits['from']
    TLms = Limits['to']
    deltams=deltaDays * 24 * 60 * 60
    testms=testDays * 24 * 60 * 60

    Starting= random.randint(FLms,TLms-deltams-testms)
    DateRange = {
        "from": "%s" % epochToString(Starting),
        "to": "%s" % epochToString(Starting+deltams)
    }

    return DateRange

epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime("%Y-%m-%d %H:%M:%S")

def globalEvaluationDataset(DatasetLimits, deltaDays, NB):
    Dataset = []
    for W in range(NB):
        DateRange = getRandomDateRange(DatasetLimits, deltaDays)
        Dataset.append(DateRange)

    return Dataset


