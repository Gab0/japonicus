#!/bin/python

NEG = lambda v: (-v[1], -v[0])
cS = {
    # Define range of values for strat settings;
    #for all evolution methods;
    "PPOTSI":{
        "PPO.short": (3,16),
        "PPO.long": (12,35),
        "PPO.signal":(3,21),
        "PPO.up": (0., 1),
        "PPO.down": (-1, 0.),
        "TSI.up": (10,40),
        "TSI.down": (-40,-10),
        "TSI.short": (3,18),
        "TSI.long": (10,42),
        "persistence": (1,10)
    },
    "PPOLRC":{
        "PPO.short": (3,12),
        "PPO.long": (15,35),
        "PPO.signal":(3,18),
        "PPO.up": (0., 0.5),
        "PPO.down": (-0.5, 0.),
        "LRC.up": (15,35),
        "LRC.down": (-35,-15),
        "LRC.depth": (3,18),
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
