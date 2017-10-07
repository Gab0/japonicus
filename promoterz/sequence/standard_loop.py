#!/bin/python
from deap import tools
from copy import deepcopy
def standard_loop(locale, Strategy, GenerationMethod='standard'):

    if not locale.EPOCH % 15:# SEND BEST IND TO HoF;
            BestSetting = tools.selBest(locale.population, 1)[0]
            locale.HallOfFame.insert(BestSetting)
            #print(EvolutionStatistics)

            #FinalBestScores.append(Stats['max'])

            print("Loading new date range;")

            print("\t%s to %s" % (DateRange['from'], DateRange['to']))
            for I in range(len(POP)):
                del POP[I].fitness.values
            toolbox.register("evaluate", coreFunctions.Evaluate,
                                 GenerationMethod.constructPhenotype, DateRange)
            FirstEpochOfDataset = True
            bestScore = 0

    assert(None not in POP)
    # --hall of fame immigration;
    if random.random() < 0.2:
        locale.population = locale.tools.ImmigrateHoF(locale.population)

    # --randomic immigration;
    if random.random() < 0.5:
        locale.population = locale.tools.ImmigrateRandom((2,7), locale.population)


    assert(len(POP))
    # --select best individues to procreate
    offspring = tools.selTournament(POP, genconf._lambda, 2*genconf._lambda)
    offspring = [deepcopy(x) for x in offspring] # is deepcopy necessary?
    
    # --modify and integrate offspring;
    offspring = algorithms.varAnd(offspring, toolbox,
                                  genconf.cxpb, genconf.mutpb)
    locale.tools.zero(offspring)
    locale.population += offspring
    

    locale.population=promoterz.validation.validatePopulation(GenerationMethod.constructPhenotype,
                                                {Strategy:TargetParameters}, POP)
    # --evaluate individuals;
    nb_evaluated=promoterz.evaluatePopulation(locale.population, toolbox.evaluate, parallel)


    # --get proper evolution statistics;
    Stats=locale.stats.compile(locale.population)

    # --calculate new POPSIZE;
    if W and not FirstEpochOfDataset:
        PRoFIGA = promoterz.supplement.PRoFIGA.calculatePRoFIGA(
            locale.genconf.PRoFIGA_beta, locale.EPOCH,
            locale.genconf.NBEPOCH,
            locale.EvolutionStatistics[W-1],
            Stats)
        locale.POP_SIZE += int(round( POP_SIZE * PRoFIGA ))

    # --filter best inds;
    locale.population[:] = tools.selBest(locale.population, locale.POP_SIZE)

    # --log statistcs;
    if FirstEpochOfDataset:
        InitialBestScores.append(Stats['max'])
        Stats['dateRange'] = "%s ~ %s" % (DateRange['from'], DateRange['to'])
    else:
        Stats['dateRange'] = None

    Stats['maxsize'] = POP_SIZE
    Stats['size'] = len(POP)
    EvolutionStatistics[W] = Stats
    coreFunctions.write_evolution_logs(W, Stats)

    # show information;
    print("EPOCH %i/%i\t&%i" % (W, genconf.NBEPOCH, nb_evaluated))
    statnames = [ 'max', 'avg', 'min', 'std', 'size', 'maxsize' ]

    statText = ""
    for s in range(len(statnames)):
        SNAME = statnames[s]
        SVAL = Stats[SNAME]
        statText += "%s" % coreFunctions.statisticsNames[SNAME]
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
    assert(None not in POP)

    #print("POPSIZE %i" % len(POP))

    # --population ages
    qpop=len(POP)
    locale.population=locale.tools.populationAges(locale.population, Stats)
    wpop=len(POP)
    print('elder %i' % (qpop-wpop))

    assert(len(POP))
    assert(None not in POP)


