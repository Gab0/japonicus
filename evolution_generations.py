#!/bin/python
import json
import random
import promoterz

from copy import deepcopy

import coreFunctions

import promoterz.sequence.standard_loop



from deap import tools
from deap import algorithms
from deap import base

from Settings import getSettings

def gekko_generations(settings, GenerationMethod, NB_LOCALE=2):

    GenerationMethod = promoterz.selectRepresentationMethod(GenerationMethod)

    genconf=getSettings('generations')
    TargetParameters=getSettings()['strategies'][genconf.Strategy]
    GlobalTools = GenerationMethod.getToolbox(genconf, TargetParameters)


    availableDataRange = promoterz.evaluation.gekko.getAvailableDataset(
            exchange_source=genconf.dataset_source)
    loops = [promoterz.sequence.standard_loop.standard_loop]
    World = promoterz.world.World(GlobalTools, loops, genconf, TargetParameters, NB_LOCALE, EnvironmentParameters=availableDataRange)

    while World.EPOCH < World.genconf.NBEPOCH:
        World.runEPOCH()
    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    #FinalBestScores.append(Stats['max'])

    for LOCALE in World.locales:
        FinalIndividue = tools.selBest(LOCALE.population, 1)[0]
        FinalIndividueSettings = GlobalTools.constructPhenotype(FinalIndividue)

        Show = json.dumps(FinalIndividueSettings, indent=2)
        coreFunctions.logInfo("~" * 18)

        ''' DEPRECATED;
        for S in range(len(FinalBestScores)):

            coreFunctions.logInfo("Candlestick Set %i: \n\n" % (S+1)+\
                                  "EPOCH ONE BEST PROFIT: %.3f\n" % InitialBestScores[S] +\
                                  "FINAL EPOCH BEST PROFIT: %.3f\n" % FinalBestScores[S])
        '''

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
        print("")
    print("\t\t.RUN ENDS.")


