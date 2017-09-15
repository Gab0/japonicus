#!/bin/python
import random
import datetime
import calendar
import json


from copy import deepcopy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import numpy as np

from multiprocessing import Pool

from gekkoWrapper import *
from coreFunctions import Evaluate, getRandomDateRange,\
    stratSettingsProofOfViability, pasteSettingsToUI
from Settings import getSettings
#from plotInfo import plotEvolutionSummary

def logInfo(message, filename="evolution.log"):
    F=open(filename, 'a+')
    F.write(message)
    print(message)
    F.close()
    
def progrBarMap(funct, array):
    l = len(array)
    result = []
    for w in range(len(array)):
        result.append(funct(array[w]))
        print("\r\tevaluating %i:\t%.2f%%" % (l, ((w+1)/l*100)), end='')
    print('\r\n')

    return result

def getRandomTradeSettings():
    pass

def createRandomVarList(SZ=10):
    VAR_LIST = [random.randrange(0,100) for x in range(SZ)]
    return VAR_LIST

def reconstructTradeSettings(IND, Strategy):
    R = lambda V, lim: ((lim[1]-lim[0])/100) * V + lim[0]
    Settings = {
        Strategy:{
            "short": R( IND[0], (1, 20) ),
            "long": R( IND[1], (10, 43) ),
            "signal": R( IND[2], (5, 15) ),
            "interval": R( IND[3], (1, 26) ),
            "thresholds": {
                "down": R( IND[4], (-0.85, 0.25) ),
                "up": R( IND[5], (-0.85, 1.02) ),
                "low": R( IND[6], (10, 60) ),
                "high": R( IND[7], (45, 95) ),
                "persistence": R( IND[8], (1, 15)),
                "fibonacci": R( IND[9], (0.1, 1))
            }
        }
    } 
        
    return Settings

def initInd(Criterion):
    w = Criterion()
    w[:] = createRandomVarList()
    return w

def gekko_generations(Strategy, NBEPOCH=300, POP_SIZE=30):
    # SETTINGS;############################
    settings=getSettings()['generations']

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
    
    POP = toolbox.population(n=POP_SIZE)
    W=0
    availableDataRange = getAvailableDataset()
    print("using candlestick dataset %s" % availableDataRange)
    print("%s strategy;" % Strategy)
    
    InfoData={}
    
    #firePaperTrader(reconstructTradeSettings(POP[0], POP[0].Strategy), "poloniex",
    #                "USDT", "BTC")
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    InitialBestScores, FinalBestScores = [], []
    FirstEpochOfDataset = False
    Stats = None
    settings_debug_min = reconstructTradeSettings([0 for x in range(10)], 'MIN_ VALUES')
    settings_debug_max = reconstructTradeSettings([100 for x in range(10)], 'MAX_ VALUES')
    
    print("DEBUG %s" % json.dumps(settings_debug_min, indent=2))
    print("DEBUG %s" % json.dumps(settings_debug_max, indent=2))
          
    while W < NBEPOCH: 
        HallOfFame = tools.HallOfFame(30)
        bestScore = 0
        Deviation = 0
        
        Z = not W % DRP and bestScore > 0.3 and not Deviation
        K = not W % (DRP*3)
        if Z or K: # SELECT NEW DATERANGE;
            if W:# SEND BEST IND TO HoF;
                BestSetting = tools.selBest(POP, 1)[0]
                HallOfFame.insert(BestSetting)
                #print(InfoData)
                #plotEvolutionSummary(InfoData,
                #                     "evolution_%s"% (Strategy))
                FinalBestScores.append(Stats['max'])
            DateRange = getRandomDateRange(availableDataRange, deltaDays)
            print("Loading new date range;")
            print("\t%s to %s" % (DateRange['from'], DateRange['to']))
            for I in range(len(POP)):
                del POP[I].fitness.values
            toolbox.register("evaluate", Evaluate, DateRange)
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
        print("EPOCH %i/%i" % (W, NBEPOCH)) 
        print("Average profit %.3f%%\tDeviation %.3f" % (Stats['avg'],Stats['std']))
        print("Maximum profit %.3f%%\tMinimum profit %.3f%%" % (Stats['max'],Stats['min']))
        print("")

        # log statistcs;
        InfoData[W] = Stats
        if FirstEpochOfDataset:
            InitialBestScores.append(Stats['max'])
            FirstEpochOfDataset = False
            
        bestScore = Stats['max']
        Deviation = Stats['std']
        # generate and append offspring in population;
        offspring = algorithms.varOr(POP, toolbox, settings['_lambda'],
                                     settings['cxpb'], settings['mutpb'])

        POP[:] = tools.selBest(POP+offspring, POP_SIZE)

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
    
