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

gekkoURLs = ['http://localhost:3000']
gekkoDIR = 'TBD'

def initializeGekko(): # not used yet.
    CMD = ['node', gekkoDIR + '/gekko', '--ui']
    D = Popen(CMD, stdin=PIPE, stdout=PIPE, stderr=PIPE)

def httpPost(URL, data={}):
    Request = requests.post(URL, json=data)
    Response = json.loads(Request.text)

    return Response
    
def getAvailableDataset():
    URL = gekkoURLs[0] + '/api/scansets'

    RESP = httpPost(URL)

    DS = RESP['datasets']
    
    for EXCHANGE in DS:
        ranges = EXCHANGE['ranges']
        range_spans = [x['to']-x['from'] for x in ranges]
        LONGEST = range_spans.index(max(range_spans))
        EXCHANGE['max_span'] = range_spans[LONGEST]
        EXCHANGE['max_span_index'] = LONGEST

    exchange_longest_spans = [x['max_span'] for x in DS]
    best_exchange = exchange_longest_spans.index(max(exchange_longest_spans))

    LongestDataset = DS[best_exchange]['ranges'][DS[best_exchange]['max_span_index']]

    return LongestDataset

def loadHostsFile():
    pass

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
    
def runBacktest(TradeSetting, DateRange):
    URL = random.choice(gekkoURLs)+'/api/backtest'
    TradeMethod = list(TradeSetting.keys())[0]
    true = True
    false= False
    CONFIG = {
        "gekkoConfig": {
            "watch": {
                "exchange": "poloniex",
                "currency": "USDT",
                "asset": "BTC"
            },
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
                "candleSize":60,
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
                "candleProps": ["close", "start"],
                "indicatorResults":true,
                "report":true,
                "roundtrips":false,
                "trades":false
            }
    }

    RESULT = httpPost(URL, CONFIG)
    # sometime report is False(not dict)
    if type(RESULT['report']) is bool:
        print("Warning: report not found")
        print(DateRange)
        #print(TradeSetting)
        #print(RESULT)
        #print(URL)
        #print(CONFIG)
        return 0.
    rP = RESULT['report']['relativeProfit']
    return rP

def getCandles(DateRange, size=100):
    URL = 'http://localhost:3000/api/getCandles'
    CONFIG = {
        "watch": {
            "exchange": 'poloniex',
            "currency": 'USDT',
            "asset": 'BTC'
            },
        "daterange": DateRange,
        "adapter": 'sqlite',
        "sqlite": {
            "path": 'plugins/sqlite',

            "dataDirectory": 'history',
            "version": 0.1,

            "dependencies": [{
                "module": 'sqlite3',
                "version": '3.1.4'
                }]
            },
        "candleSize": size
    }

    RESULT = httpPost(URL, CONFIG)
    return RESULT


