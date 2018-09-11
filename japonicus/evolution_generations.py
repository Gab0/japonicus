#!/bin/python
import json
import random
import time
import datetime
import sys

import promoterz
import evaluation

from copy import deepcopy

from . import interface

from deap import tools
from deap import algorithms
from deap import base

from .Settings import getSettings, makeSettings
import stratego
from functools import partial

import evaluation.gekko.datasetOperations as datasetOperations


StrategyFileManager = None


# TEMPORARY ASSIGNMENT OF EVAL FUNCTIONS; SO THINGS REMAIN ¿SANE;
def indicatorEvaluate(
    StrategyFileManager,
    constructPhenotype,
    genconf,
    Datasets,
    Individual,
    gekkoUrl,
):
    phenotype = constructPhenotype(Individual)
    StratName = StrategyFileManager.checkStrategy(phenotype)
    phenotype = {StratName: phenotype}
    SCORE = evaluation.gekko.backtest.Evaluate(
        genconf, Datasets, phenotype, gekkoUrl
    )
    return SCORE


def standardEvaluate(constructPhenotype, genconf, Datasets, Individual, gekkoUrl):
    phenotype = constructPhenotype(Individual)
    phenotype = {Individual.Strategy: phenotype}
    SCORE = evaluation.gekko.backtest.Evaluate(
        genconf, Datasets, phenotype, gekkoUrl
    )
    return SCORE


def benchmarkEvaluate(constructPhenotype, genconf, Datasets, Individual, gekkoUrl):
    phenotype = constructPhenotype(Individual)
    phenotype = {Individual.Strategy: phenotype}
    SCORE = evaluation.benchmark.benchmark.Evaluate(
        genconf, phenotype
    )
    return SCORE


def grabDatasets(datasetconf, GekkoURL):
    # CHECK HOW MANY EVOLUTION DATASETS ARE SPECIFIED AT SETTINGS;
    evolutionDatasetNames = ['dataset_source']
    evolutionDatasets = []
    for DS in range(1, 100):
        datasetConfigName = 'dataset_source%i' % DS
        if datasetConfigName in datasetconf.__dict__.keys():
            evolutionDatasetNames.append(datasetConfigName)
    # --GRAB PRIMARY (EVOLUTION) DATASETS
    for evolutionDatasetName in evolutionDatasetNames:
        D = evaluation.gekko.dataset.selectCandlestickData(GekkoURL,
            exchange_source=datasetconf.__dict__[evolutionDatasetName]
        )
        evolutionDatasets.append(datasetOperations.CandlestickDataset(*D))
        try:
            evolutionDatasets[-1].restrain(datasetconf.dataset_span)
        except Exception:
            print('dataset_ span not configured for evolutionDatasetName. skipping...')

    # --GRAB SECONDARY (EVALUATION) DATASET
    try:
        D = evaluation.gekko.dataset.selectCandlestickData(
            GekkoURL,
            exchange_source=datasetconf.eval_dataset_source,
            avoidCurrency=evolutionDatasets[0].specifications['asset'],
        )
        evaluationDatasets = [datasetOperations.CandlestickDataset(*D)]
        evaluationDatasets[0].restrain(datasetconf.eval_dataset_span)
    except RuntimeError:
        evaluationDatasets = []
        print("Evaluation dataset not found.")

    return evolutionDatasets, evaluationDatasets


