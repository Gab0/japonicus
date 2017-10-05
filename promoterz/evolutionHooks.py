#!/bin/python

from deap import base
from copy import deepcopy

import random

class SimulatedEnvironment(): # envelope main evolution loop as class? maybe tbd
    def __init__(self):

        self.toolbox = []
        self.HallOfFame = base.HallOfFame(30)
        self.population = []

# population always as last positional argument, to blend with toolbox;
def immigrateHoF(HallOfFame, population):
    if not HallOfFame.items:
        return population

    for Q in range(1):
        CHP = deepcopy(random.choice(HallOfFame))
        del CHP.fitness.values
        population += [CHP]
    return population

def immigrateRandom(populate, population): #(populate function)
    number = random.randint(1,9)
    population += populate(number)
    return population

def filterAwayWorst(population, N=5):
    aliveSize = len(population)-5
    population = tools.selBest(population, aliveSize)
    return population

def evaluatePopulation(population, evaluationFunction, pool):
    individues_to_simulate = [ind for ind in population if not ind.fitness.valid]
    fitnesses = pool.starmap(evaluationFunction, zip(individues_to_simulate))
    for i, fit in zip(range(len(individues_to_simulate)), fitnesses):
        individues_to_simulate[i].fitness.values = fit
    return len(individues_to_simulate)

def getEvolutionToolbox(HallOfFame, population_generator):
    T = base.Toolbox()

    T.register("ImmigrateHoF", immigrateHoF, HallOfFame)
    T.register("ImmigrateRandom", immigrateRandom, population_generator)

    return T
