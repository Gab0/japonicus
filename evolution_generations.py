#!/bin/python
import json
import random
import promoterz

from copy import deepcopy

import resultInterface
import interface

import promoterz.sequence.standard_loop

from deap import tools
from deap import algorithms
from deap import base

from Settings import getSettings
import stratego
from functools import partial

StrategyFileManager = None

class CandlestickDataset():
    def __init__(self, specifications, datarange):
        self.daterange = datarange
        self.specifications = specifications

# TEMPORARY ASSIGNMENT OF EVAL FUNCTIONS; SO THINGS REMAIN SANE (SANE?);
def aEvaluate(StrategyFileManager, constructPhenotype,
              genconf, Database, DateRange, Individual, gekkoUrl):
    phenotype = constructPhenotype(Individual)
    StratName = StrategyFileManager.checkStrategy(phenotype)
    phenotype = {StratName:phenotype}

    SCORE = promoterz.evaluation.gekko.Evaluate(genconf, Database, 
                                                DateRange, phenotype, gekkoUrl)
    return SCORE

def bEvaluate(constructPhenotype, genconf, Database,
              DateRange, Individual, gekkoUrl):

    phenotype = constructPhenotype(Individual)
    phenotype = {Individual.Strategy: phenotype}

    SCORE = promoterz.evaluation.gekko.Evaluate(genconf, Database,
                                                DateRange, phenotype, gekkoUrl)
    return SCORE


def gekko_generations(TargetParameters, GenerationMethod,
                      EvaluationMode, NB_LOCALE=2, web=None):

    Logger = promoterz.logger.Logger()
    GenerationMethod = promoterz.functions.selectRepresentationMethod(GenerationMethod)

    genconf=getSettings('generations')
    globalconf = getSettings('Global')
    datasetconf = getSettings('dataset')

    if EvaluationMode == 'indicator':
        #global StrategyFileManager
        StrategyFileManager = stratego.gekko_strategy.StrategyFileManager(globalconf.gekkoPath)
        Evaluate = partial(aEvaluate, StrategyFileManager)
        Strategy = None

    # --for standard methods;
    else:
        Evaluate = bEvaluate
        Strategy = EvaluationMode

    Logger.log("Evolving %s strategy;\n" % Strategy)

    print("evaluated parameters ranges:")

    TargetParameters = promoterz.parameterOperations.flattenParameters(TargetParameters)
    TargetParameters = promoterz.parameterOperations.parameterValuesToRangeOfValues(
        TargetParameters,
        genconf.parameter_spread)

    GlobalTools = GenerationMethod.getToolbox(Strategy, genconf, TargetParameters)

    RemoteHosts = promoterz.evaluation.gekko.loadHostsFile(globalconf.RemoteAWS)
    globalconf.GekkoURLs += RemoteHosts

    if RemoteHosts:
        print("Connected Remote Hosts:\n%s" % ('\n').join(RemoteHosts))
        if EvaluationMode == 'indicator':
            exit('Indicator mode is yet not compatible with multiple hosts.')

    for k in TargetParameters.keys():
        Logger.log( "%s%s%s" % (k, " " * (30-len(k)), TargetParameters[k]) )

    # --GRAB PRIMARY (EVOLUTION) DATASET
    D = promoterz.evaluation.gekko.selectCandlestickData(
            exchange_source=datasetconf.dataset_source)
    evolutionDataset = CandlestickDataset(*D)

    # --GRAB SECONDARY (EVALUATION) DATASET
    try:
        D = promoterz.evaluation.gekko.selectCandlestickData(
        exchange_source = datasetconf.eval_dataset_source,
        avoidCurrency = evolutionDataset.specifications['asset'] )
        evaluationDataset = CandlestickDataset(*D)
    except RuntimeError:
        evaluationDataset = None
        print("Evaluation dataset not found.")



    # --SHOW DATASET INFO;
    interface.showDatasetInfo("evolution",
                              evolutionDataset)

    if evaluationDataset:
        interface.showDatasetInfo("evaluation",
                                  evaluationDataset)

    # --INITIALIZE WORLD WITH CANDLESTICK DATASET INFO;
    GlobalTools.register('Evaluate', Evaluate,
                         GlobalTools.constructPhenotype, genconf )


    loops = [ promoterz.sequence.standard_loop.standard_loop ]
    World = promoterz.world.World(GlobalTools, loops,
                                  genconf, globalconf, TargetParameters, NB_LOCALE,
                                  EnvironmentParameters=[ evolutionDataset,
                                                          evaluationDataset ], web=web)
    World.logger = Logger
    # --RUN EPOCHES;
    while World.EPOCH < World.genconf.NBEPOCH:
        World.runEPOCH()
        if genconf.evaluateSettingsPeriodically:
            if not World.EPOCH % genconf.evaluateSettingsPeriodically:
                resultInterface.showResults(World)

    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    # FinalBestScores.append(Stats['max'])
    print(World.EnvironmentParameters)
    # After running EPOCHs, select best candidates;
    resultInterface.showResults(World)



    print("")
    print("\t\t.RUN ENDS.")


