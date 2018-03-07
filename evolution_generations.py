#!/bin/python
import json
import random
import datetime

import promoterz
import evaluation

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

from datasetOperations import *

from japonicus_options import options, args
StrategyFileManager = None

# TEMPORARY ASSIGNMENT OF EVAL FUNCTIONS; SO THINGS REMAIN SANE (¿SANE?);
def aEvaluate(StrategyFileManager, constructPhenotype,
              genconf, Database, DateRange, Individual, gekkoUrl):
    phenotype = constructPhenotype(Individual)
    StratName = StrategyFileManager.checkStrategy(phenotype)
    phenotype = {StratName:phenotype}

    SCORE = evaluation.gekko.backtest.Evaluate(genconf, Database, 
                                                DateRange, phenotype, gekkoUrl)
    return SCORE

def bEvaluate(constructPhenotype, genconf, Database,
              DateRange, Individual, gekkoUrl):

    phenotype = constructPhenotype(Individual)
    phenotype = {Individual.Strategy: phenotype}

    SCORE = evaluation.gekko.backtest.Evaluate(genconf, Database,
                                                DateRange, phenotype, gekkoUrl)
    return SCORE


def gekko_generations(TargetParameters, GenerationMethod,
                      EvaluationMode, NB_LOCALE=2, web=None):


    # --LOAD SETTINGS;
    genconf=getSettings('generations')
    globalconf = getSettings('Global')
    datasetconf = getSettings('dataset')
    indicatorconf = getSettings()['indicators']

    # --APPLY COMMAND LINE GENCONF SETTINGS;
    for parameter in genconf.__dict__.keys():
        if parameter in options.__dict__.keys():
            if options.__dict__[parameter] != None:
                genconf.__dict__[parameter] = options.__dict__[parameter]


    GenerationMethod = promoterz.functions.selectRepresentationMethod(GenerationMethod)
    if EvaluationMode == 'indicator':
        #global StrategyFileManager
        StrategyFileManager = stratego.gekko_strategy.StrategyFileManager(
            globalconf.gekkoPath, indicatorconf)
        Evaluate = partial(aEvaluate, StrategyFileManager)
        Strategy = options.skeleton

    # --for standard methods;
    else:
        Evaluate = bEvaluate
        Strategy = EvaluationMode


    TargetParameters = promoterz.parameterOperations.flattenParameters(TargetParameters)
    TargetParameters = promoterz.parameterOperations.parameterValuesToRangeOfValues(
        TargetParameters,
        genconf.parameter_spread)

    GlobalTools = GenerationMethod.getToolbox(Strategy, genconf, TargetParameters)

    RemoteHosts = evaluation.gekko.API.loadHostsFile(globalconf.RemoteAWS)
    globalconf.GekkoURLs += RemoteHosts

    if RemoteHosts:
        print("Connected Remote Hosts:\n%s" % ('\n').join(RemoteHosts))
        if EvaluationMode == 'indicator':
            exit('Indicator mode is yet not compatible with multiple hosts.')


    # --GRAB PRIMARY (EVOLUTION) DATASET
    D = evaluation.gekko.dataset.selectCandlestickData(
            exchange_source=datasetconf.dataset_source)
    evolutionDataset = CandlestickDataset(*D)
    evolutionDataset.restrain(datasetconf.dataset_span)

    # --GRAB SECONDARY (EVALUATION) DATASET
    try:
        D = evaluation.gekko.dataset.selectCandlestickData(
        exchange_source = datasetconf.eval_dataset_source,
        avoidCurrency=evolutionDataset.specifications['asset'] )
        evaluationDataset = CandlestickDataset(*D)
        evaluationDataset.restrain(datasetconf.eval_dataset_span)
    except RuntimeError:
        evaluationDataset = None
        print("Evaluation dataset not found.")


    # --INITIALIZE LOGGER;
    ds_specs = evolutionDataset.specifications

    logfilename = "%s-%s-%s-%s-%s" % (Strategy,
                                      ds_specs['exchange'],
                                      ds_specs['currency'],
                                      ds_specs['asset'],
                                      str(datetime.datetime.now())[-6:])

    Logger = promoterz.logger.Logger(logfilename)

    # --SHOW PARAMETER INFO;
    if Strategy:
        Logger.log("Evolving %s strategy;\n" % Strategy)

    Logger.log("evaluated parameters ranges:", target = "Header")

    for k in TargetParameters.keys():
        Logger.log( "%s%s%s\n" % (k, " " * (30-len(k)),
                                  TargetParameters[k]), target="Header" )

    # --LOG CONFIG INFO;
    configInfo = json.dumps(genconf.__dict__, indent=4)
    Logger.log(configInfo, target="Header", show=False)

    # --SHOW DATASET INFO;
    Logger.log(interface.parseDatasetInfo("evolution",
                                          evolutionDataset), target="Header")

    if evaluationDataset:
        Logger.log(interface.parseDatasetInfo("evaluation",
                                              evaluationDataset), target="Header")

    # --INITIALIZE WORLD WITH CANDLESTICK DATASET INFO; HERE THE GA KICKS IN;
    GlobalTools.register('Evaluate', Evaluate,
                         GlobalTools.constructPhenotype, genconf )

    # --THIS LOADS A DATERANGE FOR A LOCALE;
    def onInitLocale(World, locale):
        locale.DateRange = getLocaleDateRange(World, locale)


    loops = [ promoterz.sequence.standard_loop.standard_loop ]
    World = promoterz.world.World(GlobalTools, loops,
                                  genconf, globalconf, TargetParameters, NB_LOCALE,
                                  EnvironmentParameters=[ evolutionDataset,
                                                          evaluationDataset ],
                                  onInitLocale=onInitLocale,web=web)
    World.logger = Logger
    World.EvaluationStatistics = []
    World.logger.updateFile()

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


