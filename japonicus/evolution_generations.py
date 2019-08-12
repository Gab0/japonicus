#!/bin/python
import json
import time
import sys

import promoterz
import evaluation

from . import interface

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


def standardEvaluate(constructPhenotype,
                     genconf, Datasets, Individual, gekkoUrl):
    phenotype = constructPhenotype(Individual)
    phenotype = {Individual.Strategy: phenotype}
    SCORE = evaluation.gekko.backtest.Evaluate(
        genconf, Datasets, phenotype, gekkoUrl
    )
    return SCORE


def benchmarkEvaluate(constructPhenotype,
                      genconf, Datasets, Individual, gekkoUrl):
    phenotype = constructPhenotype(Individual)
    phenotype = {Individual.Strategy: phenotype}
    SCORE = evaluation.benchmark.benchmark.Evaluate(
        genconf, phenotype
    )
    return SCORE


def grabDatasets(conf):
    # CHECK HOW MANY EVOLUTION DATASETS ARE SPECIFIED AT SETTINGS;
    evolutionDatasetNames = ['dataset_source']
    evolutionDatasets = []
    for DS in range(1, 100):
        datasetConfigName = 'dataset_source%i' % DS
        if datasetConfigName in conf.dataset.__dict__.keys():
            evolutionDatasetNames.append(datasetConfigName)

    # --GRAB PRIMARY (EVOLUTION) DATASETS
    for evolutionDatasetName in evolutionDatasetNames:
        D = evaluation.gekko.dataset.selectCandlestickData(
            conf.Global.GekkoURLs[0],
            exchange_source=conf.dataset.__dict__[evolutionDatasetName],
            minDays=conf.backtest.deltaDays
        )
        evolutionDatasets.append(datasetOperations.CandlestickDataset(*D))
        try:
            evolutionDatasets[-1].restrain(conf.dataset.dataset_span)
        except Exception:
            print(
                'dataset_ span not configured for evolutionDatasetName. skipping...')

    # --GRAB SECONDARY (EVALUATION) DATASET
    try:
        Avoid = evolutionDatasets[0].specifications['asset']
        D = evaluation.gekko.dataset.selectCandlestickData(
            conf.Global.GekkoURLs[0],
            exchange_source=conf.dataset.eval_dataset_source,
            avoidCurrency=None,
            minDays=conf.backtest.deltaDays
        )
        if D is not None:
            evaluationDatasets = [datasetOperations.CandlestickDataset(*D)]
            evaluationDatasets[0].restrain(conf.dataset.eval_dataset_span)
        else:
            evaluationDatasets = []
    except RuntimeError:
        evaluationDatasets = []
        print("Evaluation dataset not found.")

    return evolutionDatasets, evaluationDatasets


def Generations(
        EvaluationModule,
        japonicusOptions,
        EvaluationMode,
        settings,
        options,
        web=None):

    # --LOAD SETTINGS;
    conf = makeSettings(settings)

    # --APPLY COMMAND LINE GENCONF SETTINGS;
    for parameter in conf.generation.__dict__.keys():
        if parameter in options.__dict__.keys():
            if options.__dict__[parameter] != None:
                conf.generation[parameter] = options.__dict__[parameter]

    GenerationMethod = promoterz.functions.selectRepresentationMethod(
        japonicusOptions["GenerationMethod"]
    )

    # --MANAGE Evaluation Modes;
    if EvaluationMode == 'indicator':
        # global StrategyFileManager
        StrategyFileManager = stratego.gekko_strategy.StrategyFileManager(
            conf.Global.gekkoPath, conf.indicator
        )
        Evaluate = partial(indicatorEvaluate, StrategyFileManager)
        Strategy = options.skeleton
    # --for standard methods;
    else:
        Strategy = EvaluationMode
        if options.benchmarkMode:
            Evaluate = benchmarkEvaluate
            evolutionDatasets, evaluationDatasets = [], []
            conf.gen.minimumProfitFilter = None
        else:
            Evaluate = standardEvaluate
            evolutionDatasets, evaluationDatasets = grabDatasets(
                conf
            )

    # -- PARSE TARGET PARAMETERS
    TargetParameters = promoterz.parameterOperations.flattenParameters(
        japonicusOptions["TargetParameters"])
    TargetParameters = promoterz.parameterOperations.parameterValuesToRangeOfValues(
        TargetParameters, conf.generation.parameter_spread
    )
    GlobalTools = GenerationMethod.getToolbox(Strategy,
                                              conf.generation,
                                              TargetParameters)
    RemoteHosts = evaluation.gekko.API.loadHostsFile(conf.Global.RemoteAWS)
    conf.Global.GekkoURLs += RemoteHosts
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
    configInfo = json.dumps(conf.generation.__dict__, indent=4)
    Logger.log(configInfo, target="Header", show=False)

    # --SHOW DATASET INFO;
    EvaluationModule.showPrimaryInfo(Logger,
                                     evolutionDatasets,
                                     evaluationDatasets)

    # --INITIALIZE WORLD WITH CANDLESTICK DATASET INFO; HERE THE GA KICKS IN;
    GlobalTools.register('Evaluate', Evaluate,
                         GlobalTools.constructPhenotype, conf.backtest)
    GlobalTools.register("ApplyResult", EvaluationModule.ResultToIndividue)
    GlobalTools.register("showIndividue", EvaluationModule.showIndividue)

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

    # Select run loops;
    populationLoops = [promoterz.sequence.locale.standard_loop.execute]
    worldLoops = [promoterz.sequence.world.parallel_world.execute]

    # Initalize World;
    World = promoterz.world.World(
        GlobalTools=GlobalTools,
        populationLoops=populationLoops,
        worldLoops=worldLoops,
        conf=conf,
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

    World.EvaluationModule = EvaluationModule
    World.seedEnvironment()

    World.logger.updateFile()

    # INITALIZE EVALUATION PROCESSING POOL
    World.parallel = World.EvaluationModule.EvaluationPool(
        World,
        conf.Global.GekkoURLs,
        conf.backtest.ParallelBacktests,
        conf.generation.showIndividualEvaluationInfo,
        )

    # --GENERATE INITIAL LOCALES;
    for l in range(conf.generation.NBLOCALE):
        World.generateLocale()

    # --RUN EPOCHES;
    while World.EPOCH < World.conf.generation.NBEPOCH:
        World.runEpoch()
        if conf.evalbreak.evaluateSettingsPeriodically and not options.benchmarkMode:
            if not World.EPOCH % conf.evalbreak.evaluateSettingsPeriodically:
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
