#!/bin/python
import random
import itertools
import math
import time


def world_EPOCH(World):
    print("\t======  EPOCH %i/%i  ======" % (World.EPOCH, World.genconf.NBEPOCH))
    stime = time.time()
    for LOCALE in World.locales:
        try:
            LOCALE.run()
        except AssertionError:
            World.logger.log("Locale exploding due to assertion error! (zero population)")
            World.explodeLocale(LOCALE)
        if World.web:
            for F in range(len(World.web.GraphicList)):
                if World.web.GraphicList[F].id == LOCALE.name:
                    World.web.GraphicList[F].__setattr__(
                        'figure',
                        World.web.update_graph(LOCALE.name, LOCALE.EvolutionStatistics),
                    )
    # --APPLY MIGRATION BETWEEN LOCALES;
    if len(World.locales):
        S, D = False, False
        LocalePairs = itertools.combinations(World.locales, 2)
        for L in LocalePairs:
            distance = calculateDistance(L[0].position, L[1].position)
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

    
    World.EPOCH += 1
    etime = time.time() - stime
    print("Epoch runs in %.2f seconds;" % etime)
    if not World.EPOCH % 10:
        print("Backend power %s" % World.parallel.lasttimesperind)
    print("")


def calculateDistance(point1, point2):
    x = abs(point1[0] - point2[0])
    y = abs(point1[1] - point2[1])
    D = math.sqrt(x ** 2 + y ** 2)
    return D
