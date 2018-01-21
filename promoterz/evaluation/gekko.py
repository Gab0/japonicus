#!/bin/python

#from subprocess import run
from subprocess import Popen, PIPE
import random
from copy import deepcopy
import operator
from functools import reduce
from urllib import request, parse
import json
import requests
import datetime
import os

from Settings import getSettings

gekkoDIR = 'TBD'

def getURL(path):
    pass
#return random.choice(gekkoURLs)+path
epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime(DateFormat)

def initializeGekko(): # not used yet.
    CMD = ['node', gekkoDIR + '/gekko', '--ui']
    D = Popen(CMD, stdin=PIPE, stdout=PIPE, stderr=PIPE)

def httpPost(URL, data={}):
    try:

        Request = requests.post(URL, json=data)
        Response = json.loads(Request.text)

    except ConnectionRefusedError:
        print("Error: Gekko comm error! Check your local Gekko instance.")
        exit()
    except Exception as e:
        print("Error: config failure")
        print(URL)
        print(data)
        raise e

    return Response
    
def getAllScanset():
    globalconf = getSettings('Global')
    base = random.choice(globalconf.GekkoURLs)
    URL = base + '/api/scansets'

    RESP = httpPost(URL)

    return RESP['datasets']

def getAvailableDataset(exchange_source=None):

    DataSetPack = getAllScanset()

    scanset = []
    for s in DataSetPack:
        Valid = True
        for k in "exchange currency asset".split(" "):
            if exchange_source and s[k] != exchange_source[k]:
                Valid = False
                continue
        if Valid:
            scanset.append(s)

    if len(scanset) == 0:
        if exchange_source:
            raise RuntimeError("scanset not available: %s\n\tscanset found: %s" % (exchange_source, DataSetPack))
        else:
            raise RuntimeError("no scanset available! check Gekko candle database.")

    for EXCHANGE in scanset:
        ranges = EXCHANGE['ranges']
        range_spans = [x['to']-x['from'] for x in ranges]
        LONGEST = range_spans.index(max(range_spans))
        EXCHANGE['max_span'] = range_spans[LONGEST]
        EXCHANGE['max_span_index'] = LONGEST

    exchange_longest_spans = [ x['max_span'] for x in scanset ]
    best_exchange = exchange_longest_spans.index(max(exchange_longest_spans))

    chosenScansetRange = scanset[ best_exchange]['ranges'][scanset[best_exchange]['max_span_index'] ]
        
    specKeys = ['exchange', 'currency', 'asset']
    
    chosenScansetSpecifications = {K:scanset[best_exchange][K] for K in scanset[best_exchange] if K in specKeys}

    
    return chosenScansetSpecifications, chosenScansetRange

def loadHostsFile(HostsFilePath):
    remoteGekkos=[]
    if os.path.isfile(HostsFilePath):
        H = open(HostsFilePath).read().split('\n')
        for W in H:
            if W and not '=' in W and not '[' in W:
                remoteGekkos.append("http://%s:3000" % W)

    return remoteGekkos

def runBacktest(GekkoInstanceUrl, TradeSetting, Database, DateRange, candleSize=10, gekko_config=None):
    gekko_config = createConfig(TradeSetting, Database, DateRange, candleSize, gekko_config)
    url = GekkoInstanceUrl+'/api/backtest'
    result = httpPost(url, gekko_config)
    # sometime report is False(not dict)
    if type(result['report']) is bool:
        print("Warning: report not found, probable Gekko fail!")
        print(DateRange)

        # That fail is so rare that has no impact.. still happens randomly;
        return {'relativeProfit':0, 'market':0, 'trades':0, 'sharpe':0} # fake backtest report


    #rProfit = result['report']['relativeProfit']
    #nbTransactions = result['report']['trades']
    #market = result['report']['market']
    return result['report']

def firePaperTrader(GekkoInstanceUrl, TradeSetting, Exchange, Currency, Asset):
    
    TradeMethod = list(TradeSetting.keys())[0]
    true = True
    false= False


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
    
def createConfig(TradeSetting, Database, DateRange, candleSize=10, gekko_config=None):

    TradeMethod = list(TradeSetting.keys())[0]
    true = True
    false= False

    CONFIG = {
        "gekkoConfig": {
            "debug":false,
            "info":false,
            "watch": Database,
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
    globalconf = getSettings('Global')
    base = random.choice(globalconf.GekkoURLs)

    URL = base + "/api/getCandles"
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


def Evaluate(candleSize, Database, DateRange, phenotype, GekkoInstanceUrl):
    # IndividualToSettings(IND, STRAT) is a function that depends on GA algorithm,
    # so should be provided;

    result = [ runBacktest(GekkoInstanceUrl,
                           phenotype, Database,
                           DR,
                           candleSize=candleSize) for DR in DateRange ]

    RelativeProfits = [ R['relativeProfit']-R['market'] for R in result]
    avgTrades = sum( [R['trades'] for R in result] ) / len(DateRange)
    mRelativeProfit = sum(RelativeProfits)/len(RelativeProfits)

    avgSharpe = sum ( [R['sharpe'] for R in result if R['sharpe']]) / len(DateRange)


    return (mRelativeProfit, avgSharpe), avgTrades

def getDateRange(Limits, deltaDays=3):
    DateFormat="%Y-%m-%d %H:%M:%S"


    deltams=deltaDays * 24 * 60 * 60

    DateRange = {
        "from": "%s" % epochToString(Limits['to']-deltams),
        "to": "%s" % epochToString(Limits['to'])
    }
    return DateRange

def getRandomDateRange(Limits, deltaDays):

    FLms = Limits['from']
    TLms = Limits['to']
    deltams=deltaDays * 24 * 60 * 60

    if deltams > (TLms - FLms):
        print("Fatal: deltaDays on Settings.py set to a value bigger than current dataset.\n Edit Settings file to fit your chosen candlestick data.")
        exit()
        
    Starting= random.randint(FLms,TLms-deltams)
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


