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


def filterAwayThreshold(locale, Threshold, min_nb_inds):
    thresholdFilter = lambda ind: ind.fitness.values[0] > Threshold
    populationFilter(locale, thresholdFilter, min_nb_inds)


def filterAwayTradeCounts(locale, ThresholdRange, min_nb_inds):
    def tradecountFilter(ind):
        if ind.trades < ThresholdRange[0]:
            return False
        elif ind.trades > ThresholdRange[1]:
            return False
        else:
            return True

    populationFilter(locale, tradecountFilter, min_nb_inds)


def filterAwayRoundtripDuration(locale, ThresholdRange, min_nb_inds):
    def roundtripDurationFilter(ind):
        averageExposureHours = ind.averageExposure
        if averageExposureHours < ThresholdRange[0]:
            return False
        elif averageExposureHours > ThresholdRange[1]:
            return False
        else:
            return True

    populationFilter(locale, roundtripDurationFilter, min_nb_inds)


def populationFilter(locale, filterFunction, min_nb_inds):

    newPopulation = [
        ind for ind in locale.population if filterFunction(ind)
    ]
    removed = [ind for ind in locale.population if ind not in newPopulation]

    NBreturn = min(min_nb_inds - len(locale.population),
                          min_nb_inds)
    NBreturn = max(0, NBreturn)
    if NBreturn and removed:
        for k in range(NBreturn):
            if removed:
                newPopulation.append(removed.pop(random.randrange(0,
                                                                  len(removed))))

    locale.population = newPopulation


def evaluatePopulation(locale):
    individues_to_simulate = [ind for ind in locale.population
                              if not ind.fitness.valid]
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
    toolbox.register("filterTrades", filterAwayTradeCounts, locale)
    toolbox.register("filterExposure", filterAwayRoundtripDuration, locale)
    toolbox.register('ageZero', promoterz.supplement.age.ageZero)
    toolbox.register(
        'populationAges',
        promoterz.supplement.age.populationAges,
        World.conf.generation.ageBoundaries,
    )
    toolbox.register(
        'populationPD',
        promoterz.supplement.phenotypicDivergence.populationPhenotypicDivergence,
        World.tools.constructPhenotype,
    )
    toolbox.register('evaluatePopulation', evaluatePopulation)
    return toolbox


def getGlobalToolbox(representationModule):
    # GLOBAL FUNCTION TO GET GLOBAL TBX UNDER DEVELOPMENT;
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


def selectCriteria(ind):
    return sum(ind.fitness.wvalues)


def selBest(individuals, number):
    chosen = sorted(individuals, key=selectCriteria, reverse=True)
    return chosen[:number]


def Tournament(individuals, finalselect, tournsize):
    chosen = []
    for i in range(finalselect):
        aspirants = tools.selRandom(individuals, tournsize)
        chosen.append(max(individuals, key=selectCriteria))
    return chosen
