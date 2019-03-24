#!/bin/python

from . import halt, Settings, interface

from time import sleep
from random import choice, randrange
from subprocess import Popen, PIPE
from threading import Thread
from .evolution_generations import gekko_generations

import datetime
import os


import promoterz
from version import VERSION
import evaluation


def launchGekkoChildProcess(settings):
    gekko_args = [
        'node',
        '--max-old-space-size=8192',
        settings['global']['gekkoPath'] + '/web/server.js',
    ]
    gekko_server = Popen(gekko_args, stdin=PIPE, stdout=PIPE)
    return gekko_server


def launchWebEvolutionaryInfo():
    print("WEBSERVER MODE")
    webpageTitle = "japonicus evolutionary statistics - v%.2f" % VERSION
    webServer = promoterz.webServer.core.run_server(webpageTitle)
    webServerProcess = Thread(
        target=webServer.server.run,
        kwargs={
            'debug': False,
            'host': '0.0.0.0'
        }
    )
    webServerProcess.start()
    return webServer


def buildJaponicusOptions(optionparser):
    settings = Settings.getSettings()

    # PARSE GENCONF & DATASET COMMANDLINE ARGUMENTS;
    settingSubsets = ['generations', 'dataset', 'backtest', 'evalbreak']
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


class JaponicusSession():

    def filterIllegalOptions(self, settings, options):
        # ABORT WHEN ILLEGAL OPTIONS ARE SET;
        if not options.genetic_algorithm and not options.bayesian_optimization:
            print("Aborted: No operation specified.")
            exit(1)

        if not os.path.isfile(settings['global']['gekkoPath'] + '/gekko.js'):
            print("Aborted: gekko.js not found on path specified @Settings.py;")
            exit(1)

        # -- BAYESIAN IS DEPRECATED;
        elif options.bayesian_optimization:
            print("Bayesian method is deprecated.")
            exit(1)

    def __init__(self, settings, options):
        self.filterIllegalOptions(settings, options)

        # ADDITIONAL MODES;
        self.gekko_server = launchGekkoChildProcess(settings)\
            if options.spawn_gekko else None
        self.web_server = launchWebEvolutionaryInfo()\
            if options.spawn_web else None
        sleep(1)
        markzero_time = datetime.datetime.now()

        print()

        # show title;
        interface.showTitleDisclaimer(settings['backtest'], VERSION)
        # LOCATE & VALIDATE RUNNING GEKKO INSTANCES FROM CONFIG URLs;
        possibleInstances = settings['global']['GekkoURLs']
        validatedInstances = []
        for instance in possibleInstances:
            Response = evaluation.gekko.API.checkInstance(instance)
            if Response:
                validatedInstances.append(instance)
                print("found gekko @ %s" % instance)
            else:
                print("unable to locate %s" % instance)

        if validatedInstances:
            settings['global']['GekkoURLs'] = validatedInstances
        else:
            print("Aborted: No running gekko instances found.")
            exit(1)

        # --SELECT STRATEGY;
        if options.random_strategy:
            Strategy = ""
            GekkoStrategyFolder = os.listdir(settings['global']['gekkoPath'] + '/strategies')
            while Strategy + '.js' not in GekkoStrategyFolder:
                if Strategy:
                    print(
                        "Strategy %s descripted on settings but not found on strat folder." %
                        Strategy
                    )
                Strategy = choice(list(settings['strategies'].keys()))
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
                                         (settings['global']['gekkoPath'], Strategy)
                    print("Trying to locate gekko parameters at %s" %
                          gekkoParameterPath)
                    TOMLData = promoterz.TOMLutils.preprocessTOMLFile(gekkoParameterPath)

                japonicusOptions["TargetParameters"] =\
                    promoterz.TOMLutils.TOMLToParameters(TOMLData)

            # RUN ONE EQUAL INSTANCE PER REPEATER NUMBER SETTINGS, SEQUENTIALLY;
            for s in range(options.repeater):
                gekko_generations(
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


