#!/bin/python
#from subprocess import run
from subprocess import Popen, PIPE
import random
from copy import deepcopy
import operator
from functools import reduce
from urllib import request, parse
import json
import requests
import datetime
import os

gekkoDIR = 'TBD'


def firePaperTrader(GekkoInstanceUrl, TradeSetting, Exchange, Currency, Asset):
    TradeMethod = list(TradeSetting.keys())[0]
    true = True
    false = False
    CONFIG = {
        "market": {"type": "leech", "from": "2017-09-13T15:42:00Z"},  # TIME ATM;
        "mode": "realtime",
        "watch": {"exchange": Exchange, "currency": Currency, "asset": Asset},
        "tradingAdvisor": {
            "enabled": true, "method": TradeMethod, "candleSize": 60, "historySize": 10
        },
        TradeMethod: TradeSetting[TradeMethod],
        "paperTrader": {
            "fee": 0.25,
            "slippage": 0.05,
            "simulationBalance": {"asset": 1, "currency": 100},
            "reportRoundtrips": true,
            "enabled": true,
        },
        "candleWriter": {"enabled": true, "adapter": "sqlite"},
        "type": "paper trader",
        "performanceAnalyzer": {"riskFreeReturn": 2, "enabled": true},
        "valid": true,
    }
    RESULT = httpPost(URL, CONFIG)
    print(RESULT)
