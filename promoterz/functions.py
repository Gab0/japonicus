#!/bin/python
import random
from deap import base
from deap import creator
from deap import tools
from copy import deepcopy

import importlib


def PrepareAndEvaluate(constructPhenotype, evaluationMethod, Individual):
    phenotype = constructPhenotype(Individual)
    return evaluationMethod(phenotype)


def selectRepresentationMethod(methodname):
    M = importlib.import_module("promoterz.representation.%s" % methodname)
    return M
