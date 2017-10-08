#!/bin/python
from deap import tools
from copy import deepcopy
import random
from deap import algorithms
import promoterz
def standard_loop(locale):
    assert(len(locale.population))
    if not locale.EPOCH % 15:# SEND BEST IND TO HoF;
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
    # --hall of fame immigration;
    if random.random() < 0.2:
        locale.population = locale.extratools.ImmigrateHoF(locale.population)

    # --randomic immigration;
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

    locale.population=promoterz.validation.validatePopulation(
        locale.tools.constructPhenotype,
        {locale.genconf.Strategy: locale.TargetParameters},
        locale.population)

    # --evaluate individuals;
    nb_evaluated=promoterz.evaluatePopulation(locale.population,
                                              locale.extratools.evaluate,
                                              locale.parallel)


    assert(len(locale.population))
    # --get proper evolution statistics;
    Stats=locale.stats.compile(locale.population)

    # --calculate new POPSIZE;
    if locale.EPOCH:
        PRoFIGA = promoterz.supplement.PRoFIGA.calculatePRoFIGA(
            locale.genconf.PRoFIGA_beta, locale.EPOCH,
            locale.genconf.NBEPOCH,
            locale.EvolutionStatistics[locale.EPOCH-1],
            Stats)
        locale.POP_SIZE += max(int(round( locale.POP_SIZE * PRoFIGA )), locale.genconf.POP_SIZE//2)

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
    Stats['dateRange'] = None
    Stats['maxsize'] = locale.POP_SIZE
    Stats['size'] = len(locale.population)
    locale.EvolutionStatistics[locale.EPOCH] = Stats

    LOGPATH ="%s/%s" % (locale.globalconf.save_dir, locale.globalconf.log_name)
    promoterz.statistics.write_evolution_logs(locale.EPOCH,
                                              Stats, LOGPATH)


    # show information;
    print("EPOCH %i/%i\t&%i" % (locale.EPOCH, locale.genconf.NBEPOCH, nb_evaluated))
    statnames = [ 'max', 'avg', 'min', 'std', 'size', 'maxsize' ]

    statText = ""
    for s in range(len(statnames)):
        SNAME = statnames[s]
        SVAL = Stats[SNAME]
        statText += "%s" % promoterz.statistics.statisticsNames[SNAME]
        if not SVAL % 1:
            statText += " %i\t" % SVAL
        else:
            statText += " %.3f\t" % SVAL
        if s % 2:
            statText += '\n'
    print(statText)
    print('')



    bestScore = Stats['max']
    Deviation = Stats['std']
    assert(None not in locale.population)

    #print("POPSIZE %i" % len(locale.population))

    # --population ages
    qpop=len(locale.population)
    locale.population=locale.extratools.populationAges(locale.population, Stats)
    wpop=len(locale.population)
    print('elder %i' % (qpop-wpop))

    assert(len(locale.population))
    assert(None not in locale.population)


