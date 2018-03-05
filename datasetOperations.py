#!/bin/python

import evaluation

class CandlestickDataset():
    def __init__(self, specifications, daterange):
        self.daterange = daterange
        self.specifications = specifications

    def restrain(self, deltaDays):
        if not deltaDays:
            return
        deltams = deltaDays * 24 * 60 * 60

        restainedInit = self.daterange['to'] - deltams

        self.daterange['from'] = max( self.daterange['from'],
                                     restrainedInit )

def getLocaleDateRange(World, locale):
    getDateRange = lambda: evaluation.gekko.dataset.getRandomDateRange(
        World.EnvironmentParameters[0].daterange,
    World.genconf.deltaDays )

    DateRange = [ getDateRange()\
                       for x in range(World.genconf.ParallelCandlestickDataset) ]

    return DateRange
