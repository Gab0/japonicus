#!/bin/python

stdResult = ["> this.settings.{i}.thresholds.up",
             "< this.settings.{i}.thresholds.down"]
againstPrice = ["> price", "< price"]

Reverse = lambda x: [x[1], x[0]]

IndicatorProperties = {
    "ADX" : {
        "input": '',
        "attrname": "result",
        "result": stdResult,
        "group": "momentum"
    },

    "ATR": {
        "input": '',
        "attrname": "result",
        "result": stdResult,
        "group": "volatility"
    },

    "PPO": {
        "input": '',
        "attrname": "PPOhist",
        "result": stdResult,
        "group": "momentum"
    },

    "DEMA": {
        "attrname": "result",
        "result": stdResult,
        "input": '',
    "group": "trend"
    },

    "RSI": {
        "result": Reverse(stdResult),
        "input": '',
        "attrname": "result",
        "group": "momentum"
    },

    "TSI": {
        "input": '',
        "result": stdResult,
        "attrname": "result",
        "group": "momentum"
    },

    "LRC": {
        "result": againstPrice,
        "attrname": "result",
        "input": '.depth',
        "group": "trend"
    },

    "SMMA": {
        "input": '',
        "attrname": 'result',
        "result": stdResult,
        "group": "overlap"
    },

    "CCI": {
        "input": '',
        "result": stdResult,
        "attrname": 'result',
        "group": "momentum"
    }
        }
