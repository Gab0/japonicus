#!/bin/python
import random
import json
import os

from copy import deepcopy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import numpy as np

from multiprocessing import Pool

from gekkoWrapper import *
from coreFunctions import Evaluate, getRandomDateRange,\
    stratSettingsProofOfViability, pasteSettingsToUI,\
    getStatisticsMeter,\
    logInfo, write_evolution_logs

from Settings import getSettings
#from plotInfo import plotEvolutionSummary

def reconstructTradeSettings(IND, Strategy):
    # THIS FUNCTION IS UGLYLY WRITTEN; USE WITH CAUTION;
    # (still works :})
    R = lambda V, lim: ((lim[1]-lim[0])/100) * V + lim[0]
    stratSettings = getSettings()['strategies'][Strategy]
    Settings = {
        Strategy:{}
        }
    i=0
    for K in stratSettings.keys():
        Value = R(IND[i], stratSettings[K])
        if '.' in K:
            K=K.split('.')
            if not K[0] in list(Settings[Strategy].keys()):
                Settings[Strategy][K[0]] = {}
            Settings[Strategy][K[0]][K[1]] = Value
        else:
            Settings[Strategy][K] = Value
        i+=1

    return Settings


def progrBarMap(funct, array):
    l = len(array)
    result = []
    for w in range(len(array)):
        result.append(funct(array[w]))
        print("\r\tevaluating %i:\t%.2f%%" % (l, (w+1)/l*100), end='')
    print('\r\n')

    return result

def getRandomTradeSettings():
    pass

def createRandomVarList(SZ=10):
    VAR_LIST = [random.randrange(0,100) for x in range(SZ)]
    return VAR_LIST



def initInd(Criterion):
    w = Criterion()
    w[:] = createRandomVarList()
    return w

def gekko_generations(Strategy):
    # SETTINGS;############################
    genconf=getSettings('generations')

    DRP = 10 # Date range persistence; Number of subsequent rounds
             # until another time range in dataset is selected;
    _lambda  = 5 # size of offspring generated per epoch;
    cxpb, mutpb = 0.2, 0.8 # Probabilty of crossover and mutation respectively;
    deltaDays=21 # time window of dataset for evaluation
    n_ParallelBacktests = 5
    #######################################
    parallel = Pool(n_ParallelBacktests)
    
    toolbox = base.Toolbox()
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Criterion", list,
                   fitness=creator.FitnessMax, Strategy=Strategy)
    toolbox.register("newCriterion", initInd, creator.Criterion)
    
    toolbox.register("population", tools.initRepeat, list,  toolbox.newCriterion)

    toolbox.register("map", progrBarMap)
    
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=10, up=10, indpb=0.2)
    
    POP = toolbox.population(n=genconf.POP_SIZE)
    W=0
    availableDataRange = getAvailableDataset()
    print("using candlestick dataset %s" % availableDataRange)
    print("%s strategy;" % Strategy)
    
    EvolutionStatistics={}
    
    #firePaperTrader(reconstructTradeSettings(POP[0], POP[0].Strategy), "poloniex",
    #                "USDT", "BTC")
    stats = getStatisticsMeter()

    InitialBestScores, FinalBestScores = [], []
    FirstEpochOfDataset = False
    Stats = None
    settings_debug_min = reconstructTradeSettings([0 for x in range(10)], Strategy)
    settings_debug_max = reconstructTradeSettings([100 for x in range(10)], Strategy)
    
    print("DEBUG %s" % json.dumps(settings_debug_min, indent=2))
    print("DEBUG %s" % json.dumps(settings_debug_max, indent=2))
          
    while W < genconf.NBEPOCH: 
        HallOfFame = tools.HallOfFame(30)
        bestScore = 0
        Deviation = 0
        
        Z = not W % DRP and bestScore > 0.3 and not Deviation
        K = not W % (DRP*3)
        if Z or K: # SELECT NEW DATERANGE;
            if W:# SEND BEST IND TO HoF;
                BestSetting = tools.selBest(POP, 1)[0]
                HallOfFame.insert(BestSetting)
                #print(EvolutionStatistics)
                #plotEvolutionSummary(EvolutionStatistics,
                #                     "evolution_%s"% (Strategy))
                FinalBestScores.append(Stats['max'])
            DateRange = getRandomDateRange(availableDataRange, deltaDays)
            print("Loading new date range;")
            print("\t%s to %s" % (DateRange['from'], DateRange['to']))
            for I in range(len(POP)):
                del POP[I].fitness.values
            toolbox.register("evaluate", Evaluate, reconstructTradeSettings, DateRange)
            FirstEpochOfDataset = True
            
        if random.random() < 0.2 and HallOfFame.items:
            # casually insert individuals from HallOfFame on population;
            for Q in range(1):
                CHP = deepcopy(random.choice(HallOfFame))
                del CHP.fitness.values
                POP += [CHP]

        if random.random() < 0.5:
            # should have built the wall;
            nb = random.randint(1,9)
            POP += toolbox.population(nb)
            
        individues_to_simulate = [ind for ind in POP if not ind.fitness.valid]
        #fitnesses = toolbox.map(toolbox.evaluate, individues_to_simulate)
        to_simulation = [ (x[:], x.Strategy) for x in individues_to_simulate ]
        fitnesses = parallel.starmap(toolbox.evaluate, to_simulation)
        
        for ind, fit in zip(individues_to_simulate, fitnesses):
            ind.fitness.values = fit

        # get proper evolution statistics; #TBD
        Stats=stats.compile(POP)


            

        # show information;
        print("EPOCH %i/%i" % (W, genconf.NBEPOCH)) 
        print("Average profit %.3f%%\tDeviation %.3f" % (Stats['avg'],Stats['std']))
        print("Maximum profit %.3f%%\tMinimum profit %.3f%%" % (Stats['max'],Stats['min']))
        print("")

        # log statistcs;
        EvolutionStatistics[W] = Stats

        write_evolution_logs(W, Stats)
        if FirstEpochOfDataset:
            InitialBestScores.append(Stats['max'])
            FirstEpochOfDataset = False
            
        bestScore = Stats['max']
        Deviation = Stats['std']
        # generate and append offspring in population;
        offspring = algorithms.varOr(POP, toolbox, genconf._lambda,
                                     genconf.cxpb, genconf.mutpb)

        POP[:] = tools.selBest(POP+offspring, genconf.POP_SIZE)

        #print("POPSIZE %i" % len(POP))
        W+=1

    # RUN ENDS. SELECT INDIVIDUE, LOG AND PRINT STUFF;
    FinalBestScores.append(Stats['max'])
    FinalIndividue = tools.selBest(POP, 1)[0]
    FinalIndividueSettings = reconstructTradeSettings(FinalIndividue,
                                                      FinalIndividue.Strategy)
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
