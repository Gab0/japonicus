import os
import js2py

def getSettings():
    s = {'global':{
        'gekkoPath': os.getenv("HOME")+'/gekko1',
        'Strategies': ['DEMA', 'MACD', 'PPO', 'RSI', 'StochRSI', 'TSI']
        },
         
        'generations': {
            'deltaDays': 21,
            'cxpb': 0.2,
            'mutpb': 0.8,
            '_lambda': 5,
            'Strategy': "StochRSI",
            'DRP': 10,
            'ParallelBacktests': 5
        },
        'bayesian': {'deltaDays': 21,
                    'testDays': 21,
                    'num_rounds': 10,
                    'random_state': 2017,
                    'num_iter': 50,
                    'init_points': 9,
                    'parallel': False,
                    'Strategy': 'PPO',
                    'configFilename': 'example-config.js',
                    'show_chart': True,
                    'save': True,
                    'save_dir': "output",
                    'watch':{
                            "exchange": "poloniex",
                            "currency": 'USDT',
                            "asset": 'BTC'
                    },
                    "DEMA":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60),
                           "short": (1,10), # short EMA
                           "long": (20,50), # long EMA
                           "thresholds.down": (-0.5,0.), # trend thresholds
                           "thresholds.up": (0.,0.5), # trend thresholds
                    },
                    "MACD":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60), # required history
                           "short": (1,10), # short EMA
                           "long": (20,50), # long EMA
                           "signal": (1,18), # shortEMA - longEMA diff
                           "thresholds.down": (-0.5,0.), # trend thresholds
                           "thresholds.up": (0.,0.5), # trend thresholds
                           "thresholds.persistence": (0,2), # trend duration(count up by tick) thresholds
                    },
                    "PPO":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60), # required history
                           "short": (6,18), # short EMA
                           "long": (13,39), # long EMA
                           "signal": (1,18), # 100 * (shortEMA - longEMA / longEMA)
                           "thresholds.down": (-0.5,0.), # trend thresholds
                           "thresholds.up": (0.,0.5), # trend thresholds
                           "thresholds.persistence": (0,4), # trend duration(count up by tick) thresholds
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
                           "weightHigh": (-60, -180),
                    },
                    "RSI":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60), # required history
                           "interval": (7,21), # weight
                           "thresholds.low": (15,45), # trend thresholds
                           "thresholds.hith": (45.,140), # trend thresholds
                           "thresholds.persistence": (0,4), # trend duration(count up by tick) thresholds
                    },
                    "StochRSI":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60), # required history
                           "interval": (7,21), # weight
                           "thresholds.low": (15,45), # trend thresholds
                           "thresholds.hith": (45,140), # trend thresholds
                           "thresholds.persistence": (0,4), # trend duration(count up by tick) thresholds
                    },
                    "CCI":{
                           #"candleSize":(1,60), # tick per day
                           #"historySize":(1,60), # required history
                           "consistant": (7,21), # constant multiplier. 0.015 gets to around 70% fit
                           "history": (45,135), # history size, make same or smaller than history
                           "thresholds.down": (-50,-150), # trend thresholds
                           "thresholds.up": (50,150), # trend thresholds
                           "thresholds.persistence": (0,4), # trend duration(count up by tick) thresholds
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
        }
    }
    
    return s

def get_configjs(filename="example-config.js"):
    with open(filename, "r") as f:
        text = f.read()
    text = text.replace("module.exports = config;","config;")
    return js2py.eval_js(text).to_dict()
