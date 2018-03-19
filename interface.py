#!/bin/python
import promoterz
import evaluation


def showDatasetSpecifications(specs):
    message = "%s/%s @%s" % (specs["asset"], specs["currency"], specs["exchange"])
    return message


def dateRangeToText(dateRange):
    convertDateRange = lambda x: evaluation.gekko.dataset.epochToString(x) \
                       if type(x) == int else x
    Range = [
        convertDateRange(dateRange[x]) for x in ['from', 'to' ]
    ]
    Text = "%s to %s" % (Range[0], Range[1])
    return Text


def parseDatasetInfo(purpose, candlestickDataset):
    textdaterange = dateRangeToText(candlestickDataset.daterange)
    print()
    Text = "\n%s candlestick dataset %s\n" % (purpose, textdaterange)
    Text += showDatasetSpecifications(candlestickDataset.specifications) + '\n'
    return Text
