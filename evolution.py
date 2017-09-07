#!/bin/python
import random
import datetime
import calendar

from copy import deepcopy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms

from gekkoWrapper import *
from plotInfo import plotEvolutionSummary

def progrBarMap(funct, array):
    l = len(array)
    result = []
    for w in range(len(array)):
        result.append(funct(array[w]))
        print("\r\tevaluating %i:\t%.2f%%" % (l, ((w+1)/l*100)), end='')
    print('\r\n')

    return result

def getRandomTradeSettings():

    sC = '''
{"%s":{
    "short": %i,
    "long": %i,
    "signal": %i,
    "interval": %i,
    "thresholds": {
    "down": %.3f,
    "up": %.3f,
    "low": %i,
    "high": %i,
    "persistence": %i,
    "fibonacci": %.1f
    }
    }
    }
''' % (choice(MODES),
       randrange(2,20),
       randrange(14,44),
       randrange(5,15),
       randrange(4,28),
       randrange(-50, 5)/40,
       randrange(-5, 50)/40,
       randrange(10,50),
       randrange(45,95),
       randrange(1,4),
       randrange(1,6)/10)
    
    return eval(sC)

def createRandomVarList(SZ=10):
    VAR_LIST = [random.randrange(0,100) for x in range(SZ)]
    return VAR_LIST

def reconstructTradeSettings(VAR_LIST):
    sC =\
 '''{"%s":{
    "short": %i,
    "long": %i,
    "signal": %i,
    "interval": %i,
    "thresholds": {
    "down": %.3f,
    "up": %.3f,
    "low": %i,
    "high": %i,
    "persistence": %i,
    "fibonacci": %.1f
    }
    }
    }''' % ("DEMA",
            VAR_LIST[0]//5,
            VAR_LIST[1]//3+10,
            VAR_LIST[2]//10+5,
            VAR_LIST[3]//3,
            (VAR_LIST[4]//1.5-50)/40,
            (VAR_LIST[5]//1.5-5)/40,
            VAR_LIST[6]//2+10,
            VAR_LIST[7]//2+45,
            VAR_LIST[8]//25+1,
            (VAR_LIST[9]//11+1)/10)
        
    return eval(sC)

def getDateRange(Limits, deltaDAYS=3):
    DateFormat="%Y-%m-%d %H:%M:%S"
    print(Limits)
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

def Evaluate(DateRange, Individual):
    Settings = reconstructTradeSettings(Individual)
    Score = runBacktest(Settings, DateRange)
    return Score,

def initInd(Criterion):
    w = Criterion()
    w[:] = createRandomVarList()
    return w

def gekkoGA(NBEPOCH=150, POP_SIZE=30, DDAYS=3):
    toolbox = base.Toolbox()
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Criterion", list, fitness=creator.FitnessMax)
    toolbox.register("newCriterion", initInd, creator.Criterion)
    
    toolbox.register("population", tools.initRepeat, list,  toolbox.newCriterion)

    toolbox.register("map", progrBarMap)
    
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=10, up=10, indpb=0.2)
    
    POP = toolbox.population(n=POP_SIZE)
    W=0
    chosenRange = getAvailableDataset()
    print(chosenRange)

    DRP = 20 # Date range persistence; Number of subsequent rounds
             # until another time range in dataset is selected;
    _lambda  = 5, 0.3, 0.5 # N of offspring generated per epoch;
    cxpb, mutpb = 0.3, 0.5 # Probabilty of crossover and mutation respectively;

    InfoData={}
    while W < NBEPOCH:
        HallOfFame = tools.HallOfFame(30)


        if not W % DRP: # SELECT NEW DATERANGE;
            if W:
                BestSetting = tools.selBest(POP, 1)[0]
                HallOfFame.insert(BestSetting)
                InfoData.update({W:BestSetting.fitness.values[0]})
                plotEvolutionSummary(InfoData, "evolution_%s"% (W,Strategy))
            DateRange = getDateRange(chosenRange)
            print("Loading new date range;")
            print("\t%s" % DateRange)
            for I in POP:
                del I.fitness.values
            toolbox.register("evaluate", Evaluate, DateRange)
        
        individues_to_simulate = [ind for ind in POP if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, individues_to_simulate)
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
        print("Scores for epoch:  Medium profit %.3f%%     Best profit %.3f%%" % (medScore, bestScore))

        # generate and append offspring in population;
        offspring = algorithms.varOr(POP, toolbox, _lambda, cxpb, mutpb)
        POP += offspring
        print("POPSIZE %i" % len(POP))
        
        W+=1
    
    FinalIndividue = tools.selBest(POP, 1)[0]
    print(reconstructTradeSettings(FinalIndividue))


if __name__ == '__main__':
    MODES = ['MACD', 'DEMA', 'RSI', 'PPO']

    for W in range(10):
        GA = gekkoGA()


