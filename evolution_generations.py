#!/bin/python
import json
import random
import promoterz

from copy import deepcopy

import coreFunctions


from promoterz.supplement.geneticDivergence import *
from promoterz.supplement.age import *
import promoterz.supplement.PRoFIGA
import promoterz.sequence.standard_loop
from Settings import getSettings

from multiprocessing import Pool

from deap import tools
from deap import algorithms
from deap import base



def gekko_generations(GenerationMethod):
    LOCALE = promoterz.Locale(getSettings, promoterz.sequence.standard_loop.standard_loop, GenerationMethod)
    W=0
    while W < LOCALE.genconf.NBEPOCH:
        LOCALE.run()


    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    FinalBestScores.append(Stats['max'])
    FinalIndividue = tools.selBest(LOCALE.population, 1)[0]
    FinalIndividueSettings = GenerationMethod.constructPhenotype(FinalIndividue)

    Show = json.dumps(FinalIndividueSettings, indent=2)
    coreFunctions.logInfo("~" * 18)

    for S in range(len(FinalBestScores)):
        coreFunctions.logInfo("Candlestick Set %i: \n\n" % (S+1)+\
                "EPOCH ONE BEST PROFIT: %.3f\n" % InitialBestScores[S] +\
                "FINAL EPOCH BEST PROFIT: %.3f\n" % FinalBestScores[S])


    print("Settings for Gekko config.js:")
    print(Show)
    print("Settings for Gekko --ui webpage")
    coreFunctions.logInfo(coreFunctions.pasteSettingsToUI(FinalIndividueSettings))

    print("\nRemember to check MAX and MIN values for each parameter.")
    print("\tresults may improve with extended ranges.")

    print("Testing Strategy:\n")
    Vv=coreFunctions.stratSettingsProofOfViability(FinalIndividueSettings, availableDataRange)
    Vv = "GOOD STRAT" if Vv else "SEEMS BAD"
    coreFunctions.logInfo(Vv)
    print("\t\t.RUN ENDS.")

    return FinalIndividueSettings, EvolutionStatistics
