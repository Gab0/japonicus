#!/bin/python
import random

def world_EPOCH(World):
    print("\t======  EPOCH %i/%i  ======" % (World.EPOCH,
                                             World.genconf.NBEPOCH))
    stime = time.time()
    for LOCALE in World.locales:
        LOCALE.run()

    # --APPLY MIGRATION BETWEEN LOCALES;
    if len(World.locales) > 1 and random.random() < (1-0.1 :
        S, D=False, False
        while S == D:
            S=random.choice(World.locales)
            D=random.choice(World.locales)
        World.migration(S, D, (1,5))

    # --APPLY LOCALE CREATION;
    if random.random() < 0.01:
        World.generateLocale()

    # --APPLY LOCALE DESTRUCTION;
    if random.random() < 0.01:
        World.explodeLocale(random.choice(World.locales))

    World.EPOCH+=1
    etime = time.time() - stime
    print("Epoch runs in %.2f seconds;" % etime)
    if not World.EPOCH % 10:
        print("Backend power %s" % World.parallel.lasttimesperind)
    print("")

def calculateDistance(point1, point2):
    x = abs(point1[0] - point2[0])
    y = abs(point1[1] - point2[1])

    D = math.sqrt(x**2 + y**2)
    return D
