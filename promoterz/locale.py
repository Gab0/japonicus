#!/bin/python
from deap import tools
from deap import base
import promoterz

import coreFunctions
class Locale():
    def __init__(self, getSettings, loop):
        self.Population = []
        self.genconf = genconf

        self.GenerationMethod= GM
        self.EPOCH=0

        self.EvolutionStatistics={}

        self.TargetParameters = TargetParameters
        self.HallOfFame = tools.HallOfFame(30)

        self.tools=base.Toolbox()

        self.genconf=getSettings('generations')
        self.globalconf=getSettings('global')
        self.stratconf=getSettings('strategies')
        self.TargetParameters=getSettings()['strategies'][Strategy]

        # GENERATION METHOD SELECTION;
        # to easily employ various GA algorithms,
        # this base EPOCH processor loads a GenerationMethod file,
        # which should contain a genToolbox function to generate
        # fully working DEAP toolbox, and a reconstructTradeSettings
        # function to convert parameters from individue to usable strategy Settings;
        # Check promoterz/representation;

        genconf.Strategy = Strategy # ovrride strat defined on settings if needed;
        GenerationMethod = promoterz.selectRepresentationMethod(GenerationMethod)

        self.tools = GenerationMethod.getToolbox(self.genconf, self.TargetParameters)

        promoterz.evolutionHooks.appendToolbox(self.tools, self.HallOfFame, self.tools.population)
        promoterz.supplement.age.appendToolbox(self.tools, self.genconf.ageBoundaries)

        self.parallel = Pool(genconf.ParallelBacktests)

        availableDataRange = getAvailableDataset(exchange_source=genconf.dataset_source)
        self.DateRange = coreFunctions.getRandomDateRange(availableDataRange, genconf.deltaDays)
        print("using candlestick dataset %s" % availableDataRange)
        print("%s strategy;" % Strategy)

        self.stats = promoterz.statistics.getStatisticsMeter()

        InitialBestScores, FinalBestScores = [], []
        self.POP_SIZE = self.genconf.POP_SIZE

        print("evaluated parameters ranges %s" % promoterz.utils.flattenParameters(TargetParameters))

    def run(self):
        loop(self)
        self.EPOCH += 1
