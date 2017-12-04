#1/bin/python

cI = {
    "PPO":{
        "active": True,
        "short": (6,18), # short EMA
        "long": (13,39), # long EMA
        "signal": (1,18), # 100 * (shortEMA - longEMA / longEMA)
        "thresholds.down": (-0.5,0.), # trend thresholds
        "thresholds.up": (0.,0.5) # trend thresholds
    },
    "TSI":{
        "active": True,
        "thresholds.up": (15,35),
        "thresholds.down": (-35,-15),
        "short": (3,12),
        "long": (15,35)
    },
    "LRC": {
        "active": True,
        "thresholds.up": (15,35),
        "thresholds.down": (-35,-15),
        "depth": (3,18)
    },
    "RSI":{
        "active": True,
        "interval": (7,21), # weight
        "thresholds.down": (15,45), # trend thresholds
        "thresholds.up": (45,140), # trend thresholds
    },
    "SMMA":{
        "active": True,
        "weight": (7,16),
        "thresholds.up": (0,0.1),
        "thresholds.down": (-0.1,0)
        },
    "DEMA":{
        "active": True,
        "short": (7,15),
        "long": (12,35),
        "thresholds.up": (0,0.1),
        "thresholds.down": (-0.1,0)
    },
    "CCI":{
        "active": True,
        "consistant": (7,21), # constant multiplier. 0.015 gets to around 70% fit
        "history": (45,135), # history size, make same or smaller than history
        "thresholds.down": (-150,-50), # trend thresholds
        "thresholds.up": (50,150), # trend thresholds
        "thresholds.persistence": (4,10)},
"persistence": (1,5)
}
