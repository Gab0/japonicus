#!/bin/python
import json
import random
import promoterz

from copy import deepcopy
from gekkoWrapper import getAvailableDataset

import coreFunctions


from promoterz.supplement.geneticDivergence import *
from promoterz.supplement.age import *
from Settings import getSettings

from multiprocessing import Pool

from deap import tools
from deap import algorithms
from deap import base

def gekko_generations(Strategy, GenerationMethod='standard'):

    genconf=getSettings('generations')
    conf=getSettings('global')
    TargetParameters=getSettings()['strategies'][Strategy]
    # GENERATION METHOD SELECTION;
    # to easily employ various GA algorithms,
    # this base EPOCH processor loads a GenerationMethod file,
    # which should contain a genToolbox function to generate
    # fully working DEAP toolbox, and a reconstructTradeSettings
    # function to convert parameters from individue to usable strategy Settings;
    # Check promoterz/representation;

    genconf.Strategy = Strategy # ovrride strat defined on settings if needed;
    GenerationMethod = promoterz.selectRepresentationMethod(GenerationMethod)
    toolbox = GenerationMethod.getToolbox(genconf, TargetParameters)

    ageTools = promoterz.supplement.age.getToolbox(genconf.ageBoundaries)
    parallel = Pool(genconf.ParallelBacktests)

    POP = toolbox.population(n=genconf.POP_SIZE)
    W=0
    availableDataRange = getAvailableDataset(exchange_source=genconf.dataset_source)
    print("using candlestick dataset %s" % availableDataRange)
    print("%s strategy;" % Strategy)

    EvolutionStatistics={}

    stats = coreFunctions.getStatisticsMeter()

    InitialBestScores, FinalBestScores = [], []
    FirstEpochOfDataset = False
    Stats = None
    # settings_debug_min = GenerationMethod.constructPhenotype([0 for x in range(10)], Strategy)
    # settings_debug_max = GenerationMethod.constructPhenotype([100 for x in range(10)], Strategy)

    # print("DEBUG %s" % json.dumps(settings_debug_min, indent=2))
    # print("DEBUG %s" % json.dumps(settings_debug_max, indent=2))

    HallOfFame = tools.HallOfFame(30)
    bestScore = 0
    Deviation = 0

    coreTools = promoterz.getEvolutionToolbox(HallOfFame, toolbox.population)

    print("evaluated parameters ranges %s" % coreFunctions.flattenParameters(TargetParameters))
    while W < genconf.NBEPOCH:

        FirstEpochOfDataset = False

        # -- periodically change environment
        Z = not W % genconf.DRP and bestScore > 0.3 and not Deviation
        K = not W % (genconf.DRP*3)
        if Z or K: # SELECT NEW DATERANGE;
            if W:# SEND BEST IND TO HoF;
                BestSetting = tools.selBest(POP, 1)[0]
                HallOfFame.insert(BestSetting)
                #print(EvolutionStatistics)

                FinalBestScores.append(Stats['max'])

            DateRange = coreFunctions.getRandomDateRange(availableDataRange, genconf.deltaDays)
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
            POP = coreTools.ImmigrateHoF(POP)

        # --randomic immigration;
        if random.random() < 0.5:
            POP = coreTools.ImmigrateRandom(POP)


        # --select best individues to procreate
        offspring = tools.selTournament(POP, genconf._lambda, 2*genconf._lambda)
        offspring = [deepcopy(x) for x in offspring]

        # --modify and integrate offspring;
        offspring = algorithms.varAnd(offspring, toolbox,
                                      genconf.cxpb, genconf.mutpb)
        ageTools.zero(offspring)
        POP += offspring


        POP=coreFunctions.validatePopulation(GenerationMethod.constructPhenotype,
                                        {Strategy:TargetParameters}, POP)
        # --evaluate individuals;
        nb_evaluated=promoterz.evaluatePopulation(POP, toolbox.evaluate, parallel)
        # --filter best inds;
        POP[:] = tools.selBest(POP, genconf.POP_SIZE)

        # --get proper evolution statistics;
        Stats=stats.compile(POP)

        # show information;
        print("EPOCH %i/%i\t&%i" % (W, genconf.NBEPOCH, nb_evaluated))
        statnames = ['max', 'avg', 'min', 'std']

        statText = ""
        for s in range(len(statnames)):
            SNAME = statnames[s]
            statText += "%s %.3f%%\t" % (coreFunctions.statisticsNames[SNAME], Stats[SNAME])
            if s % 2:
                statText += '\n'
        print(statText)
        print('')

        if FirstEpochOfDataset:
            InitialBestScores.append(Stats['max'])
            Stats['dateRange'] = "%s ~ %s" % (DateRange['from'], DateRange['to'])
        else:
            Stats['dateRange'] = None

        # --log statistcs;
        EvolutionStatistics[W] = Stats
        coreFunctions.write_evolution_logs(W, Stats)

        bestScore = Stats['max']
        Deviation = Stats['std']
        assert(None not in POP)

        #print("POPSIZE %i" % len(POP))
        # --population ages
        qpop=len(POP)
        POP=ageTools.populationAges(POP, Stats['avg'])
        wpop=len(POP)
        print('elder %i' % (qpop-wpop))
        assert(None not in POP)
        W+=1

    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    FinalBestScores.append(Stats['max'])
    FinalIndividue = tools.selBest(POP, 1)[0]
    FinalIndividueSettings = GenerationMethod.constructPhenotype(FinalIndividue)

    Show = json.dumps(FinalIndividueSettings, indent=2)
    coreFunctions.logInfo("~" * 18)

    for S in range(len(FinalBestScores)):
        coreFunctions.logInfo("Candlestick Set %i: \n\n" % (S+1)+\
                "EPOCH ONE BEST PROFIT: %.3f\n" % InitialBestScores[S] +\
                "FINAL EPOCH BEST PROFIT: %.3f\n" % FinalBestScores[S])


    print("Settings for Gekko config.js:")
    print(Show)
    print("Settings for Gekko --ui webpage")
    coreFunctions.logInfo(coreFunctions.pasteSettingsToUI(FinalIndividueSettings))

    print("\nRemember to check MAX and MIN values for each parameter.")
    print("\tresults may improve with extended ranges.")

    print("Testing Strategy:\n")
    Vv=coreFunctions.stratSettingsProofOfViability(FinalIndividueSettings, availableDataRange)
    Vv = "GOOD STRAT" if Vv else "SEEMS BAD"
    coreFunctions.logInfo(Vv)
    print("\t\t.RUN ENDS.")

    return FinalIndividueSettings, EvolutionStatistics
