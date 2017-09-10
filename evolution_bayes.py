#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import datetime
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.finance as mpf
from matplotlib import ticker
import matplotlib.dates as mdates
from gekkoWrapper import getAvailableDataset, runBacktest, getCandles
#from plotInfo import plotEvolutionSummary


def moving_average(x, n, type='simple'):
    """
    compute an n period moving average.

    type is 'simple' | 'exponential'

    """
    x = np.asarray(x)
    if type == 'simple':
        weights = np.ones(n)
    else:
        weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()

    a = np.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a


def relative_strength(prices, n=14):
    """
    compute the n period relative strength indicator
    http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
    http://www.investopedia.com/terms/r/rsi.asp
    """

    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n - 1) + upval)/n
        down = (down*(n - 1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)

    return rsi


def moving_average_convergence(x, nslow=26, nfast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = moving_average(x, nslow, type='exponential')
    emafast = moving_average(x, nfast, type='exponential')
    return emaslow, emafast, emafast - emaslow

def reconstructTradeSettingsDict(IND, Strategy):
    f = {
        "short": lambda x: x//5+1,
        "long": lambda x: x//3+10,
        "signal": lambda x: x//10+5,
        "interval": lambda x: x//3,
        "down": lambda x: (x//1.5-50)/40,
        "up": lambda x: (x//1.5-5)/40,
        "low": lambda x: x//2+10,
        "high": lambda x: x//2+45,
        "persistence": lambda x: x//25+1,
        "fibonacci": lambda x: (x//11+1)/10
    }
    Settings = {}
    Settings[Strategy] = {}
    Settings[Strategy]["thresholds"] = {}
    for key in "short long signal interval".split(" "):
        if key in IND:
            Settings[Strategy][key] = f[key](IND[key])
    for key in "down up low high persistence fibonacci".split(" "):
        if key in IND:
            Settings[Strategy]["thresholds"][key] = f[key](IND[key])
    return Settings

def reconstructTradeSettings(IND, Strategy):
    Settings = {
        Strategy:{
            "short": IND[0]//5+1,
            "long": IND[1]//3+10,
            "signal": IND[2]//10+5,
            "interval": IND[3]//3,
            "thresholds": {
                "down": (IND[4]//1.5-50)/40,
                "up": (IND[5]//1.5-5)/40,
                "low": IND[6]//2+10,
                "high": IND[7]//2+45,
                "persistence": IND[8]//25+1,
                "fibonacci": (IND[9]//11+1)/10
            }
        }
    }
        
    return Settings

def getRandomDateRange(Limits, deltaDays=3):
    DateFormat="%Y-%m-%d %H:%M:%S"

    epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime(DateFormat)
    FLms = Limits['from']
    TLms = Limits['to']
    deltams=deltaDays * 24 * 60 * 60
    testms=testDays * 24 * 60 * 60

    Starting= random.randint(FLms,TLms-deltams-testms)
    DateRange = {
        "from": "%s" % epochToString(Starting),
        "to": "%s" % epochToString(Starting+deltams)
    }
    return DateRange
def getDateRange(Limits, deltaDays=3):
    DateFormat="%Y-%m-%d %H:%M:%S"

    epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime(DateFormat)
    deltams=deltaDays * 24 * 60 * 60

    DateRange = {
        "from": "%s" % epochToString(Limits['to']-deltams),
        "to": "%s" % epochToString(Limits['to'])
    }
    return DateRange

def Evaluate(DateRange, Individual, Strategy):
    Settings = reconstructTradeSettingsDict(Individual, Strategy)
    Score = runBacktest(Settings, DateRange)
    return Score

def gekko_search(**args):
    #print(args)
    #print(params)
    params.update(args.copy())
    #print(params)
    scores = np.zeros((num_rounds))
    for i in range(num_rounds):
        chosenRange = getAvailableDataset()
        DateRange = getRandomDateRange(chosenRange, deltaDays=deltaDays)
        scores[i] = Evaluate(DateRange, params, Strategy)
    smean = np.mean(scores)
    sstd = np.std(scores)
    smax = np.max(scores)
    smin = np.min(scores)
    stats.append([smean, sstd, smax, smin])
    all_val.append(smean)
    return smean

def candlechart(ohlc, width=0.8):
    fig, ax = plt.subplots()
    mpf.candlestick2_ohlc(ax, opens=ohlc.open.values, closes=ohlc.close.values,
                          lows=ohlc.low.values, highs=ohlc.high.values,
                          width=width, colorup='r', colordown='b')

    xdate = ohlc.index
    ax.xaxis.set_major_locator(ticker.MaxNLocator(6))

    def mydate(x, pos):
        try:
            return xdate[int(x)]
        except IndexError:
            return ''

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.grid()

    fig.autofmt_xdate()
    fig.tight_layout()

    return fig, ax

def showCandles():
    chosenRange = getAvailableDataset()
    DateRange = getDateRange(chosenRange["to"], deltaDays=deltaDays)
    print("\t%s to %s" % (DateRange['from'], DateRange['to']))
    candle = getCandles(DateRange)
    df = pd.DataFrame(candle)
    df["start"] = pd.to_datetime(df["start"], unit='s')
    df.index = df["start"]
    fig, ax = candlechart(df)
    fig.show()
    plt.waitforbuttonpress()
    exit()

def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    #yield key + "." + subkey, subvalue
                    yield subkey, subvalue
            else:
                yield key, value

    return dict(items())

if __name__ == '__main__':
    MODES = ['MACD', 'DEMA', 'RSI', 'PPO']
    Strategy = MODES[2]
    filename = "example-config.js"
    with open(filename, "r") as f:
        text = f.read()
    text = text.replace("module.exports = config;","config;")
    import js2py
    config = js2py.eval_js(text).to_dict()
    #print(config)
    deltaDays = 3
    testDays = 3
    num_rounds = 30
    random_state = 2016
    num_iter = 25
    init_points = 5
    all_val = []
    stats = []

    params = flatten_dict(config[Strategy])
    print("")
    print("Starting search %s parameters" % Strategy)
    #print(params)

    from bayes_opt import BayesianOptimization
    bo = BayesianOptimization(gekko_search, {
            "short": (1,30),
            "long": (1,30),
            "signal": (5,10),
            "interval": (3,15),
            "down": (-0.025,0.025),
            "up": (-0.025,0.025),
            "low": (3,30),
            "high": (45,70),
            "fibonacci": (0.1, 0.2)
        })

    bo.maximize(init_points=init_points, n_iter=num_iter)

    print('='*50)
    print('Final Results')
    max_val = bo.res['max']['max_val']
    index = all_val.index(max_val)
    s = stats[index]
    print('='*50)
    print(json.dumps(bo.res, indent=2))
    print('-'*53)
    print('Avg: %f' % s[0])
    print('Std: %f' % s[1])
    print('Max: %f' % s[2])
    print('Min: %f' % s[3])
    print('-'*50)
    max_params = bo.res['max']['max_params'].copy()
    max_params["persistence"] = 1
    resultjson = json.dumps(reconstructTradeSettingsDict(max_params, Strategy), indent=2)
    print("Result Config: %s" % resultjson)
    print('-'*50)
    chosenRange = getAvailableDataset()
    DateRange = getDateRange(chosenRange, deltaDays=testDays)
    print("Evaluate nearest date: %s to %s" % (DateRange['from'], DateRange['to']))
    scores = Evaluate(DateRange, max_params, Strategy)
    print("Evaluted Score: %f" % scores)



