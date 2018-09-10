#!/bin/python
from deap import base


def getExtraTools(HallOfFame, W):
    T = base.Toolbox()
    T.register('q')
