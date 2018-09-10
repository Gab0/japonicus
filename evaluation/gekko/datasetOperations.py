#!/bin/python
import evaluation
import random


class CandlestickDataset():
    def __init__(self, specifications, daterange):
        self.daterange = daterange
        self.specifications = specifications

    def restrain(self, deltaDays):
        if not deltaDays:
            return

        deltams = deltaDays * 24 * 60 * 60
        restrainedInit = self.daterange['to'] - deltams
        self.daterange['from'] = max(self.daterange['from'], restrainedInit)

    def textDaterange(self):
        return dateRangeToText(self.daterange)

    def textSpecifications(self):
        message = "%s/%s @%s" % (self.specifications["asset"],
                                 self.specifications["currency"],
                                 self.specifications["exchange"])

        return message


def getRandomSectorOfDataset(sourceDataset, deltaDays):

    G = evaluation.gekko.dataset.getRandomDateRange
    dateRange = G(sourceDataset.daterange, deltaDays)
    newDataset = CandlestickDataset(sourceDataset.specifications,
                                    dateRange)

    return newDataset


def getLocaleDataset(World, locale, Type='evolution'):

    localeDataset = []
    for DS in range(World.backtestconf.ParallelCandlestickDataset):
        sourceDataset = random.choice(World.EnvironmentParameters['evolution'])

        newDataset = getRandomSectorOfDataset(sourceDataset,
                                              World.backtestconf.deltaDays)
        localeDataset.append(newDataset)

    return localeDataset


def dateRangeToText(dateRange):
    def convertDateRange(x):
        if type(x) == int:
            return evaluation.gekko.dataset.epochToString(x) 
        else:
            return x

    Range = [
        convertDateRange(dateRange[x]) for x in ['from', 'to']
    ]
    Text = "%s to %s" % (Range[0], Range[1])
    return Text
