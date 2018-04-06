#!/bin/python
from .import deapCreator as creator
from deap import base


def init(fitness, extraParameters):
    creator.create("FitnessMax", fitness, weights=(1.0, 1))
    creator.create("Individual", list, fitness=creator.FitnessMax, **extraParameters)
    return creator