def gekko_generations(
        TargetParameters, GenerationMethod, EvaluationMode, settings,
        options, web=None):

    # --LOAD SETTINGS;
    genconf = makeSettings(settings['generations'])
    globalconf = makeSettings(settings['global'])
    datasetconf = makeSettings(settings['dataset'])
    indicatorconf = makeSettings(settings['indicators'])
    backtestconf = makeSettings(settings['backtest'])
    evalbreakconf = makeSettings(settings['evalbreak'])

    # --APPLY COMMAND LINE GENCONF SETTINGS;
    for parameter in genconf.__dict__.keys():
        if parameter in options.__dict__.keys():
            if options.__dict__[parameter] != None:
                genconf.__dict__[parameter] = options.__dict__[parameter]
    GenerationMethod = promoterz.functions.selectRepresentationMethod(GenerationMethod)
    if EvaluationMode == 'indicator':
        # global StrategyFileManager
        StrategyFileManager = stratego.gekko_strategy.StrategyFileManager(
            globalconf.gekkoPath, indicatorconf
        )
        Evaluate = partial(indicatorEvaluate, StrategyFileManager)
        Strategy = options.skeleton
    # --for standard methods;
    else:
        Strategy = EvaluationMode
        if options.benchmarkMode:
            Evaluate = benchmarkEvaluate
            evolutionDatasets, evaluationDatasets = [], []
            genconf.minimumProfitFilter = None
        else:
            Evaluate = standardEvaluate
            evolutionDatasets, evaluationDatasets = grabDatasets(datasetconf, globalconf.GekkoURLs[0])

    # -- PARSE TARGET PARAMETERS
    TargetParameters = promoterz.parameterOperations.flattenParameters(TargetParameters)
    TargetParameters = promoterz.parameterOperations.parameterValuesToRangeOfValues(
        TargetParameters, genconf.parameter_spread
    )
    GlobalTools = GenerationMethod.getToolbox(Strategy, genconf, TargetParameters)
    RemoteHosts = evaluation.gekko.API.loadHostsFile(globalconf.RemoteAWS)
    globalconf.GekkoURLs += RemoteHosts
    if RemoteHosts:
        print("Connected Remote Hosts:\n%s" % ('\n').join(RemoteHosts))
        if EvaluationMode == 'indicator':
            exit('Indicator mode is yet not compatible with multiple hosts.')

    # --INITIALIZE LOGGER;
    todayDate = time.strftime("%Y_%m_%d-%H.%M.%S", time.gmtime())
    if evolutionDatasets:
        ds_specs = evolutionDatasets[0].specifications
        logfilename = "%s-%s-%s-%s-%s" % (
            Strategy,
            ds_specs['exchange'],
            ds_specs['currency'],
            ds_specs['asset'],
            todayDate
        )
    else:
        logfilename = "benchmark%s" % todayDate
    Logger = promoterz.logger.Logger(logfilename)

    # --PRINT RUNTIME ARGS TO LOG HEADER;
    ARGS = ' '.join(sys.argv)
    Logger.log(ARGS, target='Header')

    # --SHOW PARAMETER INFO;
    if Strategy:
        Logger.log("Evolving %s strategy;\n" % Strategy)
    Logger.log("evaluated parameters ranges:", target="Header")
    for k in TargetParameters.keys():
        Logger.log(
            "%s%s%s\n" % (k, " " * (30 - len(k)), TargetParameters[k]),
            target="Header"
        )

    # --LOG CONFIG INFO;
    configInfo = json.dumps(genconf.__dict__, indent=4)
    Logger.log(configInfo, target="Header", show=False)

    # --SHOW DATASET INFO;
    for evolutionDataset in evolutionDatasets:
        Logger.log(
            interface.parseDatasetInfo("evolution", evolutionDataset),
            target="Header"
        )
    if evaluationDatasets:
        for evaluationDataset in evaluationDatasets:
            Logger.log(
                interface.parseDatasetInfo("evaluation", evaluationDataset),
                target="Header"
            )

    # --INITIALIZE WORLD WITH CANDLESTICK DATASET INFO; HERE THE GA KICKS IN;
    GlobalTools.register('Evaluate', Evaluate,
                         GlobalTools.constructPhenotype, backtestconf)

    # --THIS LOADS A DATERANGE FOR A LOCALE;
    if options.benchmarkMode:
        def onInitLocale(World):
            Dataset = [
                datasetOperations.CandlestickDataset(
                    {},
                    {
                        'from': 0,
                        'to': 0
                    }
                )]
            return Dataset
    else:
        def onInitLocale(World):
            Dataset = datasetOperations.getLocaleDataset(World)
            return Dataset

    populationLoops = [promoterz.sequence.locale.standard_loop.execute]
    worldLoops = [promoterz.sequence.world.parallel_world.execute]
    World = promoterz.world.World(
        GlobalTools=GlobalTools,
        populationLoops=populationLoops,
        worldLoops=worldLoops,
        genconf=genconf,
        TargetParameters=TargetParameters,
        EnvironmentParameters={
            'evolution':  evolutionDatasets,
            'evaluation': evaluationDatasets
        },
        onInitLocale=onInitLocale,
        web=web,
    )
    World.logger = Logger
    World.EvaluationStatistics = []

    World.backtestconf = backtestconf
    World.evalbreakconf = evalbreakconf
    World.globalconf = globalconf

    World.seedEnvironment()

    World.logger.updateFile()

    # INITALIZE EVALUATION PROCESSING POOL
    World.parallel = promoterz.evaluationPool.EvaluationPool(
            World.tools.Evaluate,
            globalconf.GekkoURLs,
            backtestconf.ParallelBacktests,
            genconf.showIndividualEvaluationInfo,
        )

    # --GENERATE INITIAL LOCALES;
    for l in range(genconf.NBLOCALE):
        World.generateLocale()

    # --RUN EPOCHES;
    while World.EPOCH < World.genconf.NBEPOCH:
        World.runEpoch()
        if evalbreakconf.evaluateSettingsPeriodically and not options.benchmarkMode:
            if not World.EPOCH % evalbreakconf.evaluateSettingsPeriodically:
                promoterz.evaluationBreak.showResults(World)
        if not World.EPOCH % 10:
            print("Total Evaluations: %i" % World.totalEvaluations)

    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    # FinalBestScores.append(Stats['max'])
    print(World.EnvironmentParameters)
    # After running EPOCHs, select best candidates;
    if not options.benchmarkMode:
        promoterz.evaluationBreak.showResults(World)
    print("")
    print("\t\t.RUN ENDS.")
