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

    GenerationMethod = promoterz.functions.selectRepresentationMethod(GenerationMethod)
    EvaluationMethod = promoterz.evaluation.gekko.Evaluate

    genconf=getSettings('generations')
    globalconf = getSettings('Global')
    TargetParameters=getSettings()['strategies'][genconf.Strategy]
    GlobalTools = GenerationMethod.getToolbox(genconf, TargetParameters)

    RemoteHosts = promoterz.evaluation.gekko.loadHostsFile(globalconf.RemoteAWS)
    globalconf.GekkoURLs+=RemoteHosts
    if RemoteHosts:
        print("Connected Remote Hosts:\n%s" % ('\n').join(RemoteHosts))

    print("Evolving %s strategy;\n" % genconf.Strategy)

    print("evaluated parameters ranges:")

    Params = promoterz.utils.flattenParameters(TargetParameters)

    for k in Params.keys():
        print( "%s%s%s" % (k, " " * (30-len(k)), Params[k]) )

    GlobalTools.register('Evaluate', EvaluationMethod,
                         GlobalTools.constructPhenotype, genconf.candleSize)

    availableDataRange = promoterz.evaluation.gekko.getAvailableDataset(
            exchange_source=genconf.dataset_source)

    showdatadaterange = [ promoterz.evaluation.gekko.epochToString(availableDataRange[x])\
                    for x in ['from', 'to'] ]

    print("using candlestick dataset %s to %s" %     (showdatadaterange[0],
                                                      showdatadaterange[1]))



    loops = [ promoterz.sequence.standard_loop.standard_loop ]
    World = promoterz.world.World(GlobalTools, loops,
                                  genconf, globalconf,  TargetParameters, NB_LOCALE,
                                  EnvironmentParameters=availableDataRange)

    while World.EPOCH < World.genconf.NBEPOCH:
        World.runEPOCH()
    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    #FinalBestScores.append(Stats['max'])
    print(World.EnvironmentParameters)
    ValidationDataset =\
        promoterz.evaluation.gekko.globalEvaluationDataset(World.EnvironmentParameters,
                                                           genconf.deltaDays, 12)

    for LOCALE in World.locales:
        BestIndividues = tools.selBest(LOCALE.population, genconf.finaltest['NBBESTINDS'])

        Z=genconf.finaltest['NBADDITIONALINDS']
        AdditionalIndividues = tools.selTournament(LOCALE.population, Z, Z*2)
        AdditionalIndividues = [ x for x in AdditionalIndividues if x not in BestIndividues ]
        FinalIndividues = BestIndividues + AdditionalIndividues

        for FinalIndividue in FinalIndividues:

            AssertFitness=coreFunctions.stratSettingsProofOfViability(World,
                                                                      FinalIndividue,
                                                                      ValidationDataset)
            print("Testing Strategy:\n")
            if AssertFitness[0] or AssertFitness[1] > 50:
                FinalIndividueSettings = GlobalTools.constructPhenotype(FinalIndividue)

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


