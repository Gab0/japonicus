#!/bin/python
import js2py
from pathlib import Path

from .configStrategies import cS
from .configIndicators import cI

import os
import pytoml


class makeSettings(dict):
    def __init__(self, entries):
        for K in entries.keys():
            if type(entries[K]) == dict:
                entries[K] = makeSettings(entries[K])
        self.__dict__.update(entries)
        self.update(entries)


def getSettings(specific=None):
    HOME = str(Path.home())

    s = {
        # gekko global settings;
        'global': loadTomlSettings('global'),
        # gekko backtest settings;
        'backtest': loadTomlSettings('backtest'),
        # evaluation break settings;
        'evalbreak': loadTomlSettings('evalbreak'),
        # genetic algorithm settings;
        'generations': loadTomlSettings('generations'),

        'dataset': loadTomlSettings('dataset'),

        'strategies': cS,
        'indicators': cI,
        'skeletons': {
            'ontrend': {
                "SMA_long": 1000,
                "SMA_short": 50
            }
        }
    }

    s['global']['gekkoPath'] = s['global']['gekkoPath'].replace("$HOME", HOME)
    if specific is not None:
        if not specific:
            return makeSettings(s)
        else:
            return makeSettings(s[specific])

    return s


def loadTomlSettings(settingsDivisionName):
    userSettingsAndDefaultSettings = [
        '%s.toml' % settingsDivisionName,
        '_%s.toml' % settingsDivisionName
    ]
    for targetFile in userSettingsAndDefaultSettings:
        filePath = os.path.join('settings', targetFile)
        if os.path.isfile(filePath):
            Settings = pytoml.load(open(filePath))
            return Settings

    exit("Failed to load settings! %s" % settingsDivisionName)


def get_configjs(filename="example-config.js"):
    with open(filename, "r") as f:
        text = f.read()
    text = text.replace("module.exports = config;","config;")
    return js2py.eval_js(text).to_dict()
