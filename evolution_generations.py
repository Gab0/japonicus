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

from Settings import getSettings

def gekko_generations(GenerationMethod, NB_LOCALE=2):
    GenerationMethod = promoterz.selectRepresentationMethod(GenerationMethod)

    genconf=getSettings('generations')
    TargetParameters=getSettings()['strategies'][genconf.Strategy]

    GlobalTools = GenerationMethod.getToolbox(genconf, TargetParameters)
    availableDataRange = promoterz.evaluation.gekko.getAvailableDataset(
            exchange_source=genconf.dataset_source)
    genLOCALE = lambda name: promoterz.Locale(name, getSettings,
                                         promoterz.sequence.standard_loop.standard_loop,
                                              GlobalTools, availableDataRange)

    LOCALEs = ['Locale%i' % (x+1) for x in range(NB_LOCALE)]
    LOCALEs = [genLOCALE(Name) for Name in LOCALEs]
    W=0
    while W < genconf.NBEPOCH:
        for K in LOCALEs:
            K.run()
        if len(LOCALEs) > 1 and random.random() < 0.1 :
            S, D=False, False
            while S == D:
                S=random.choice(LOCALEs)
                D=random.choice(LOCALEs)
            promoterz.world.migration(S, D, (1,5))
        W+=1

    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    #FinalBestScores.append(Stats['max'])

    for LOCALE in LOCALEs:
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


