#!/bin/python
import os
import js2py
from pathlib import Path

from configStrategies import cS
from configIndicators import cI


class _settings:

    def __init__(self, **entries):
        '''
        print(entries)
        def iterate(self, DATA):
            for W in DATA.keys():
                if type(DATA[W]) == dict:
                    iterate(self,DATA[W])
                else:
                    self.__dict__.update(DATA)
        iterate(self,entries)
        '''
        self.__dict__.update(entries)

    def getstrat(self, name):
        return self.strategies[name]


def getSettings(specific=None):
    HOME = str(Path.home())
    s = {
        'Global': {'gekkoPath': HOME + '/gekko', 'configFilename': 'example-config.js', 'save_dir': "output", 'log_name': 'evolution_gen.csv', 'RemoteAWS': '../AmazonSetup/hosts', 'GekkoURLs': ['http://localhost:3000'], 'showFailedStrategies': False},
        # Hosts list of remote machines running gekko, to distribute evaluation load;
        # option values: path to HOSTS file list OR False;
        # Your gekko local URL - CHECK THIS!
        # genetic algorithm settings
        'generations': {'gekkoDebug': True, 'showIndividualEvaluationInfo': False, 'parameter_spread': 60, 'POP_SIZE': 30, 'NBEPOCH': 800, 'evaluateSettingsPeriodically': 20, 'deltaDays': 90, 'ParallelCandlestickDataset': 1, 'cxpb': 0.8, 'mutpb': 0.2, '_lambda': 7, 'PRoFIGA_beta': 0.005, 'ageBoundaries': (9, 19), 'candleSize': 10, 'proofSize': 12, 'DRP': 70, 'ParallelBacktests': 6, 'finaltest': {'NBBESTINDS': 1, 'NBADDITIONALINDS': 4}, 'chromosome': {'GeneSize': 2, 'Density': 3}, 'weights': {'profit': 1.0, 'sharpe': 0.1}, 'interpreteBacktestProfit': 'v3'},
        # show gekko verbose (strat info) - gekko must start with -d flag;
        # Verbose single evaluation results;
        # if parameter is set to value rather than tuple limits at settings, make the value
        # a tuple based on chosen spread value (percents); value: 10 --spread=50-->  value: (5,15)
        # Initial population size, per locale
        # number of epochs to run
        # show current best settings on every X epochs. (or False)
        # time window size on days of candlesticks for each evaluation
        # Number of candlestick data loaded simultaneously in each locale;
        # slower EPOCHS, theoretical better evolution;
        # seems broken. values other than 1 makes evolution worse.
        # -- Genetic Algorithm Parameters  # Probabilty of crossover  # Probability of mutation;  # size of offspring generated per epoch;  # weight of PRoFIGA calculations on variability of population size  # minimum age to die, age when everyone dies (on EPOCHS)  # candle size for gekko backtest, in minutes
        # Date range persistence; Number of subsequent rounds
        # until another time range in dataset is selected;
        # mode of profit interpretation: v1, v2 or v3.
        # please check the first functions at evaluation.gekko.backtest
        # to understand what is this. has big impact on evolutionary agenda.
        # bayesian optimization settings
        'bayesian': {'gekkoDebug': False, 'deltaDays': 60, 'num_rounds': 10, 'random_state': 2017, 'num_iter': 50, 'init_points': 9, 'parallel': False, 'show_chart': False, 'save': True, 'parameter_spread': 100, 'candleSize': 30, 'historySize': 10, 'watch': {"exchange": "poloniex", "currency": 'USDT', "asset": 'BTC'}, 'interpreteBacktestProfit': 'v3'},
        # show gekko verbose (strat info) - gekko must start with -d flag;
        # time window size on days of candlesticks for each evaluation
        # number of evaluation rounds
        # seed for randomziation of values
        # number of iterations on each round
        # number of random values to start bayes evaluation
        # candleSize & historySize on Gekko, for all evals
        'dataset': {'dataset_source': None, '!dataset_source': {"exchange": "kraken", "currency": 'USD', "asset": 'LTC'}, 'eval_dataset_source': None, 'dataset_span': 0, 'eval_dataset_span': 0},
        # -- Gekko Dataset Settings
        # leave the ! on the ignored entry as convenient;
        # dataset_source can be set to None so it searches from any source;  # in case of specifying exchange-currency-asset, rename this removing the '!', and del the original key above.
        # span in days from the end of dataset to the beggining. Or zero.
        # (to restrain length);
        'strategies': cS,
        'indicators': cI,
        'skeletons': {'ontrend': {"SMA_long": 1000, "SMA_short": 50}},
    }
    if specific != None:
        if not specific:
            return _settings(**s)

        else:
            return _settings(** s[specific])

    return s


def get_configjs(filename="example-config.js"):
    with open(filename, "r") as f:
        text = f.read()
    text = text.replace("module.exports = config;", "config;")
    return js2py.eval_js(text).to_dict()
