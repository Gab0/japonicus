#!/bin/python
from deap import base
from deap import creator

from promoterz import *


getPromoterFromMap = lambda x: [x[z] for z in list(x.keys())]

def constructPhenotype(stratSettings, Individue):
    Settings = {}

    PromotersPath = {v: k for k, v in Individue.PromoterMap.items()}
    #print(PromotersPath)
    #print(Individue[:])
    Promoters = list(PromotersPath.keys())
    GeneSize=2
    for C in Individue:
        for BP in range(len(C)):
            if C[BP] in Promoters:
                read_window = C[BP+1:BP+1+GeneSize]
                read_window = [ V for V in read_window if type(V) == int and V < 33 ]
                Value = sum(read_window)
                ParameterName = PromotersPath[C[BP]]
                min, max = stratSettings[ParameterName][0], stratSettings[ParameterName][1]
                Value = min + (max-min) * (Value/(33*GeneSize))
                Settings[ParameterName] = Value

    _Settings = {}

    for K in Settings.keys():
        if '.' in K:
            Q = K.split('.')
            if not Q[0] in _Settings.keys():
                _Settings[Q[0]] = {}
            _Settings[Q[0]][Q[1]] = Settings[K]
        else:
            _Settings[K] = Settings[K]

    Settings = {Individue.Strategy: _Settings}
    return Settings

def getToolbox(genconf, Attributes):
    toolbox = base.Toolbox()
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax, PromoterMap=None, Strategy=genconf.Strategy)

    toolbox.register("mate", pachytene)
    toolbox.register("mutate", mutate)

    PromoterMap = initPromoterMap(Attributes)
    toolbox.register("newind", initInd, creator.Individual, PromoterMap)
    toolbox.register("population", tools.initRepeat, list, toolbox.newind)

    toolbox.register("constructPhenotype", constructPhenotype, Attributes)
    return toolbox

def initPromoterMap(ParameterRanges):
    PRK = list(ParameterRanges.keys())
    Promoters = [x for x in PRK]
    PromoterMap = {}
    for W in Promoters:
        promoter = random.randrange(120,150)
        PromoterMap[W] = promoter

    print(ParameterRanges)
    print(PromoterMap)
    assert(len(PRK) == len(list(PromoterMap.keys())))
    return PromoterMap

def initChromosomes(PromoterMap, Density=3):
    Promoters = getPromoterFromMap(PromoterMap)
    PromoterPerChr = round(len(Promoters)/Density)+1

    _promoters = deepcopy(Promoters)
    Chromosomes = [[] for k in range(PromoterPerChr)]


    while _promoters:
        for c in range(len(Chromosomes)):
            if random.random() < 0.3:
                if _promoters:
                    promoter = _promoters.pop(random.randrange(0,len(_promoters)))
                    Chromosomes[c].append(promoter)

            Chromosomes[c].append(random.randrange(0, 33))

    return Chromosomes

def initInd(Individual, PromoterMap):

    i = Individual()
    i[:] = initChromosomes(PromoterMap)
    i.PromoterMap = PromoterMap
    return i

def generateUID():
    Chars = string.ascii_uppercase + string.digits
    UID = ''.join(random.choices(Chars), k=6)
    return UID

def getIndividueMap():
    IndividueMap = {
        'high': generateUID(),
        'low': generateUID(),
        'persistence': generateUID()
        }

    return IndividueMap
