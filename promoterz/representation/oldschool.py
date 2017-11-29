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
from .. import utils

def constructPhenotype(stratSettings, individue):
    # THIS FUNCTION IS UGLYLY WRITTEN; USE WITH CAUTION;
    # (still works :})

    Strategy = individue.Strategy
    R = lambda V, lim: ((lim[1]-lim[0])/100) * V + lim[0]

    AttributeNames = sorted(list(stratSettings.keys()))
    Phenotype = {}
    for K in range(len(AttributeNames)):
        Value = R(individue[K], stratSettings[AttributeNames[K]])
        Phenotype[AttributeNames[K]] = Value

    Phenotype = utils.expandNestedParameters(Phenotype)

    return Phenotype


def createRandomVarList(IndSize):
    VAR_LIST = [random.randrange(0,100) for x in range(IndSize)]
    return VAR_LIST


def initInd(Criterion, Attributes):
    w = Criterion()
    IndSize =len(list(Attributes.keys()))
    w[:] = createRandomVarList(IndSize)
    return w


def getToolbox(Strategy, genconf, Attributes):
    toolbox = base.Toolbox()
    creator.create("FitnessMax", base.Fitness, weights=(1.0, 3))
    creator.create("Individual", list,
                   fitness=creator.FitnessMax, Strategy=Strategy)
    toolbox.register("newind", initInd, creator.Individual, Attributes)

    toolbox.register("population", tools.initRepeat, list,  toolbox.newind)

    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=10, up=10, indpb=0.2)

    toolbox.register("constructPhenotype", constructPhenotype, Attributes)
    return toolbox
