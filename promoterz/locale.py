#!/bin/python
from deap import tools
from deap import base
import promoterz
import statistics


class Locale():

    def __init__(self, World, name, position, loop):
        self.World = World
        self.name = name
        self.EPOCH = 0
        self.position = position
        self.EvolutionStatistics = []
        self.HallOfFame = tools.HallOfFame(30)
        self.extratools = promoterz.evolutionHooks.getLocaleEvolutionToolbox(
            World, self
        )
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
        self.lastEvaluation = None
        self.lastEvaluationOnSecondary = None

        # --INIT STATISTICS;
        self.stats = statistics.getStatisticsMeter()
        self.InitialBestScores, self.FinalBestScores = [], []
        self.POP_SIZE = World.genconf.POP_SIZE
        self.loop = loop

    def run(self):
        print(self.name)
        self.loop(self.World, self)
        self.EPOCH += 1
