#!/bin/python
import json
import random
import promoterz

from copy import deepcopy

import resultInterface

import promoterz.sequence.standard_loop

from deap import tools
from deap import algorithms
from deap import base

from Settings import getSettings
import stratego
from functools import partial
StrategyFileManager = None


# TEMPORARY ASSIGNMENT OF EVAL FUNCTIONS; SO THINGS REMAIN SANE (SANE?);
def aEvaluate(StrategyFileManager, constructPhenotype,
              candleSize, Database, DateRange, Individual, gekkoUrl):
    phenotype = constructPhenotype(Individual)
    StratName = StrategyFileManager.checkStrategy(phenotype)
    phenotype = {StratName:phenotype}
    SCORE = promoterz.evaluation.gekko.Evaluate(candleSize, Database, 
                                                DateRange, phenotype, gekkoUrl)
    return SCORE

def bEvaluate(constructPhenotype, candleSize, Database,
              DateRange, Individual, gekkoUrl):
    phenotype = constructPhenotype(Individual)
    phenotype = {Individual.Strategy: phenotype}
    SCORE = promoterz.evaluation.gekko.Evaluate(candleSize, Database,
                                                DateRange, phenotype, gekkoUrl)
    return SCORE


def gekko_generations(TargetParameters, GenerationMethod, EvaluationMode, NB_LOCALE=2):

    GenerationMethod = promoterz.functions.selectRepresentationMethod(GenerationMethod)

    genconf=getSettings('generations')
    globalconf = getSettings('Global')

    if EvaluationMode == 'indicator':
        #global StrategyFileManager
        StrategyFileManager = stratego.gekko_strategy.StrategyFileManager(globalconf.gekkoPath)
        Evaluate = partial(aEvaluate, StrategyFileManager)
        Strategy = None
    else:
        Evaluate = bEvaluate
        Strategy = EvaluationMode

    print("Evolving %s strategy;\n" % Strategy)

    print("evaluated parameters ranges:")

    TargetParameters = promoterz.utils.flattenParameters(TargetParameters)

    GlobalTools = GenerationMethod.getToolbox(Strategy, genconf, TargetParameters)


    RemoteHosts = promoterz.evaluation.gekko.loadHostsFile(globalconf.RemoteAWS)
    globalconf.GekkoURLs+=RemoteHosts
    if RemoteHosts:
        print("Connected Remote Hosts:\n%s" % ('\n').join(RemoteHosts))
        if EvaluationMode == 'indicator':
            exit('Indicator mode is yet not compatible with multiple hosts.')

    for k in TargetParameters.keys():
        print( "%s%s%s" % (k, " " * (30-len(k)), TargetParameters[k]) )

    datasetSpecifications, availableDataRange = promoterz.evaluation.gekko.getAvailableDataset(
            exchange_source=genconf.dataset_source)




    GlobalTools.register('Evaluate', Evaluate,
                         GlobalTools.constructPhenotype, genconf.candleSize, datasetSpecifications)




    showdatadaterange = [ promoterz.evaluation.gekko.epochToString(availableDataRange[x])\
                    for x in ['from', 'to'] ]

    print()
    print("using candlestick dataset %s to %s" %     (showdatadaterange[0],
                                                      showdatadaterange[1]))

    print()

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
    # After running EPOCHs, select best candidates;
    for LOCALE in World.locales:
        B=genconf.finaltest['NBBESTINDS']
        BestIndividues = tools.selBest(LOCALE.population,B)

        Z=genconf.finaltest['NBADDITIONALINDS']
        print("Selecting %i+%i individues, random test;" % (B,Z))
        AdditionalIndividues = promoterz.evolutionHooks.Tournament(LOCALE.population, Z, Z*2)

        print("%i selected;" % len(AdditionalIndividues))
        AdditionalIndividues = [ x for x in AdditionalIndividues\
                                 if x not in BestIndividues ]

        FinalIndividues = BestIndividues + AdditionalIndividues

        print("%i selected;" % len(FinalIndividues))
        for FinalIndividue in FinalIndividues:
            proof = resultInterface.stratSettingsProofOfViability
            AssertFitness, FinalProfit = proof(World,
                                              FinalIndividue,
                                              ValidationDataset)
            print("Testing Strategy:\n")
            if AssertFitness or FinalProfit > 50:
                FinalIndividueSettings = GlobalTools.constructPhenotype(
                    FinalIndividue)

                Show = json.dumps(FinalIndividueSettings, indent=2)
                resultInterface.logInfo("~" * 18)

                resultInterface.logInfo("%.3f final profit ~~~~" % FinalProfit)
                print("Settings for Gekko config.js:")
                print(Show)
                print("Settings for Gekko --ui webpage")
                resultInterface.logInfo(resultInterface.pasteSettingsToUI(FinalIndividueSettings))

                print("\nRemember to check MAX and MIN values for each parameter.")
                print("\tresults may improve with extended ranges.")

            else:
                print("Strategy Fails.")



            print("")
    print("\t\t.RUN ENDS.")


