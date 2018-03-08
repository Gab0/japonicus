#!/bin/python

import random
import datetime
from Settings import getSettings
from .API import httpPost

def getAllScanset():
    globalconf = getSettings('Global')
    base = random.choice(globalconf.GekkoURLs)
    URL = base + '/api/scansets'

    RESP = httpPost(URL)

    return RESP['datasets']

def selectCandlestickData(exchange_source=None, avoidCurrency=None):

    DataSetPack = getAllScanset()

    specKeys = ['exchange', 'currency', 'asset']

    scanset = []
    for s in DataSetPack:
        Valid = True
        for k in specKeys:
            if exchange_source and s[k] != exchange_source[k]:
                Valid = False

        if avoidCurrency and not exchange_source:
            if s["asset"] == avoidCurrency:
                Valid = False

        if Valid:
            scanset.append(s)

    if len(scanset) == 0:
        if exchange_source:
            raise RuntimeError("scanset not available: %s\n\tscanset found: %s" % (
                exchange_source, DataSetPack))
        else:
            raise RuntimeError("no scanset available! check Gekko candle database.")

    for EXCHANGE in scanset:
        ranges = EXCHANGE['ranges']
        range_spans = [ x['to'] - x['from'] for x in ranges ]
        LONGEST = range_spans.index(max(range_spans))
        EXCHANGE['max_span'] = range_spans[LONGEST]
        EXCHANGE['max_span_index'] = LONGEST

    exchange_longest_spans = [ x['max_span'] for x in scanset ]
    best_exchange = exchange_longest_spans.index(max(exchange_longest_spans))

    chosenScansetRange = scanset[best_exchange]['ranges'][scanset[best_exchange]['max_span_index'] ]


    chosenScansetSpecifications = { K:scanset[best_exchange][K] for K in scanset[best_exchange] if K in specKeys }

    return chosenScansetSpecifications, chosenScansetRange

def getCandles(DateRange, Dataset, size=100):
    globalconf = getSettings('Global')
    base = random.choice(globalconf.GekkoURLs)

    URL = base + "/api/getCandles"
    CONFIG = {
        "watch": Dataset.specifications,
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

    Start = random.randint(FLms,TLms-deltams) if deltaDays else FLms
    End = (Start + deltams) if deltaDays else TLms

    DateRange = {
        "from": "%s" % epochToString(Start),
        "to": "%s" % epochToString(End)
    }

    return DateRange

epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime("%Y-%m-%d %H:%M:%S")


