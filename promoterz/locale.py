#!/bin/python
from deap import tools
from deap import base
import promoterz

import coreFunctions



class Locale():
    def __init__(self, World, name, position, loop):
        self.World = World
        self.name = name
        self.EPOCH=0
        self.position = position
        self.EvolutionStatistics={}

        self.HallOfFame = tools.HallOfFame(30)

        self.extratools=promoterz.evolutionHooks.getLocaleEvolutionToolbox(World, self)


        # GENERATION METHOD SELECTION;
        # to easily employ various GA algorithms,
        # this base EPOCH processor loads a GenerationMethod file,
        # which should contain a genToolbox function to generate
        # fully working DEAP toolbox, and a reconstructTradeSettings
        # function to convert parameters from individue to usable strategy Settings;
        # Check promoterz/representation;

        #genconf.Strategy = Strategy # ovrride strat defined on settings if needed;

        # --initial population
        self.population = World.tools.population(World.genconf.POP_SIZE)


        self.DateRange = promoterz.evaluation.gekko.getRandomDateRange(
            World.EnvironmentParameters, World.genconf.deltaDays)
        #self.extratools.register('Evaluate', World.tools.evaluatePopulation, self.DateRange)

        print("-- Initializing %s"% self.name)

        self.stats = promoterz.statistics.getStatisticsMeter()

        self.InitialBestScores, self.FinalBestScores = [], []
        self.POP_SIZE = World.genconf.POP_SIZE


        self.loop=loop

    def compileStats(self):
        # --get proper evolution statistics;
        Stats=self.stats.compile(self.population)
        Stats['dateRange'] = None
        Stats['maxsize'] = self.POP_SIZE
        Stats['size'] = len(self.population)
        self.EvolutionStatistics[self.EPOCH] = Stats

        LOGPATH ="output/evolution_gen_%s.csv" % self.name
        promoterz.statistics.write_evolution_logs(self.EPOCH,
                                              Stats, LOGPATH)

    def showStats(self, nb_evaluated,elder):
        # show information;
        Stats = self.EvolutionStatistics[self.EPOCH]
        print("EPOCH %i\t&%i" % (self.EPOCH, nb_evaluated))
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
        print('Elder dies %i' % elder)
        print('')

    def run(self):
        print(self.name)
        self.loop(self.World, self)
        self.EPOCH += 1
