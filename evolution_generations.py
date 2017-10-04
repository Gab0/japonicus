#!/bin/python
import json
import random
import promoterz

from copy import deepcopy
from gekkoWrapper import getAvailableDataset
from coreFunctions import Evaluate, getRandomDateRange,\
    stratSettingsProofOfViability, pasteSettingsToUI,\
    getStatisticsMeter,\
    logInfo, write_evolution_logs

from Settings import getSettings

from multiprocessing import Pool

from deap import tools
from deap import algorithms
from deap import base

def gekko_generations(Strategy, GenerationMethod='standard'):

    genconf=getSettings('generations')
    conf=getSettings('global')
    stratattr=getSettings()['strategies'][Strategy]
    # GENERATION METHOD SELECTION;
    # to easily employ various GA algorithms,
    # this base EPOCH processor loads a GenerationMethod file,
    # which should contain a genToolbox function to generate
    # fully working DEAP toolbox, and a reconstructTradeSettings
    # function to convert parameters from individue to usable strategy Settings;
    # Check promoterz/representation;

    GenerationMethod = promoterz.selectRepresentationMethod(GenerationMethod)
    toolbox = GenerationMethod.getToolbox(genconf, stratattr)

    parallel = Pool(genconf.ParallelBacktests)

    POP = toolbox.population(n=genconf.POP_SIZE)
    W=0
    availableDataRange = getAvailableDataset(exchange_source=genconf.dataset_source)
    print("using candlestick dataset %s" % availableDataRange)
    print("%s strategy;" % Strategy)

    EvolutionStatistics={}

    stats = getStatisticsMeter()

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

            DateRange = getRandomDateRange(availableDataRange, genconf.deltaDays)
            print("Loading new date range;")

            print("\t%s to %s" % (DateRange['from'], DateRange['to']))
            for I in range(len(POP)):
                del POP[I].fitness.values
            toolbox.register("evaluate", Evaluate,
                             GenerationMethod.constructPhenotype, DateRange)
            FirstEpochOfDataset = True
            bestScore = 0



        # --hall of fame immigration;
        if random.random() < 0.2:
            POP = coreTools.ImmigrateHoF(POP)


        # --randomic immigration;
        if random.random() < 0.5:
            POP = coreTools.ImmigrateRandom(POP)


        # --evaluate individuals;
        promoterz.evaluatePopulation(POP, toolbox.evaluate, parallel)

        # --get proper evolution statistics;
        Stats=stats.compile(POP)

        # show information;
        print("EPOCH %i/%i" % (W, genconf.NBEPOCH)) 
        print("Average profit %.3f%%\tDeviation %.3f" % (Stats['avg'],Stats['std']))
        print("Maximum profit %.3f%%\tMinimum profit %.3f%%" % (Stats['max'],Stats['min']))
        print("")


        if FirstEpochOfDataset:
            InitialBestScores.append(Stats['max'])
            Stats['dateRange'] = "%s ~ %s" % (DateRange['from'], DateRange['to'])
        else:
            Stats['dateRange'] = None

        # --log statistcs;
        EvolutionStatistics[W] = Stats
        write_evolution_logs(W, Stats)

        bestScore = Stats['max']
        Deviation = Stats['std']

        # --select best individues to procreate
        offspring = tools.selTournament(POP, genconf._lambda, 2*genconf._lambda)
        offspring = [deepcopy(x) for x in offspring]

        # --modify and integrate offspring;
        offspring = algorithms.varAnd(offspring, toolbox,
                                     genconf.cxpb, genconf.mutpb)

        promoterz.evaluatePopulation(offspring, toolbox.evaluate, parallel)
        POP += offspring

        # --filter best inds;
        POP[:] = tools.selBest(POP, genconf.POP_SIZE)

        #print("POPSIZE %i" % len(POP))
        W+=1

    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    FinalBestScores.append(Stats['max'])
    FinalIndividue = tools.selBest(POP, 1)[0]
    FinalIndividueSettings = GenerationMethod.constructPhenotype(FinalIndividue)

    Show = json.dumps(FinalIndividueSettings, indent=2)
    logInfo("~" * 18)
    for S in range(len(FinalBestScores)):
        logInfo("Candlestick Set %i: \n\n" % (S+1)+\
                "EPOCH ONE BEST PROFIT: %.3f\n" % InitialBestScores[S] +\
                "FINAL EPOCH BEST PROFIT: %.3f\n" % FinalBestScores[S])

        
    print("Settings for Gekko config.js:")
    print(Show)
    print("Settings for Gekko --ui webpage")
    logInfo(pasteSettingsToUI(FinalIndividueSettings))

    print("\nRemember to check MAX and MIN values for each parameter.")
    print("\tresults may improve with extended ranges.")
    
    print("Testing Strategy:\n")
    Vv=stratSettingsProofOfViability(FinalIndividueSettings, availableDataRange)
    Vv = "GOOD STRAT" if Vv else "SEEMS BAD"
    logInfo(Vv)
    print("\t\t.RUN ENDS.")

    return FinalIndividueSettings, EvolutionStatistics
