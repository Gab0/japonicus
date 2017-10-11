#!/bin/python
import random
import math
import promoterz.locale

from multiprocessing import Pool
class World():
    def __init__(self, GlobalTools, loops, genconf,
                 TargetParameters, NB_LOCALE=3, EnvironmentParameters=None):
        self.tools = GlobalTools
        self.loops = loops
        self.EPOCH = 0
        self.locales = []
        self.size = [500,500]

        self.localeID=1
        self.TargetParameters = TargetParameters
        self.genconf=genconf
        self.EnvironmentParameters=EnvironmentParameters

        self.parallel = Pool(self.genconf.ParallelBacktests)
        for l in range(NB_LOCALE):
            self.generateLocale()
        print("using candlestick dataset %s" % self.EnvironmentParameters)
        print("%s strategy;" % self.genconf.Strategy)
        print("evaluated parameters ranges %s" %\
              promoterz.utils.flattenParameters(self.TargetParameters))
    def generateLocale(self):
        name = 'Locale%i' % (self.localeID)
        self.localeID +=1
        position = [random.randrange(0, self.size[x]) for x in range(2)]
        L = promoterz.locale.Locale(self, name, position, random.choice(self.loops)) 
        self.locales.append(L)

    def runEPOCH(self):
        print("\tEPOCH %i/%i" % (self.EPOCH, self.genconf.NBEPOCH))
        for LOCALE in self.locales:
            LOCALE.run()
        # APPLY MIGRATION;
        if len(self.locales) > 1 and random.random() < 0.1 :
            S, D=False, False
            while S == D:
                S=random.choice(self.locales)
                D=random.choice(self.locales)
            self.migration(S, D, (1,5))
        # --APPLY LOCALE CREATION;
        if random.random() < 0.01:
            self.generateLocale()
        # --APPLY LOCALE DESTRUCTION;
        if random.random() < 0.01:
            self.explodeLocale(random.choice(self.locales))

        self.EPOCH+=1


    def migration(self, source, target, number_range):
        number = random.randrange(*number_range)

        for W in range(number):
            index = random.randrange(0,len(source.population))
            individual = source.population.pop(index)
            del individual.fitness.values
            target.population.append(individual)

    def explodeLocale(self, locale):
        if len(self.locales) < 2:
            return
        totaldistance = 0
        for T in self.locales:
            if locale == T:
                T.tempdist=0
                continue
            distance = calculateDistance(locale.position, T.position)
            T.tempdist = distance
            totaldistance+=distance
        for T in self.locales:
            T.fugitivenumber=T.tempdist/totaldistance * len(locale.population)
        for T in self.locales:
            self.migration(locale, T, (T.fugitivenumber, T.fugitivenumber+1))
            del T.tempdist
            del T.fugitivenumber
        del locale

def calculateDistance(point1, point2):
    x = abs(point1[0] - point2[0])
    y = abs(point1[1] - point2[1])

    D = math.sqrt(x**2 + y**2)
    return D
