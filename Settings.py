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
            'gekkoPath': HOME+'/Gekko',
            'configFilename': 'example-config.js',
            'save_dir': "output",
            'log_name': 'evolution_gen.csv',
            'RemoteAWS': '../AmazonSetup/hosts', # Hosts list of remote machines running gekko, to distribute evaluation load; BETA.
                                                # option values: path to HOSTS file list OR False;
            'GekkoURLs': [ 'http://localhost:3000' ]
        },
        # genetic algorithm settings
        'generations': {
            'gekkoDebug': True,
            'showIndividualEvaluationInfo': False, # Verbose single evaluation results;
            'POP_SIZE': 30, # Initial population size, per locale 
            'NBEPOCH': 400, # number of epochs to run
            'evaluateSettingsPeriodically': 20, # show current best settings on every X epochs. (or False)
            'deltaDays': 60, # time window size on days of candlesticks for each evaluation
            'NBCandlestickData': 4, # Number of candlestick data loaded simultaneously in each locale; slower EPOCHS, theoretical better evolution;
            # -- Genetic Algorithm Parameters
            'cxpb': 0.3, # Probabilty of crossover 
            'mutpb': 0.7,# Probability of mutation;
            '_lambda': 7,# size of offspring generated per epoch;

            'PRoFIGA_beta': 0.005, # weight of PRoFIGA calculations on variability of population size
            'ageBoundaries': (9, 19), # minimum age to die, age when everyone dies (on EPOCHS)

            'candleSize': 15, # candle size for gekko backtest, in minutes

            'proofSize': 12,

            'DRP': 70,# Date range persistence; Number of subsequent rounds
             # until another time range in dataset is selected;
            'ParallelBacktests': 5,

            # -- Gekko Dataset Settings
            # leave the ! on the ignored entry as convenient;
            'dataset_source': None,
             # dataset_source can be set to None so it searches from any source;
            '!dataset_source': { # in case of specifying exchange-currency-asset, rename this removing the '!', and del the original key above.
                "exchange": "kraken",
                "currency": 'USD',
                "asset": 'LTC'
            },
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
                'sharpe': 0.1}
        },

        # bayesian optimization settings
        'bayesian': {
            'gekkoDebug': False,
            'deltaDays': 21,
            'testDays': 21,
            'num_rounds': 10,
            'random_state': 2017,
            'num_iter': 50,
            'init_points': 9,
            'parallel': False,
            'Strategy': 'PPO',
            'show_chart': False,
            'save': True,
            'candleSize': 30,
            'historySize': 10,
            'watch':{
                "exchange": "poloniex",
                "currency": 'USDT',
                "asset": 'BTC'
            }
        },
        'strategies': cS,
        'indicators': cI
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
