#!/bin/python

from deap import creator
from deap import base


def init(fitness, extraParameters):
    creator.create("FitnessMax", fitness, weights=(1.0, 1))
    creator.create("Individual", list,
                   fitness=creator.FitnessMax, **extraParameters)

    return creator
