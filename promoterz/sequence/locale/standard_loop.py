#!/bin/python
from deap import tools
from copy import deepcopy
import random
from deap import algorithms

import statistics
from ... import evolutionHooks
from ... import validation
from ... import supplement

def checkPopulation(population, message):
    if not (len(population)):
        print(message)


def execute(World, locale):

    # --assertions are most for debugging purposes; they should not trigger
    assert (len(locale.population))
    locale.extraStats = {}

    # --validate individuals;
    locale.population = validation.validatePopulation(
        World.tools.constructPhenotype, World.TargetParameters, locale.population
    )

    # --remove equal citizens before evaluation for efficency
    nonevaluated = [ind for ind in locale.population if not ind.fitness.valid]
    Lu = len(nonevaluated)
    print("first unevaluated: %i" % len(nonevaluated))
    remains = locale.extratools.populationPD(nonevaluated, 1.0)
    Lr = len(remains)
    print("%i individues removed due to equality" % (Lu - Lr))
    locale.population = [
        ind for ind in locale.population if ind.fitness.valid
    ] + remains

    # --evaluate individuals;
    locale.extraStats['nb_evaluated'], locale.extraStats[
        'avgTrades'
    ] = World.parallel.evaluatePopulation(
        locale
    )

    locale.extraStats['avgExposure'] = sum([I.averageExposure for I in locale.population])/len(locale.population)

    # --send best individue to HallOfFame;
    if not locale.EPOCH % 15:
        BestSetting = tools.selBest(locale.population, 1)[0]
        locale.HallOfFame.insert(BestSetting)
    assert (sum([x.fitness.valid for x in locale.population]) == len(locale.population))

    # --compile stats;
    statistics.compileStats(locale)
    # --population ages
    qpop = len(locale.population)
    locale.population = locale.extratools.populationAges(
        locale.population, locale.EvolutionStatistics[locale.EPOCH]
    )
    wpop = len(locale.population)
    locale.extraStats['nbElderDies'] = qpop - wpop

    # INDIVIDUE FITNESS ATTRIBUTES FILTERS;
    # --remove very inapt citizens
    if World.genconf.minimumProfitFilter is not None:
        locale.extratools.filterThreshold(World.genconf.minimumProfitFilter,
                                          World.genconf._lambda)
        checkPopulation(locale.population, "Population dead after profit filter.")

    # --remove individuals below tradecount
    if World.genconf.TradeNumberFilterRange is not None:
        locale.extratools.filterTrades(World.genconf.TradeNumberFilterRange,
                                       World.genconf._lambda)
        checkPopulation(locale.population, "Population dead after trading number filter.")

    # --remove individues based on average roundtripe exposure time;
    if World.genconf.averageExposureLengthFilterRange is not None:
        locale.extratools.filterExposure(
            World.genconf.averageExposureLengthFilterRange,
            World.genconf._lambda
        )
        checkPopulation(locale.population, "Population dead after roundtrip exposure filter.")

    if not locale.population:
        locale.population = World.tools.population(World.genconf.POP_SIZE)
        print("Repopulating... Aborting epoch.")
    # --show stats;
    statistics.showStatistics(locale)
    # --calculate new population size;
    if locale.EPOCH:
        PRoFIGA = supplement.PRoFIGA.calculatePRoFIGA(
            World.genconf.PRoFIGA_beta,
            locale.EPOCH,
            World.genconf.NBEPOCH,
            locale.EvolutionStatistics[locale.EPOCH - 1],
            locale.EvolutionStatistics[locale.EPOCH],
        )
        locale.POP_SIZE += locale.POP_SIZE * PRoFIGA
        minps, maxps = World.genconf.POP_SIZE // 2, World.genconf.POP_SIZE * 3
        try:
            locale.POP_SIZE = int(round(max(min(locale.POP_SIZE, maxps), minps)))
        except:
            locale.POP_SIZE = 30
            M = "POP_SIZE PROFIGA ERROR;"
            print(M)
    # --filter best inds;
    locale.population[:] = evolutionHooks.selBest(locale.population, locale.POP_SIZE)
    checkPopulation(locale.population, "Population dead after selection of score filter.")
    assert (None not in locale.population)
    # print(EvolutionStatistics)
    #FinalBestScores.append(Stats['max'])

    # --select best individues to procreate
    LAMBDA = max(World.genconf._lambda, locale.POP_SIZE - len(locale.population))
    TournamentSize = max(2 * LAMBDA, len(locale.population))
    offspring = evolutionHooks.Tournament(locale.population, LAMBDA, TournamentSize)
    offspring = [deepcopy(x) for x in offspring]  # is deepcopy necessary?
    # --modify and integrate offspring;
    offspring = algorithms.varAnd(
        offspring, World.tools, World.genconf.cxpb, World.genconf.mutpb
    )
    locale.extratools.ageZero(offspring)
    locale.population += offspring
    # --NOW DOESN'T MATTER IF SOME INDIVIDUE LACKS FITNESS VALUES;
    assert (None not in locale.population)
    # --immigrate individual from HallOfFame;
    if random.random() < 0.2:
        locale.population = locale.extratools.ImmigrateHoF(locale.population)
    # --immigrate random number of random individues;
    if random.random() < 0.5:
        locale.population = locale.extratools.ImmigrateRandom((2, 7), locale.population)
    assert (len(locale.population))

    assert (None not in locale.population)
