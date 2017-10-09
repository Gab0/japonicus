#!/bin/python
from deap import tools
from deap import base
import promoterz

import coreFunctions

from multiprocessing import Pool
class Locale():
    def __init__(self, name, getSettings, loop, globaltools):
        self.name = name
        self.EPOCH=0

        self.EvolutionStatistics={}

        self.HallOfFame = tools.HallOfFame(30)

        self.extratools=base.Toolbox()

        self.genconf=getSettings('generations')
        self.globalconf=getSettings('global')
        self.stratconf=getSettings('strategies')
        self.TargetParameters=getSettings()['strategies'][self.genconf.Strategy]

        # GENERATION METHOD SELECTION;
        # to easily employ various GA algorithms,
        # this base EPOCH processor loads a GenerationMethod file,
        # which should contain a genToolbox function to generate
        # fully working DEAP toolbox, and a reconstructTradeSettings
        # function to convert parameters from individue to usable strategy Settings;
        # Check promoterz/representation;

        #genconf.Strategy = Strategy # ovrride strat defined on settings if needed;

        #elf.GenerationMethod = promoterz.selectRepresentationMethod(GenerationMethod)

        self.tools = globaltools
        #self.tools = self.GenerationMethod.getToolbox(self.genconf, self.TargetParameters)
        promoterz.evolutionHooks.appendToolbox(self.extratools,
                                               self.HallOfFame, self.tools.population)

        promoterz.supplement.age.appendToolbox(self.extratools, self.genconf.ageBoundaries)

        # --initial population
        self.population = self.tools.population(self.genconf.POP_SIZE)

        # --start parallel pool
        self.parallel = Pool(self.genconf.ParallelBacktests)

        availableDataRange = promoterz.evaluation.gekko.getAvailableDataset(
            exchange_source=self.genconf.dataset_source)
        self.DateRange = promoterz.evaluation.gekko.getRandomDateRange(availableDataRange,
                                                                       self.genconf.deltaDays)
        print("using candlestick dataset %s" % availableDataRange)
        print("%s strategy;" % self.genconf.Strategy)

        self.stats = promoterz.statistics.getStatisticsMeter()
        promoterz.evaluation.gekko.appendToolbox(self.extratools,
                                                 self.tools.constructPhenotype,
                                                 self.DateRange)

        InitialBestScores, FinalBestScores = [], []
        self.POP_SIZE = self.genconf.POP_SIZE

        print("evaluated parameters ranges %s" % promoterz.utils.flattenParameters(self.TargetParameters))
        self.loop=loop

    def compileStats(self):
        # --get proper evolution statistics;
        Stats=self.stats.compile(self.population)
        Stats['dateRange'] = None
        Stats['maxsize'] = self.POP_SIZE
        Stats['size'] = len(self.population)
        self.EvolutionStatistics[self.EPOCH] = Stats

        LOGPATH ="%s/%s" % (self.globalconf.save_dir, self.globalconf.log_name)
        promoterz.statistics.write_evolution_logs(self.EPOCH,
                                              Stats, LOGPATH)


    def showStats(self, nb_evaluated):
        # show information;
        Stats = self.EvolutionStatistics[self.EPOCH]
        print("EPOCH %i/%i\t&%i" % (self.EPOCH, self.genconf.NBEPOCH, nb_evaluated))
        statnames = [ 'max', 'avg', 'min', 'std', 'size', 'maxsize' ]

        statText = ""
        for s in range(len(statnames)):
            SNAME = statnames[s]
            SVAL = Stats[SNAME]
            statText += "%s" % promoterz.statistics.statisticsNames[SNAME]
            if not SVAL % 1:
                statText += " %i\t" % SVAL
            else:
                statText += " %.3f\t" % SVAL
            if s % 2:
                statText += '\n'
        print(statText)
        print('')

    def run(self):
        print(self.name)
        self.loop(self)
        self.EPOCH += 1
