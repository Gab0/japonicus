#!/bin/python
import random
import promoterz.locale
import time
from functools import partial

import promoterz.sequence.parallel_world


class World():

    def __init__(
            self,
            GlobalTools=None,
            loops=None,
            genconf=None,
            TargetParameters=None,
            EnvironmentParameters=None,
            onInitLocale=None,
            web=None,
    ):
        self.tools = GlobalTools
        self.loops = loops
        self.EPOCH = 0
        self.locales = []
        self.size = [500, 500]
        self.maxdistance = promoterz.sequence.parallel_world.calculateDistance([0, 0], self.size)
        self.localeID = 1
        self.TargetParameters = TargetParameters
        self.genconf = genconf
        self.EnvironmentParameters = EnvironmentParameters
        self.runEPOCH = partial(promoterz.sequence.parallel_world.world_EPOCH, self)
        self.onInitLocale = onInitLocale
        self.web = web
        self.totalEvaluations = 0

    def generateLocale(self):
        name = 'Locale%i' % (self.localeID)
        self.localeID += 1
        position = [random.randrange(0, self.size[x]) for x in range(2)]
        L = promoterz.locale.Locale(self, name, position, random.choice(self.loops))
        if self.onInitLocale:
            self.onInitLocale(self, L)
        if self.web:
            self.web.newGraphic(name)
        self.locales.append(L)

    def migration(self, source, target, number_range):
        number = random.randrange(*number_range)
        for W in range(number):
            if len(source.population):
                index = random.randrange(0, len(source.population))
                individual = source.population.pop(index)
                del individual.fitness.values
                target.population.append(individual)

    def explodeLocale(self, locale):
        if len(self.locales) < 2:
            return

        if self.web:
            for g in range(len(self.web.GraphicList)):
                if self.web.GraphicList[g].id == locale.name:
                    self.web.GraphicList[g].Active = False
        totaldistance = 0
        for T in self.locales:
            if locale == T:
                T.tempdist = 0
                continue

            distance = promoterz.sequence.parallel_world.calculateDistance(
                locale.position, T.position)
            T.tempdist = distance
            totaldistance += distance
        for T in self.locales:
            T.fugitivenumber = int(
                round(T.tempdist / totaldistance * len(locale.population))
            )
        for T in self.locales:
            self.migration(locale, T, (T.fugitivenumber, T.fugitivenumber + 1))
            del T.tempdist
            del T.fugitivenumber
        self.locales = [x for x in self.locales if x != locale]
