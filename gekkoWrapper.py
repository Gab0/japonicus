#!/bin/python
from subprocess import run
from subprocess import Popen, PIPE
from random import randrange, choice
from copy import deepcopy
import operator
from functools import reduce
from urllib import request, parse

import requests

gekkoURL = 'http://localhost:3000'
gekkoDIR = 'TBD'


def initializeGekko(): # not used yet.
    CMD = ['node', GekkoDir + '/gekko', '--ui']
    D = Popen(CMD, stdin=PIPE, stdout=PIPE, stderr=PIPE)

def getAvailableDataset():
    URL = gekkoURL + '/api/scansets'

    REQ = requests.post(URL)

    RESP = REQ.json()
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

def runBacktest(TradeSetting, DateRange):
    URL = 'http://localhost:3000/api/backtest'
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
                "fee":0.25,
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

    REQ = requests.post(URL, json=CONFIG)

    RESULT = REQ.json()
    rP = RESULT['report']['relativeProfit']
    return rP

'''    
def runStandaloneBacktest(TradeSetting, DateRange):
    # needs modified gekko -> to accept trade config from the command line.
    # DEPRECATED; ugly stuff.
    
    CMD = ['node', GekkoDir + '/gekko',
           '--config', 'config.js',
           '--backtest',
           '--daterange', DateRange,
           '--trade', TradeSetting]

    D = Popen(CMD, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    Result = D.communicate()[0].decode('utf-8').split('\n')
    for line in Result:
        if 'simulated profit' in line:
            print('*'+line)
            RES = float(line.split(' ')[-1][1:-2])
            print("* %.3f *" % RES)

        
    return RES
    #print(Result)
'''
'''
def getFromDict(DataDict, Indexes):
    return reduce(operator.getitem, Indexes, DataDict)
def writeToDict(DataDict, Indexes, Value):
    getFromDict(DataDict, Indexes[:-1])[Indexes[-1]] = Value
'''
