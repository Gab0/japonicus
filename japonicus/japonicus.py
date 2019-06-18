#!/bin/python

from . import halt, Settings, interface

from time import sleep
import random
from threading import Thread

from .evolution_generations import Generations


import datetime
import os

import waitress

import promoterz
from version import VERSION


def launchWebEvolutionaryInfo():
    print("WEBSERVER MODE")
    webpageTitle = "japonicus evolutionary statistics - v%.2f" % VERSION
    webServer = promoterz.webServer.core.build_server(webpageTitle)

    webServerProcess = Thread(
        target=waitress.serve,
        kwargs={
            "app": webServer,
            "listen": "0.0.0.0:8182"
        }
    )

    webServerProcess.start()
    return webServer


def buildSettingsOptions(optionparser, settingSubsets):
    settings = Settings.getSettings(SettingsFiles=settingSubsets)

    # PARSE GENCONF & DATASET COMMANDLINE ARGUMENTS;
    for settingSubset in settingSubsets:
        parser = promoterz.metaPromoterz.generateCommandLineArguments(
            optionparser,
            settings[settingSubset])

    options, args = parser.parse_args()
    for settingSubset in settingSubsets:
        settings[settingSubset] =\
            promoterz.metaPromoterz.applyCommandLineOptionsToSettings(
            options,
            settings[settingSubset]
        )

    return settings, options


def loadEvaluationModule():

    req = [
        "validateSettings",
        "showStatistics"
    ]
    pass


class JaponicusSession():

    def __init__(self, EvaluationModule, settings, options):

        # ADDITIONAL MODES;
        self.web_server = launchWebEvolutionaryInfo()\
            if options.spawn_web else None
        sleep(1)
        markzero_time = datetime.datetime.now()

        print()

        # show title;
        interface.showTitleDisclaimer(settings['backtest'], VERSION)

        if not EvaluationModule.validateSettings(settings):
            exit(1)

        # --SELECT STRATEGY;
        if options.random_strategy:
            Strategy = ""
            GekkoStrategyFolder = os.listdir(settings['Global']['gekkoPath'] + '/strategies')
            while Strategy + '.js' not in GekkoStrategyFolder:
                if Strategy:
                    print(
                        "Strategy %s descripted on settings but not found on strat folder." %
                        Strategy
                    )
                Strategy = random.choice(list(settings['strategies'].keys()))
                print("> %s" % Strategy)
        elif options.strategy:
            Strategy = options.strategy
        elif not options.skeleton:
            print("No strategy specified! Use --strat or go --help")
            exit(1)

        # --LAUNCH GENETIC ALGORITHM;
        if options.genetic_algorithm:

            japonicusOptions = {
                "GenerationMethod": None,
                "TargetParameters": None
            }

            japonicusOptions["GenerationMethod"] =\
                'chromosome' if options.chromosome_mode else 'oldschool'

            if options.skeleton:
                EvaluationMode = 'indicator'
                AllIndicators = Settings.getSettings()['indicators']
                TargetParameters = Settings.getSettings()['skeletons'][options.skeleton]
                for K in AllIndicators.keys():
                    if type(AllIndicators[K]) != dict:
                        TargetParameters[K] = AllIndicators[K]
                    elif AllIndicators[K]['active']:
                        TargetParameters[K] = AllIndicators[K]
                        TargetParameters[K]['active'] = (0, 1)

                japonicusOptions["TargetParameters"] = TargetParameters

                if not TargetParameters:
                    print("Bad configIndicators!")
                    exit(1)
            else:
                EvaluationMode = Strategy
                # READ STRATEGY PARAMETER RANGES FROM TOML;
                try:
                    TOMLData = promoterz.TOMLutils.preprocessTOMLFile(
                        "strategy_parameters/%s.toml" % Strategy
                    )
                except FileNotFoundError:
                    print("Failure to find strategy parameter rules for " +
                          "%s at ./strategy_parameters" % Strategy)
                    gekkoParameterPath = "%s/config/strategies/%s.toml" %\
                                         (settings['Global']['gekkoPath'], Strategy)
                    print("Trying to locate strategy parameters at %s" %
                          gekkoParameterPath)

                    TOMLData = promoterz.TOMLutils.preprocessTOMLFile(
                        gekkoParameterPath)

                japonicusOptions["TargetParameters"] =\
                    promoterz.TOMLutils.TOMLToParameters(TOMLData)

            # RUN ONE EQUAL INSTANCE PER REPEATER NUMBER SETTINGS,
            # SEQUENTIALLY...
            for s in range(options.repeater):
                Generations(
                    EvaluationModule,
                    japonicusOptions,
                    EvaluationMode,
                    settings,
                    options,
                    web=self.web_server
                )

        deltatime = datetime.datetime.now() - markzero_time
        print("Run took %i seconds." % deltatime.seconds)
        if options.spawn_web:
            print('Statistics info server still runs...')


