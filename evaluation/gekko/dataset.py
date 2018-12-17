#!/bin/python
import random
import datetime
from .API import httpPost


def getAllScanset(GekkoURL):
    URL = GekkoURL + '/api/scansets'
    RESP = httpPost(URL)
    return RESP['datasets']


def selectCandlestickData(GekkoURL, exchange_source=None, avoidCurrency=None):
    DataSetPack = getAllScanset(GekkoURL)
    specKeys = ['exchange', 'currency', 'asset']
    scanset = []

    # IF EXCHANGE SPECIFICATIONS ARE TO BRE IGNORED;
    if 'autoselect' in exchange_source.keys():
        if exchange_source['autoselect']:
            exchange_source = None

    # SEARCH CANDIDATE DATASETS AMONG THOSE OBTAINED FROM GEKKO API;
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

    # IN CASE NO CANDLESTICK DATASET IS COMPATIBLE;
    if len(scanset) == 0:
        if exchange_source:
            raise RuntimeError(
                "scanset not available: %s\n\tscanset found: %s" %
                (exchange_source, DataSetPack)
            )

        else:
            raise RuntimeError("no scanset available! check Gekko candle database.")

    # SEARCH ON ALL FOUND SCANSETS;
    for EXCHANGE in scanset:
        ranges = EXCHANGE['ranges']
        # no ranges found?
        if not ranges:
            # print("No scansets found for %s" % EXCHANGE)
            continue
        range_spans = [x['to'] - x['from'] for x in ranges]
        LONGEST = range_spans.index(max(range_spans))
        EXCHANGE['max_span'] = range_spans[LONGEST]
        EXCHANGE['max_span_index'] = LONGEST

    # COMPILE MOST INTERESTING SCANSETS;
    availableScanset = [exchange for exchange in scanset
                        if 'max_span' in exchange.keys()]
    exchange_longest_spans = [x['max_span'] for x in availableScanset]

    # Without scansets we cannot continue.
    if not exchange_longest_spans:
        print("FATAL: No scanset available.")
        exit(1)

    best_exchange = exchange_longest_spans.index(max(exchange_longest_spans))
    best_exchange_span = availableScanset[best_exchange]['max_span_index']
    chosenScansetRange = availableScanset[best_exchange]['ranges'][best_exchange_span]

    chosenScansetSpecifications = {
        K: availableScanset[best_exchange][K]
        for K in availableScanset[best_exchange]
        if K in specKeys
    }

    return chosenScansetSpecifications, chosenScansetRange


def getCandles(globalconf, DateRange, Dataset, size=100):
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
            "dependencies": [{"module": "sqlite3", "version": "3.1.4"}],
        },
        "candleSize": size,
    }
    RESULT = httpPost(URL, CONFIG)
    return RESULT


def getDateRange(Limits, deltaDays=3):
    DateFormat = "%Y-%m-%d %H:%M:%S"
    deltams = deltaDays * 24 * 60 * 60
    DateRange = {
        "from": "%s" % epochToString(Limits['to'] - deltams),
        "to": "%s" % epochToString(Limits['to']),
    }
    return DateRange


def getRandomDateRange(Limits, deltaDays):
    FLms = Limits['from']
    TLms = Limits['to']
    deltams = deltaDays * 24 * 60 * 60
    if deltams > (TLms - FLms):
        print(
            "Fatal: deltaDays on Settings.py set to a value bigger than current dataset.\n Edit Settings file to fit your chosen candlestick data."
        )
        exit(1)
    Start = random.randint(FLms, TLms - deltams) if deltaDays else FLms
    End = (Start + deltams) if deltaDays else TLms
    DateRange = {
        "from": "%s" % epochToString(Start),
        "to": "%s" % epochToString(End)
    }
    return DateRange


def epochToString(D):
    return datetime.datetime.utcfromtimestamp(D).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
