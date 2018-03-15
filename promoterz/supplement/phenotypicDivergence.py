#!/bin/python
from deap import tools
from . .import parameterOperations
import random


def checkPhenotypicDivergence(constructPhenotype, indA, indB):
    cmp = [indA, indB]
    cmp = [constructPhenotype(x) for x in cmp]
    cmp = [parameterOperations.flattenParameters(x) for x in cmp]
    score = 0
    for w in cmp[0].keys():
        if cmp[0][w] != cmp[1][w]:
            score += 1
    return score


def populationPhenotypicDivergence(constructPhenotype, population, delpercent):
    if len(population) > 1:
        for I in range(len(population) - 1):
            for J in range(I + 1, len(population)):
                if population[I]:
                    score = checkPhenotypicDivergence(
                        constructPhenotype, population[I], population[J]
                    )
                    if not score and random.random() < delpercent:
                        population[I] = None
    population = [x for x in population if x]
    return population
