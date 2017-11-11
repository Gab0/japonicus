import os
import js2py

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
    s = {
        'Global': {
            'gekkoPath': os.getenv("HOME")+'/gekko1',
            'configFilename': 'example-config.js',
            'save_dir': "output",
            'log_name': 'evolution_gen.csv',
            'RemoteAWS': '../AmazonSetup/hosts', # Hosts list of remote machines running gekko, to distribute evaluation load; BETA.
                                                # option values: path to HOSTS file list OR False;
            'GekkoURLs': ['http://localhost:3000']
        },
        # genetic algorithm settings
        'generations': { 
            'POP_SIZE': 30, # Initial population size, per locale 
            'NBEPOCH': 500, # number of epochs to run
            'deltaDays': 21, # time window size on days of candlesticks for each evaluation
            'cxpb': 0.2, # Probabilty of crossover 
            'mutpb': 0.8,# Probability of mutation;
            '_lambda': 5,# size of offspring generated per epoch;
            'Strategy': "UO", # Gekko strategy of choice;
            'DRP': 70,# Date range persistence; Number of subsequent rounds
             # until another time range in dataset is selected;
            'ParallelBacktests': 5,
            'PRoFIGA_beta': 0.005, # weight of PRoFIGA calculations on variability of population size
            'ageBoundaries': (9, 19), # minimum age to die, age where everyone dies (on EPOCHS)
            'candleSize': 30, # candle size for gekko backtest, in minutes
            'dataset_source': { # dataset_source can be set to None so it searches from any source;
                "exchange": "poloniex",
                "currency": 'USDT',
                "asset": 'BTC'
            },
            'finaltest': {
                'NBBESTINDS': 1,
                'NBADDITIONALINDS': 4,
            },
            'chromosome': {
                'GeneSize': 2,
                'Density': 3,
            }
        },
        # bayesian optimization settings
        'bayesian': {
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
        'strategies': {
            # Define range of values for strat settings;
            #for all evolution methods;
            "PPOTSI":{
            "PPO.short": (3,12),
            "PPO.long": (15,35),
            "PPO.signal":(3,18),
            "PPO.up": (0., 0.5),
            "PPO.down": (-0.5, 0.),
            "TSI.up": (15,35),
            "TSI.down": (-35,-15),
            "TSI.short": (3,12),
            "TSI.long": (15,35),
            "persistence": (1,5)
                    },
                
            "DEMA":{
                #"candleSize":(1,60), # tick per day
                #"historySize":(1,60),
                "short": (1,10), # short EMA
                "long": (20,50), # long EMA
                "thresholds.down": (-0.5,0.1), # trend thresholds
                "thresholds.up": (-0.1,0.5), # trend thresholds
            },
            "MACD":{
                #"candleSize":(1,60), # tick per day
                #"historySize":(1,60), # required history
                "short": (1,10), # short EMA
                "long": (20,50), # long EMA
                "signal": (9,18), # shortEMA - longEMA diff
                "thresholds.down": (-0.5,0.), # trend thresholds
                "thresholds.up": (0.,0.5), # trend thresholds
                "thresholds.persistence": (2,10), # trend duration(count up by tick) thresholds
            },
            "PPO":{
                #"candleSize":(1,60), # tick per day
                #"historySize":(1,60), # required history
                "short": (6,18), # short EMA
                "long": (13,39), # long EMA
                "signal": (1,18), # 100 * (shortEMA - longEMA / longEMA)
                "thresholds.down": (-0.5,0.), # trend thresholds
                "thresholds.up": (0.,0.5), # trend thresholds
                "thresholds.persistence": (2,10), # trend duration(count up by tick) thresholds
            },
            # Uses one of the momentum indicators but adjusts the thresholds when PPO is bullish or bearish
            # Uses settings from the ppo and momentum indicator config block
            "varPPO":{ # TODO: merge PPO config
                #"candleSize":(1,60), # tick per day
                #"historySize":(1,60), # required history
                    "short": (6,18), # short EMA
                "long": (13,39), # long EMA
                "signal": (1,18), # 100 * (shortEMA - longEMA / longEMA)
                "thresholds.down": (-0.5,0.), # trend thresholds
                "thresholds.up": (0.,0.5), # trend thresholds
                "thresholds.persistence": (0,4), # trend duration(count up by tick) thresholds
                "momentum": (0, 2.99999), # index of ["RSI", "TSI", "UO"]
                           # new threshold is default threshold + PPOhist * PPOweight
                "weightLow": (60, 180),
                "weightHigh": (-180, -60),
                    },
                    "RSI":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60), # required history
                           "interval": (7,21), # weight
                           "thresholds.low": (15,45), # trend thresholds
                           "thresholds.high": (45,140), # trend thresholds
                           "thresholds.persistence": (4,10), # trend duration(count up by tick) thresholds
                    },
                    "StochRSI":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60), # required history
                           "interval": (7,21), # weight
                           "thresholds.low": (15,45), # trend thresholds
                           "thresholds.high": (45,140), # trend thresholds
                           "thresholds.persistence": (4,10), # trend duration(count up by tick) thresholds
                    },
                    "CCI":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60), # required history
                           "consistant": (7,21), # constant multiplier. 0.015 gets to around 70% fit
                           "history": (45,135), # history size, make same or smaller than history
                           "thresholds.down": (-150,-50), # trend thresholds
                           "thresholds.up": (50,150), # trend thresholds
                           "thresholds.persistence": (4,10), # trend duration(count up by tick) thresholds
                    },
                    "UO":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60), # required history
                           "first.weight": (2,8), # 
                           "first.period": (4.5,14), # 
                           "second.weight": (1,4), # 
                           "second.period": (7,28), # 
                           "third.weight": (0.5,2), # 
                           "third.period": (14,56), # 
                           "thresholds.low": (15,45), # trend thresholds
                           "thresholds.high": (45,140), # trend thresholds
                           "thresholds.persistence": (0,4), # trend duration(count up by tick) thresholds
                     },
            "MRBB": {
                "short": (3, 12),
                "long": (12, 32),
                "signal": (6, 23),
                "interval": (7, 23),
                "crosspersistence": (7, 30),
                "macdhigh": (0.1,0.6),
                "macdlow": (-0.6,-0.1),
                "rsihigh": (30,100),
                "rsilow": (1,35),
                "bbands.TimePeriod": (16,22),
                "bbands.NbDevUp": (1,3),
                "bbands.NbDevDn": (1,3),
                "bbands.MAType": (1,3)

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
