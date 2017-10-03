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

def evaluatePopulation(population, evaluationFunction):
    individues_to_simulate = [ind for ind in POP if not ind.fitness.valid]
    fitnesses = parallel.starmap(evaluationFunction, zip(individues_to_simulate))
    for ind, fit in zip(individues_to_simulate, fitnesses):
        ind.fitness.values = fit

def getEvolutionToolbox(HallOfFame, population_generator):
    T = base.toolbox()

    coreTools.register("ImmigrateHoF", immigrateHoF, HallOfFame)
    coreTools.register("ImmigrateRandom", immigrateRandom, population_generator)

    return T
