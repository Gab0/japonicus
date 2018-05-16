#!/bin/python
import json
import random
import datetime
import sys

import promoterz
import evaluation

from copy import deepcopy

import resultInterface
import interface

import promoterz.sequence.standard_loop

from deap import tools
from deap import algorithms
from deap import base

from Settings import getSettings, makeSettings
import stratego
from functools import partial

from evaluation.gekko.datasetOperations import *


StrategyFileManager = None


# TEMPORARY ASSIGNMENT OF EVAL FUNCTIONS; SO THINGS REMAIN SANE (¿SANE?);
def aEvaluate(
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


def bEvaluate(constructPhenotype, genconf, Datasets, Individual, gekkoUrl):
    phenotype = constructPhenotype(Individual)
    phenotype = {Individual.Strategy: phenotype}
    SCORE = evaluation.gekko.backtest.Evaluate(
        genconf, Datasets, phenotype, gekkoUrl
    )
    return SCORE


def gekko_generations(
        TargetParameters, GenerationMethod, EvaluationMode, settings,
        options, web=None):
    # --LOAD SETTINGS;
    genconf = makeSettings(settings['generations'])
    globalconf = makeSettings(settings['Global'])
    datasetconf = makeSettings(settings['dataset'])
    indicatorconf = makeSettings(settings['indicators'])
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
        Evaluate = partial(aEvaluate, StrategyFileManager)
        Strategy = options.skeleton
    # --for standard methods;
    else:
        Evaluate = bEvaluate
        Strategy = EvaluationMode
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
    # CHECK HOW MANY EVOLUTION DATASETS ARE SPECIFIED AT SETTINGS;
    evolutionDatasetNames = ['dataset_source']
    evolutionDatasets = []
    for DS in range(1, 100):
        datasetConfigName = 'dataset_source%i' % DS
        if datasetConfigName in datasetconf.__dict__.keys():
            evolutionDatasetNames.append(datasetConfigName)
    # --GRAB PRIMARY (EVOLUTION) DATASETS
    for evolutionDatasetName in evolutionDatasetNames:
        D = evaluation.gekko.dataset.selectCandlestickData(
            exchange_source=datasetconf.__dict__[evolutionDatasetName]
        )
        evolutionDatasets.append(CandlestickDataset(*D))
        try:
            evolutionDatasets[-1].restrain(datasetconf.dataset_span)
        except:
            print('dataset_ span not configured for evolutionDatasetName. skipping...')

    # --GRAB SECONDARY (EVALUATION) DATASET
    try:
        D = evaluation.gekko.dataset.selectCandlestickData(
            exchange_source=datasetconf.eval_dataset_source,
            avoidCurrency=evolutionDatasets[0].specifications['asset'],
        )
        evaluationDatasets = [CandlestickDataset(*D)]
        evaluationDatasets[0].restrain(datasetconf.eval_dataset_span)
    except RuntimeError:
        evaluationDatasets = []
        print("Evaluation dataset not found.")
    # --INITIALIZE LOGGER;
    ds_specs = evolutionDatasets[0].specifications
    logfilename = "%s-%s-%s-%s-%s" % (
        Strategy,
        ds_specs['exchange'],
        ds_specs['currency'],
        ds_specs['asset'],
        str(datetime.datetime.now())[-6:],
    )
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
                         GlobalTools.constructPhenotype, genconf)

    # --THIS LOADS A DATERANGE FOR A LOCALE;
    def onInitLocale(World, locale):
        locale.Dataset = getLocaleDataset(World, locale)


    loops = [promoterz.sequence.standard_loop.standard_loop]
    World = promoterz.world.World(
        GlobalTools,
        loops,
        genconf,
        globalconf,
        TargetParameters,
        EnvironmentParameters={'evolution':  evolutionDatasets,
                               'evaluation': evaluationDatasets},
        onInitLocale=onInitLocale,
        web=web,
    )
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
