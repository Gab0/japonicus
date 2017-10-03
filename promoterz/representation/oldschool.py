#!/bin/python
import random
import json
import os

from copy import deepcopy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import numpy as np



from gekkoWrapper import *


from Settings import getSettings
#from plotInfo import plotEvolutionSummary

def reconstructTradeSettings(IND):
    # THIS FUNCTION IS UGLYLY WRITTEN; USE WITH CAUTION;
    # (still works :})
    Strategy = IND.Strategy
    R = lambda V, lim: ((lim[1]-lim[0])/100) * V + lim[0]
    stratSettings = getSettings()['strategies'][Strategy]
    Settings = {
        Strategy:{}
        }
    i=0
    for K in stratSettings.keys():
        Value = R(IND[i], stratSettings[K])
        if '.' in K:
            K=K.split('.')
            if not K[0] in list(Settings[Strategy].keys()):
                Settings[Strategy][K[0]] = {}
            Settings[Strategy][K[0]][K[1]] = Value
        else:
            Settings[Strategy][K] = Value
        i+=1

    return Settings


def createRandomVarList(SZ=10):
    VAR_LIST = [random.randrange(0,100) for x in range(SZ)]
    return VAR_LIST


def initInd(Criterion):
    w = Criterion()
    w[:] = createRandomVarList()
    return w


def getToolbox(genconf):
    toolbox = base.Toolbox()
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list,
                   fitness=creator.FitnessMax, Strategy=genconf.Strategy)
    toolbox.register("newind", initInd, creator.Individual)

    toolbox.register("population", tools.initRepeat, list,  toolbox.newind)

    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=10, up=10, indpb=0.2)

    return toolbox
