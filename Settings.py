import os
def getSettings():
    s = {'global':{
        'gekkoPath': os.getenv("HOME")+'/gekko1'
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
         
        'bayesian': {'deltaDays': 3,
                     'testDays': 3,
                     'num_rounds': 10,
                     'random_state': 2017,
                     'num_iter': 45,
                     'init_points':9,
                     'parallel': False,
                     'Strategy': 'MACD',
                     'configFilename': 'example-config.js'
        }
    }
    
    return s
