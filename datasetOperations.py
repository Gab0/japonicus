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


def getLocaleDateRange(World, locale):
    def getDateRange(dataset):
        return evaluation.gekko.dataset.getRandomDateRange(
            dataset.daterange, World.genconf.deltaDays
        )
    Dataset = []

    for D in range(World.genconf.ParallelCandlestickDataset):
        BaseDataset = random.choice(World.EnvironmentParameters[0])
        newDataset = CandlestickDataset(BaseDataset.specifications,
                                        getDateRange(BaseDataset))
        Dataset.append(newDataset)

    return Dataset
