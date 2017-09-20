#!/bin/python

import promoterz

from coreFunctions import Evaluate

def reconstructTradeSettings(Individue, PromoterMap):
    Settings = {}

    Promoters = list(PromoterMap.keys())
    for C in Individue:
        for BP in range(len(C)):
            if C[BP] in Promoters:
                read_window = C[BP+1:BP+3]
                read_window = [V for V in read_window if V < 33]
                Value = sum(read_window)
                Settings[PromoterMap[C[BP]]] = Value

    return Settings

def gekko_chromosomes(Strategy):
    chrconf = getSettings('chromosome')
    Settings = None
    population = promoters.populate(chrconf.POP_SIZE, Settings)
    StrategySettings = getSettings['strategies']['Strategy']
    PromoterMap = promoterz.initPromoterMap(StrategySettings)

    toolbox = promoterz.getToolbox()
    toolbox.register("Evaluate", reconstructTradeSettings)
    W = 0
    while W < chrconf.NBEPOCH:

        invalid_ind = [ x for x in population if not x.fitness.valid]
        to_simulation = [ (x[:], x.Strategy) for x in invalid_ind ]
        fitnesses = parallel.starmap(toolbox.evaluate, to_simulation)

        for ind, fit in zip(individues_to_simulate, fitnesses):
            ind.fitness.values = fit
