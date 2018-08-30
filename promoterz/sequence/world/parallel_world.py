#!/bin/python
import random
import itertools
import math
import time


def execute(World):

    # --APPLY MIGRATION BETWEEN LOCALES;
    if len(World.locales):
        S, D = False, False
        LocalePairs = itertools.combinations(World.locales, 2)
        for L in LocalePairs:
            distance = World.calculateDistance(L[0].position, L[1].position)
            distance_weight = distance / World.maxdistance
            if random.random() > distance_weight:
                World.migration(L[0], L[1], (1, 7))
                World.migration(L[1], L[0], (1, 7))

    # --APPLY LOCALE CREATION;
    if random.random() < 0.01:
        World.generateLocale()

    # --APPLY RANDOMIC LOCALE DESTRUCTION;
    if random.random() < World.genconf.localeExplodeChance / 100:
        chosenLocale = random.choice(World.locales)
        World.explodeLocale(chosenLocale)

    # --APPLY EXPECTED LOCALE DESTRUCTION;
    for L in range(len(World.locales)):
        if World.locales[L].EPOCH > World.genconf.localeExpirationAge:
            if len(World.locales) > 2:
                World.explodeLocale(World.locales[L])
                #  if two locales are destroyed @ same time, post-locale migrations
                #  will be a mess
                break



