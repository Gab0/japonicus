#!/bin/python
from deap import tools
from copy import deepcopy
import random
from deap import algorithms
import promoterz

def standard_loop(locale):
    assert(len(locale.population))

    # --validate individuals;
    locale.population=promoterz.validation.validatePopulation(
        locale.tools.constructPhenotype,
        {locale.genconf.Strategy: locale.TargetParameters},
        locale.population)

    # --evaluate individuals;
    nb_evaluated=promoterz.evaluatePopulation(locale.population,
                                              locale.extratools.evaluate,
                                              locale.parallel)

    assert(len(locale.population))
    assert(sum([x.fitness.valid for x in locale.population]) == len(locale.population))
    # --compile stats;
    locale.compileStats()

    # --show stats;
    locale.showStats(nb_evaluated)

    # --calculate new population size;
    if locale.EPOCH:
        PRoFIGA = promoterz.supplement.PRoFIGA.calculatePRoFIGA(
            locale.genconf.PRoFIGA_beta, locale.EPOCH,
            locale.genconf.NBEPOCH,
            locale.EvolutionStatistics[locale.EPOCH-1],
            locale.EvolutionStatistics[locale.EPOCH])

        deltaPOP_SIZE = max(int(round( locale.POP_SIZE * PRoFIGA )), locale.genconf.POP_SIZE//2 )
        deltaPOP_SIZE = min(deltaPOP_SIZE, 899)
        locale.POP_SIZE += deltaPOP_SIZE

    # --population ages
    qpop=len(locale.population)
    locale.population=locale.extratools.populationAges(locale.population, locale.EvolutionStatistics[locale.EPOCH])
    wpop=len(locale.population)
    print('elder %i' % (qpop-wpop))

    assert(len(locale.population))
    assert(None not in locale.population)

    # --send best individue to HallOfFame;
    if not locale.EPOCH % 15:
            BestSetting = tools.selBest(locale.population, 1)[0]
            locale.HallOfFame.insert(BestSetting)
            #print(EvolutionStatistics)

            #FinalBestScores.append(Stats['max'])
            '''
            print("Loading new date range;")

            print("\t%s to %s" % (locale.DateRange['from'], locale.DateRange['to']))
            for I in range(len(locale.population)):
                del locale.population[I].fitness.values
            toolbox.register("evaluate", coreFunctions.Evaluate,
                                 GenerationMethod.constructPhenotype, DateRange)
            FirstEpochOfDataset = True
            bestScore = 0
            '''
    assert(None not in locale.population)

    # --immigrate individual from HallOfFame;
    if random.random() < 0.2:
        locale.population = locale.extratools.ImmigrateHoF(locale.population)

    # --immigrate random number of random individues;
    if random.random() < 0.5:
        locale.population = locale.extratools.ImmigrateRandom( (2,7), locale.population)


    assert(len(locale.population))

    # --select best individues to procreate
    offspring = tools.selTournament(locale.population,
                                    locale.genconf._lambda, 2*locale.genconf._lambda)
    offspring = [deepcopy(x) for x in offspring] # is deepcopy necessary?

    # --modify and integrate offspring;
    offspring = algorithms.varAnd(offspring, locale.tools,
                                  locale.genconf.cxpb, locale.genconf.mutpb)
    locale.extratools.ageZero(offspring)
    locale.population += offspring



    assert(len(locale.population))


    # --filter best inds;
    locale.population[:] = tools.selBest(locale.population, locale.POP_SIZE)

    # --log statistcs;
    '''
    if FirstEpochOfDataset:
        InitialBestScores.append(Stats['max'])
        Stats['dateRange'] = "%s ~ %s" % (locale.DateRange['from'], locale.DateRange['to'])
    else:
        Stats['dateRange'] = None
    '''




    assert(None not in locale.population)

    #print("POPSIZE %i" % len(locale.population))




