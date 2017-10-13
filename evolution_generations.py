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
    EvaluationMethod = promoterz.evaluation.gekko.Evaluate

    genconf=getSettings('generations')
    TargetParameters=getSettings()['strategies'][genconf.Strategy]
    GlobalTools = GenerationMethod.getToolbox(genconf, TargetParameters)

    GlobalTools.register('Evaluate', EvaluationMethod, GlobalTools.constructPhenotype)

    availableDataRange = promoterz.evaluation.gekko.getAvailableDataset(
            exchange_source=genconf.dataset_source)
    loops = [promoterz.sequence.standard_loop.standard_loop]
    World = promoterz.world.World(GlobalTools, loops, genconf, TargetParameters, NB_LOCALE, EnvironmentParameters=availableDataRange)

    while World.EPOCH < World.genconf.NBEPOCH:
        World.runEPOCH()
    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    #FinalBestScores.append(Stats['max'])

    for LOCALE in World.locales:
        BestIndividues = tools.selBest(LOCALE.population, genconf.finaltest['NBBESTINDS'])

        Z=genconf.finaltest['NBADDITIONALINDS']
        AdditionalIndividues = tools.selTournament(LOCALE.population, Z, Z*2)
        AdditionalIndividues = [x for x in AdditionalIndividues if x not in BestIndividues]
        FinalIndividues = BestIndividues + AdditionalIndividues

        for FinalIndividue in FinalIndividues:
            FinalIndividueSettings = GlobalTools.constructPhenotype(FinalIndividue)

            AssertFitness=coreFunctions.stratSettingsProofOfViability(FinalIndividueSettings, availableDataRange)
            print("Testing Strategy:\n")
            if AssertFitness[0] or AssertFitness[1] > 50:

                Show = json.dumps(FinalIndividueSettings, indent=2)
                coreFunctions.logInfo("~" * 18)


                print("Settings for Gekko config.js:")
                print(Show)
                print("Settings for Gekko --ui webpage")
                coreFunctions.logInfo(coreFunctions.pasteSettingsToUI(FinalIndividueSettings))

                print("\nRemember to check MAX and MIN values for each parameter.")
                print("\tresults may improve with extended ranges.")

            else:
                print("Strategy Fails.")



            print("")
    print("\t\t.RUN ENDS.")


