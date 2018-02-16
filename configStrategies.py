#!/bin/python

NEG = lambda v: (-v[1], -v[0])
cS = {
    # Define values for strat settings for strategies to be used
    # on japonicus;
    # Each value can be a tuple of limits or just a base value.
    
"RSI_BULL_BEAR" : {

# SMA Trends
"SMA_long": 1000,
"SMA_short": 50,

# BULL
"BULL_RSI": 10,
"BULL_RSI_high":  80,
"BULL_RSI_low" : 60,

# BEAR
"BEAR_RSI": 15,
"BEAR_RSI_high": 50,
"BEAR_RSI_low" : 20
},

"RSI_BULL_BEAR_ADX" : {

# SMA Trends
"SMA_long": 1000,
"SMA_short": 50,

# BULL
"BULL_RSI": 10,
"BULL_RSI_high":  80,
"BULL_RSI_low" : 60,

# BEAR
"BEAR_RSI": 15,
"BEAR_RSI_high": 50,
"BEAR_RSI_low" : 20,

# ADX
"ADX": 3,
"ADX_high": 70,
"ADX_low": 50
},

"Bestone" :{
    "customMACDSettings": {
        "optInFastPeriod": (3,10),
        "optInSlowPeriod": (20,50),
        "optInSignalPeriod": (5,15)
    },

    "customEMAshortSettings": {
        "optInTimePeriod": (5,15)
    },

    "customEMAlongSettings": {
        "optInTimePeriod": (15,26)
    },

    "customSTOCHSettings": {
        "optInFastKPeriod": (6, 14),
        "optInSlowKPeriod": (2,5),
        "optInSlowKMAType": (1,1),
        "optInSlowDPeriod": (2,5),
        "optInSlowDMAType": (1,1)
    },

    "customRSISettings": {
        "optInTimePeriod": (7,20)
    }

},

    
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
    "Supertrend": {
        "atrEma":(1,10),
        "bandFactor": (1,10)
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
    "buyatsellat": {
        'buyat': (1.03,1.20),
	'sellat': (0.92, 0.97), 
	'stop_loss_pct': (0.87, 0.95), 
	'sellat_up': (1.01,1.20)
    },
    "buyatsellatPPO": {
        'buyat': (1.03,1.20),
        'sellat': (0.92, 0.97), 
        'stop_loss_pct': (0.87, 0.95), 
        'sellat_up': (1.01,1.20),
        "short": (6,18), # short EMA
        "long": (13,39), # long EMA
        "signal": (1,18), # 100 * (shortEMA - longEMA / longEMA)
        "thresholds.down": (-0.5,0.), # trend thresholds
        "thresholds.up": (0.,0.5), # trend thresholds
        "thresholds.persistence": (2,10), # trend duration(count up by tick) thresholds
    },
    "DEMA":{
        "short": (1,10), # short EMA
        "long": (20,50), # long EMA
        "thresholds.down": (-0.5,0.1), # trend thresholds
        "thresholds.up": (-0.1,0.5), # trend thresholds
    },
    "MACD":{
        "short": (1,10), # short EMA
        "long": (20,50), # long EMA
        "signal": (9,18), # shortEMA - longEMA diff
        "thresholds.down": (-0.5,0.), # trend thresholds
        "thresholds.up": (0.,0.5), # trend thresholds
        "thresholds.persistence": (2,10), # trend duration(count up by tick) thresholds
    },
    "PPO":{
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
        "interval": (7,21), # weight
        "thresholds.low": (15,45), # trend thresholds
        "thresholds.high": (45,140), # trend thresholds
        "thresholds.persistence": (4,10), # trend duration(count up by tick) thresholds
    },
    "StochRSI":{
        "interval": (7,21), # weight
        "thresholds.low": (15,45), # trend thresholds
        "thresholds.high": (45,140), # trend thresholds
        "thresholds.persistence": (4,10), # trend duration(count up by tick) thresholds
    },
    "CCI":{
        "consistant": (7,21), # constant multiplier. 0.015 gets to around 70% fit
        "history": (45,135), # history size, make same or smaller than history
        "thresholds.down": (-150,-50), # trend thresholds
        "thresholds.up": (50,150), # trend thresholds
        "thresholds.persistence": (4,10), # trend duration(count up by tick) thresholds
    },
    "UO":{
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
