#!/bin/python

from deap import base
from copy import deepcopy
import random
class SimulatedEnvironment():
    def __init__(self):

        self.toolbox = []
        self.HallOfFame = base.HallOfFame(30)
        self.population = []

def immigrateHoF(population, HallOfFame):
    if not HallOfFame.items:
        return population

    for Q in range(1):
        CHP = deepcopy(random.choice(HallOfFame))
        del CHP.fitness.values
        population += [CHP]
    return population

def immigrateRandom(population, populate): #(populate function)
    number = random.randint(1,9)
    population += populate(number)
    return population
