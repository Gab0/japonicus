#!/bin/python
from deap import tools
from copy import deepcopy
import random
from deap import algorithms
import promoterz
from .. import statistics, evolutionHooks
def standard_loop(World, locale):
    assert(len(locale.population))
    locale.extraStats = {} 
    # --validate individuals;
    locale.population=promoterz.validation.validatePopulation(
        World.tools.constructPhenotype,
        World.TargetParameters,
        locale.population)

    # --evaluate individuals;
    locale.extraStats['nb_evaluated'], locale.extraStats['avgTrades']= World.parallel.evaluatePopulation(locale)

    assert(len(locale.population))
    # --send best individue to HallOfFame;
    if not locale.EPOCH % 15:
        BestSetting = tools.selBest(locale.population, 1)[0]
        locale.HallOfFame.insert(BestSetting)

    assert(len(locale.population))
    assert(sum([x.fitness.valid for x in locale.population]) == len(locale.population))


    # --compile stats;
    statistics.compileStats(locale)

    # --population ages
    qpop=len(locale.population)
    locale.population=locale.extratools.populationAges(
        locale.population,
        locale.EvolutionStatistics[locale.EPOCH])

    wpop=len(locale.population)
    locale.extraStats['elder']=qpop-wpop

    # --remove equal citizens
    locale.population = locale.extratools.populationPD(locale.population)

    # --remove very inapt citizens
    locale.extratools.filterThreshold(-15)
    
    # --show stats;
    statistics.showStats(locale)

    # --calculate new population size;
    if locale.EPOCH:
        PRoFIGA = promoterz.supplement.PRoFIGA.calculatePRoFIGA(
            World.genconf.PRoFIGA_beta, locale.EPOCH,
            World.genconf.NBEPOCH,
            locale.EvolutionStatistics[locale.EPOCH-1],
            locale.EvolutionStatistics[locale.EPOCH])

        locale.POP_SIZE += locale.POP_SIZE * PRoFIGA
        minps, maxps = World.genconf.POP_SIZE//2, World.genconf.POP_SIZE * 3
        try:
            locale.POP_SIZE = int(round(max(min(locale.POP_SIZE, maxps), minps)))
        except:
            locale.POP_SIZE = 30
            M="POP_SIZE PROFIGA ERROR;"
            print(M)

    # --filter best inds;
    locale.population[:] = tools.selBest(locale.population, locale.POP_SIZE)



    assert(len(locale.population))
    assert(None not in locale.population)

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
    # --select best individues to procreate
    offspring = evolutionHooks.Tournament(locale.population,
                                    World.genconf._lambda, 2*World.genconf._lambda)
    offspring = [deepcopy(x) for x in offspring] # is deepcopy necessary?

    # --modify and integrate offspring;
    offspring = algorithms.varAnd(offspring, World.tools,
                                  World.genconf.cxpb, World.genconf.mutpb)
    locale.extratools.ageZero(offspring)
    locale.population += offspring

    # --NOW DOESN'T MATTER IF SOME INDIVIDUE LACKS FITNESS VALUES;
    assert(None not in locale.population)

    # --immigrate individual from HallOfFame;
    if random.random() < 0.2:
        locale.population = locale.extratools.ImmigrateHoF(locale.population)

    # --immigrate random number of random individues;
    if random.random() < 0.5:
        locale.population = locale.extratools.ImmigrateRandom( (2,7), locale.population)


    assert(len(locale.population))


    '''
    if FirstEpochOfDataset:
        InitialBestScores.append(Stats['max'])
        Stats['dateRange'] = "%s ~ %s" % (locale.DateRange['from'], locale.DateRange['to'])
    else:
        Stats['dateRange'] = None
    '''

    assert(None not in locale.population)






