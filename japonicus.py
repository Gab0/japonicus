#!/bin/python
import sys

if not sys.version_info.major >= 3 or not sys.version_info.minor >= 6:
    exit('check your python version before running japonicus. Python>=3.6 is required.')
import signal

signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

from time import sleep
from random import choice, randrange
from subprocess import Popen, PIPE
from threading import Thread
from Settings import getSettings
from evolution_generations import gekko_generations

import TOMLutils

import datetime
from os import chdir, path, listdir

chdir(path.dirname(path.realpath(__file__)))

from japonicus_options import options, args
import web
import promoterz
from version import VERSION

settings = getSettings()


# from evolution_bayes import gekko_bayesian
def showTitleDisclaimer():
    TITLE = """\tGEKKO
        ██╗ █████╗ ██████╗  ██████╗ ███╗   ██╗██╗ ██████╗██╗   ██╗███████╗
        ██║██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██║██╔════╝██║   ██║██╔════╝
        ██║███████║██████╔╝██║   ██║██╔██╗ ██║██║██║     ██║   ██║███████╗
   ██   ██║██╔══██║██╔═══╝ ██║   ██║██║╚██╗██║██║██║     ██║   ██║╚════██║
   ╚█████╔╝██║  ██║██║     ╚██████╔╝██║ ╚████║██║╚██████╗╚██████╔╝███████║
    ╚════╝ ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═════╝ ╚══════╝"""
    try:
        print(TITLE)
    except UnicodeEncodeError:
        print("\nJAPONICUS\n")
    print('\t' * 8 + 'v%.2f' % VERSION)
    print()
    print(
        "The profits reported here are the profit beyond market price change;\n" +
        "\ti.e. shown profit =  <backtest profit> - <market profit in evaluated candlestick period>;"
    )


def launchGekkoChildProcess():
    gekko_args = [
        'node',
        '--max-old-space-size=8192',
        settings['Global']['gekkoPath'] + '/web/server.js',
    ]
    gekko_server = Popen(gekko_args, stdin=PIPE, stdout=PIPE)
    return gekko_server


def launchWebEvolutionaryInfo():
    # web_args = ['python', 'web.py']
    #web_server = Popen(web_args, stdin=PIPE, stdout=PIPE)
    print("WEBSERVER MODE")
    webServer = web.run_server()
    webServerProcess = Thread(
        target=webServer.server.run, kwargs={'debug': False, 'host': '0.0.0.0'}
    )
    webServerProcess.start()
    return webServer


def launchJaponicus():
    if not options.genetic_algorithm or options.bayesian_optimization:
        exit("Aborted: No operation specified.")
    gekko_server = launchGekkoChildProcess() if options.spawn_gekko else None
    web_server = launchWebEvolutionaryInfo() if options.spawn_web else None
    sleep(1)
    markzero_time = datetime.datetime.now()
    showTitleDisclaimer()
    # --SELECT STRATEGY;
    if options.random_strategy:
        Strategy = ""
        GekkoStrategyFolder = listdir(settings['Global']['gekkoPath'] + '/strategies')
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
        exit("No strategy specified! Use --strat or go --help")
    # --LAUNCH GENETIC ALGORITHM;
    if options.genetic_algorithm:
        GenerationMethod = 'chromosome' if options.chromosome_mode else 'oldschool'
        if options.skeleton:
            EvaluationMode = 'indicator'
            AllIndicators = getSettings()['indicators']
            TargetParameters = getSettings()['skeletons'][options.skeleton]
            for K in AllIndicators.keys():
                if type(AllIndicators[K]) != dict:
                    TargetParameters[K] = AllIndicators[K]
                elif AllIndicators[K]['active']:
                    TargetParameters[K] = AllIndicators[K]
                    TargetParameters[K]['active'] = (0, 1)
            if not TargetParameters:
                exit("Bad configIndicators!")
        else:
            EvaluationMode = Strategy
            try:
                TargetParameters = getSettings()['strategies'][Strategy]
            # -- Yeah, nested exceptions;
            except KeyError:
                try:
                    TOMLData = TOMLutils.preprocessTOMLFile(
                        "strategy_parameters/%s.toml" % Strategy
                    )
                except FileNotFoundError:
                    TOMLData = TOMLutils.preprocessTOMLFile(
                        "%s/config/strategis/%s.toml" % (GekkoDir, Strategy)
                    )
                TargetParameters = TOMLutils.TOMLToParameters(TOMLData)
        for s in range(options.repeater):
            gekko_generations(
                TargetParameters, GenerationMethod, EvaluationMode, web=web_server
            )
    # --LAUNCH BAYESIAN OPTIMIZATION;
    elif options.bayesian_optimization:
        import evolution_bayes

        for s in range(options.repeater):
            evolution_bayes.gekko_bayesian(Strategy)
    deltatime = datetime.datetime.now() - markzero_time
    print("Run took %i seconds." % deltatime.seconds)
    if options.spawn_web:
        print('Statistics info server still runs...')


if __name__ == "__main__":
    launchJaponicus()
