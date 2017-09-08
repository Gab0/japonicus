#!/bin/python
import random
import datetime
import calendar

from copy import deepcopy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

from multiprocessing import Pool

from gekkoWrapper import *
#from plotInfo import plotEvolutionSummary

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
    Settings = {
        Strategy:{
            "short": IND[0]//5+1,
            "long": IND[1]//3+10,
            "signal": IND[2]//10+5,
            "interval": IND[3]//3,
            "thresholds": {
                "down": (IND[4]//1.5-50)/40,
                "up": (IND[5]//1.5-5)/40,
                "low": IND[6]//2+10,
                "high": IND[7]//2+45,
                "persistence": IND[8]//25+1,
                "fibonacci": (IND[9]//11+1)/10
            }
        }
    } 
        
    return Settings

def getDateRange(Limits, deltaDAYS=3):
    DateFormat="%Y-%m-%d %H:%M:%S"

    epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime(DateFormat)
    FLms = Limits['from']
    TLms = Limits['to']
    delta=datetime.timedelta(days=deltaDAYS)
    deltams=deltaDAYS * 24 * 60 * 60

    Starting= random.randint(FLms,TLms-deltams)
    DateRange = {
        "from": "%s" % epochToString(Starting),
        "to": "%s" % epochToString(Starting+deltams)
    }

    return DateRange

def Evaluate(DateRange, Individual, Strategy):
    Settings = reconstructTradeSettings(Individual, Strategy)
    Score = runBacktest(Settings, DateRange)
    return Score,

def initInd(Criterion):
    w = Criterion()
    w[:] = createRandomVarList()
    return w

def gekko_generations(NBEPOCH=150, POP_SIZE=30, DDAYS=3):
    
    Strategy= "DEMA" # Strategy to be used;
    DRP = 20 # Date range persistence; Number of subsequent rounds
             # until another time range in dataset is selected;
    _lambda  = 5 # size of offspring generated per epoch;
    cxpb, mutpb = 0.3, 0.5 # Probabilty of crossover and mutation respectively;
    deltaDays=3 # time window of dataset for evaluation
    n_ParallelBacktests = 5

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
    chosenRange = getAvailableDataset()
    print("using candlestick dataset %s" % chosenRange)

    InfoData={}


    print("DEBUG %s" % reconstructTradeSettings([0 for x in range(10)], 'MIN_ VALUES'))
    print("DEBUG %s" % reconstructTradeSettings([100 for x in range(10)], 'MAX_ VALUES'))
          
    while W < NBEPOCH: 
        HallOfFame = tools.HallOfFame(30)


        if not W % DRP: # SELECT NEW DATERANGE;
            if W:
                BestSetting = tools.selBest(POP, 1)[0]
                HallOfFame.insert(BestSetting)
                #print(InfoData)
                #plotEvolutionSummary(InfoData,
                #                     "evolution_%s"% (Strategy))
            DateRange = getDateRange(chosenRange, deltaDAYS=deltaDays)
            print("Loading new date range;")
            print("\t%s" % DateRange)
            for I in POP:
                del I.fitness.values
            toolbox.register("evaluate", Evaluate, DateRange)
        
        individues_to_simulate = [ind for ind in POP if not ind.fitness.valid]
        
        #fitnesses = toolbox.map(toolbox.evaluate, individues_to_simulate)
        to_simulation = [(x[:], x.Strategy) for x in individues_to_simulate]
        fitnesses = parallel.starmap(toolbox.evaluate, to_simulation)
        
        for ind, fit in zip(individues_to_simulate, fitnesses):
            ind.fitness.values = fit

        hof=0
        if HallOfFame.items:
            # casually insert individuals from HallOfFame on population;
            for Q in range(1):
                CHP = deepcopy(choice(HallOfFame))
                POP += [CHP]
                hof+=1
            
        # remove worst individuals from population;
        POP = tools.selBest(POP, len(POP)-_lambda-hof)

        # sort some information to show;
        medScore = sum([I.fitness.values[0] for I in POP])/len(POP)
        bestScore = tools.selBest(POP,1)[0].fitness.values[0]
        print("EPOCH %i:  Medium profit %.3f%%     Best profit %.3f%%" % (W, medScore, bestScore))
        
        InfoData[W] = {
            'best': bestScore,
            'med': medScore
        }
        
        # generate and append offspring in population;
        offspring = algorithms.varOr(POP, toolbox, _lambda, cxpb, mutpb)
        POP += offspring
        #print("POPSIZE %i" % len(POP))
        W+=1
        
    FinalIndividue = tools.selBest(POP, 1)[0]
    print(reconstructTradeSettings(FinalIndividue, FinalIndividue.Settings))

if __name__ == '__main__':
    MODES = ['MACD', 'DEMA', 'RSI', 'PPO']

    for W in range(10):
        GA = gekko_generations()


