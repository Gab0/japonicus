#!/bin/python
from deap import base, tools
from copy import deepcopy

import random

import promoterz.supplement.age
import promoterz.supplement.PRoFIGA
import promoterz.supplement.phenotypicDivergence

import itertools



# population as last positional argument, to blend with toolbox;
def immigrateHoF(HallOfFame, population):
    if not HallOfFame.items:
        return population

    for Q in range(1):
        CHP = deepcopy(random.choice(HallOfFame))
        del CHP.fitness.values
        population += [CHP]
    return population


def immigrateRandom(populate, nb_range, population):  # (populate function)
    number = random.randint(*nb_range)
    population += populate(number)
    return population


def filterAwayWorst(population, N=5):
    aliveSize = len(population) - 5
    population = tools.selBest(population, aliveSize)
    return population


def filterAwayThreshold(locale, Threshold, minimum):
    remove = [ind for ind in locale.population if ind.fitness.values[0] <= Threshold]
    locale.population = [
        ind for ind in locale.population if ind.fitness.values[0] > Threshold
    ]
    NBreturn = max(0, min(minimum - len(locale.population), minimum))
    if NBreturn and remove:
        for k in range(NBreturn):
            locale.population.append(random.choice(remove))


def evaluatePopulation(locale):
    individues_to_simulate = [ind for ind in locale.population if not ind.fitness.valid]
    fitnesses = locale.World.parallel.starmap(
        locale.extratools.Evaluate, zip(individues_to_simulate)
    )
    for i, fit in zip(range(len(individues_to_simulate)), fitnesses):
        individues_to_simulate[i].fitness.values = fit
    return len(individues_to_simulate)


def getLocaleEvolutionToolbox(World, locale):
    toolbox = base.Toolbox()
    toolbox.register("ImmigrateHoF", immigrateHoF, locale.HallOfFame)
    toolbox.register("ImmigrateRandom", immigrateRandom, World.tools.population)
    toolbox.register("filterThreshold", filterAwayThreshold, locale)
    toolbox.register('ageZero', promoterz.supplement.age.ageZero)
    toolbox.register(
        'populationAges',
        promoterz.supplement.age.populationAges,
        World.genconf.ageBoundaries,
    )
    toolbox.register(
        'populationPD',
        promoterz.supplement.phenotypicDivergence.populationPhenotypicDivergence,
        World.tools.constructPhenotype,
    )
    toolbox.register('evaluatePopulation', evaluatePopulation)
    return toolbox


def getGlobalToolbox(representationModule):
    # GLOBAL FUNCTION TO GET GLOBAL TBX UNDER DEVELOPMENT (ITS COMPLICATED);
    toolbox = base.Toolbox()
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create(
        "Individual",
        list,
        fitness=creator.FitnessMax,
        PromoterMap=None,
        Strategy=genconf.Strategy,
    )
    toolbox.register("mate", representationModule.crossover)
    toolbox.register("mutate", representationModule.mutate)
    PromoterMap = initPromoterMap(Attributes)
    toolbox.register("newind", initInd, creator.Individual, PromoterMap)
    toolbox.register("population", tools.initRepeat, list, toolbox.newind)
    toolbox.register("constructPhenotype", representationModule.constructPhenotype)
    return toolbox


def getFitness(individual):
    R = sum(individual.wvalues)




# selectCriteria = lambda x: sum(x.fitness.wvalues)
def selectCriteria(ind):
    p = ind.fitness.wvalues[0]
    s = (1 + ind.fitness.wvalues[1])
    R = p * s
    if p < 0 and s < 0:
        R = - abs(R)
    return R


def selBest(individuals, number):
    chosen = sorted(individuals, key=selectCriteria, reverse=True)
    return chosen[:number]


def Tournament(individuals, finalselect, tournsize):
    chosen = []
    for i in range(finalselect):
        aspirants = tools.selRandom(individuals, tournsize)
        chosen.append(max(individuals, key=selectCriteria))
    return chosen
