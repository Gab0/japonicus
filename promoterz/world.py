#!/bin/python
import random

import time
import math

from . import locale


class World():
    def __init__(
            self,
            GlobalTools=None,
            populationLoops=None,
            worldLoops=None,
            genconf=None,
            TargetParameters=None,
            EnvironmentParameters=None,
            onInitLocale=None,
            web=None,
    ):
        self.tools = GlobalTools

        # main components
        self.populationLoops = populationLoops
        self.worldLoops = worldLoops

        # genetic algorithm status
        self.EPOCH = 0
        self.locales = []
        self.totalEvaluations = 0

        # genetic algorithm attributes
        self.size = [500, 500]
        self.maxdistance = self.calculateDistance([0, 0], self.size)
        self.TargetParameters = TargetParameters
        self.genconf = genconf

        self.localeID = 1
        self.EnvironmentParameters = EnvironmentParameters
        self.onInitLocale = onInitLocale
        self.web = web

    def generateLocale(self):
        name = 'Locale%i' % (self.localeID)
        self.localeID += 1
        position = [random.randrange(0, self.size[x]) for x in range(2)]

        L = locale.Locale(self,
                          name,
                          position,
                          random.choice(self.populationLoops)
        )

        self.locales.append(L)

    def migration(self, source, target, number_range):
        number = random.randrange(*number_range)
        for W in range(number):
            if len(source.population):
                index = random.randrange(0, len(source.population))
                individual = source.population.pop(index)
                del individual.fitness.values
                target.population.append(individual)

    def explodeLocale(self, explLocale):
        if len(self.locales) < 2:
            return

        totaldistance = 0
        for T in self.locales:
            if explLocale == T:
                T.tempdist = 0
                continue

            distance = self.calculateDistance(
                explLocale.position, T.position)
            T.tempdist = distance
            totaldistance += distance
        for T in self.locales:
            fugitiveNumber = T.tempdist / totaldistance *\
                len(explLocale.population)

            T.fugitivenumber = int(round(fugitiveNumber))

        for T in self.locales:
            self.migration(explLocale, T,
                           (T.fugitivenumber, T.fugitivenumber + 1))
            del T.tempdist
            del T.fugitivenumber

        self.locales = [x for x in self.locales if x != locale]

    def runEpoch(self):
        epochHeader = "EPOCH %i/%i" % (
            self.EPOCH,
            self.genconf.NBEPOCH
        )

        print("\t====== %s ======" % epochHeader)
        epochStartTime = time.time()

        if self.web:
            self.epochInfo = epochHeader
            self.web.updateWorldGraph(app=self.web, WORLD=self)

        for LOCALE in self.locales:
            LOCALE.run()
            if self.web:
                self.web.updateLocaleGraph(app=self.web, LOCALE=LOCALE)

        self.worldLoops[0](self)

        self.EPOCH += 1
        epochRunTime = time.time() - epochStartTime
        print("Epoch runs in %.2f seconds;" % epochRunTime)
        if not self.EPOCH % 10:
            print("Backend power %s" % self.parallel.lasttimesperind)
        print("")

    @staticmethod
    def calculateDistance(point1, point2):
        x = abs(point1[0] - point2[0])
        y = abs(point1[1] - point2[1])
        D = math.sqrt(x ** 2 + y ** 2)
        return D

    def seedEnvironment(self):
        # round to nearest square number
        self.sectorSeedRoot = round(math.sqrt(self.genconf.worldSeedSize))

        self.environmentSectors = []
        for i in range(self.sectorSeedRoot):
            row = []
            for j in range(self.sectorSeedRoot):
                ENV = self.onInitLocale(self)
                row.append(ENV)
            self.environmentSectors.append(row)

    def loadDatasetForLocalePosition(self, position):
        pos = [math.floor(P / self.size[p] * self.sectorSeedRoot)
               for p, P in enumerate(position)]

        return self.environmentSectors[pos[0]][pos[1]]

    def localeWalk(self, locale):
        ammount = self.genconf.localeWalkDistance

        variation = [random.randrange(-ammount, ammount)
                     for i in range(2)]

        for i in range(2):
            locale.position[i] += variation[i]

            # put it inside boundaries,
            # make world appear rounded like our planet :3;

            # fix too low values
            while locale.position[i] < 0:
                locale.position[i] += self.size[i]

            # fix too high values
            locale.position[i] = locale.position[i] % self.size[i]
