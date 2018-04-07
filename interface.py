#!/bin/python
import promoterz
import evaluation


def showDatasetSpecifications(specs):
    message = "%s/%s @%s" % (specs["asset"],
                             specs["currency"],
                             specs["exchange"])
    return message


def parseDatasetInfo(purpose, candlestickDataset):
    textdaterange = evaluation.gekko.datasetOperations.dateRangeToText(
        candlestickDataset.daterange)
    print()
    Text = "\n%s candlestick dataset %s\n" % (purpose, textdaterange)
    Text += showDatasetSpecifications(candlestickDataset.specifications) + '\n'
    return Text
