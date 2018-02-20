#!/bin/python

import promoterz

def showDatasetSpecifications(specs):
    message = "%s/%s @%s" % (specs["asset"],
                             specs["currency"],
                             specs["exchange"])

    return message

def dateRangeToText(dateRange):
    Range = [ promoterz.evaluation.gekko.epochToString(dateRange[x])\
        for x in ['from', 'to'] ]

    Text = "%s to %s" % (Range[0], Range[1])
    return Text

def showDatasetInfo(purpose, candlestickDataset):
    textdaterange = dateRangeToText(candlestickDataset.daterange)
    print()

    print("%s candlestick dataset %s" %     (purpose,
                                             textdaterange))

    print(showDatasetSpecifications(candlestickDataset.specifications))
    print()
