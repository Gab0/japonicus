#!/bin/python
import os
import js2py
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
    HOME = os.getenv("HOME")
    s = {
        'Global': {
            'gekkoPath': HOME+'/gekko',
            'configFilename': 'example-config.js',
            'save_dir': "output",
            'log_name': 'evolution_gen.csv',

            # Hosts list of remote machines running gekko, to distribute evaluation load;
            # option values: path to HOSTS file list OR False;
            'RemoteAWS': '../AmazonSetup/hosts',

            # Your gekko local URL - CHECK THIS!
            'GekkoURLs': [ 'http://localhost:3000' ],
            'showFailedStrategies': False
        },
        # genetic algorithm settings
        'generations': {
            # show gekko verbose (strat info) - gekko must start with -d flag;
            'gekkoDebug': True,

            # Verbose single evaluation results;
            'showIndividualEvaluationInfo': False,

            # if parameter is set to value rather than tuple limits at settings, make the value
            # a tuple based on chosen spread value (percents); value: 10 --spread=50-->  value: (5,15)
            'parameter_spread' : 60,

            # Initial population size, per locale
            'POP_SIZE': 30, 

            # number of epochs to run
            'NBEPOCH': 800,

            # show current best settings on every X epochs. (or False)
            'evaluateSettingsPeriodically': 20,

            # time window size on days of candlesticks for each evaluation
            'deltaDays': 60,

            # Number of candlestick data loaded simultaneously in each locale;
            # slower EPOCHS, theoretical better evolution;
            # seems broken. values other than 1 makes evolution worse.
            'ParallelCandlestickDataset': 1,


            # -- Genetic Algorithm Parameters
            'cxpb': 0.6, # Probabilty of crossover 
            'mutpb': 0.2,# Probability of mutation;
            '_lambda': 7,# size of offspring generated per epoch;

            'PRoFIGA_beta': 0.005, # weight of PRoFIGA calculations on variability of population size
            'ageBoundaries': (9, 19), # minimum age to die, age when everyone dies (on EPOCHS)

            'candleSize': 10, # candle size for gekko backtest, in minutes

            'proofSize': 12,

            'DRP': 70,# Date range persistence; Number of subsequent rounds
             # until another time range in dataset is selected;
            'ParallelBacktests': 6,

            'finaltest': {
                'NBBESTINDS': 1,
                'NBADDITIONALINDS': 4,
            },
            'chromosome': {
                'GeneSize': 2,
                'Density': 3,
            },
            'weights': {
                'profit': 1.0,
                'sharpe': 0.1},

            # mode of profit interpretation: v1, v2 or v3.
            # please check the first functions at evaluation.gekko.backtest
            # to understand what is this. has big impact on evolutionary agenda.
            'interpreteBacktestProfit': 'v3'
        },

        # bayesian optimization settings
        'bayesian': {
            # show gekko verbose (strat info) - gekko must start with -d flag;
            'gekkoDebug': False,


            # time window size on days of candlesticks for each evaluation
            'deltaDays': 60,

            # number of evaluation rounds
            'num_rounds': 10,

            # seed for randomziation of values
            'random_state': 2017,

            # number of iterations on each round
            'num_iter': 50,

            # number of random values to start bayes evaluation
            'init_points': 9,

            'parallel': False,
            'show_chart': False,
            'save': True,
            
            'parameter_spread': 100,

            # candleSize & historySize on Gekko, for all evals
            'candleSize': 30,
            'historySize': 10,

            'watch':{
                "exchange": "poloniex",
                "currency": 'USDT',
                "asset": 'BTC'
            },
            
            'interpreteBacktestProfit': 'v3'

        },
        'dataset' : {
            # -- Gekko Dataset Settings
            # leave the ! on the ignored entry as convenient;
            'dataset_source': None,
             # dataset_source can be set to None so it searches from any source;
            '!dataset_source': { # in case of specifying exchange-currency-asset, rename this removing the '!', and del the original key above.
                "exchange": "kraken",
                "currency": 'USD',
                "asset": 'LTC',
            },
            'eval_dataset_source': None,

            # span in days from the end of dataset to the beggining. Or zero.
            # (to restrain length);
            'dataset_span': 0,
            'eval_dataset_span': 0

            },
        'strategies': cS,
        'indicators': cI,
        'skeletons': {
            'ontrend': {
                "SMA_long": 1000,
                "SMA_short": 50
            }
        }
    }

    if specific != None:
        if not specific:
            return _settings(**s)
        else:
            return _settings(**s[specific])

    return s

def get_configjs(filename="example-config.js"):
    with open(filename, "r") as f:
        text = f.read()
    text = text.replace("module.exports = config;","config;")
    return js2py.eval_js(text).to_dict()
