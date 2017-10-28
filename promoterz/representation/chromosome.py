#!/bin/python
from deap import base
from deap import creator

from promoterz import *


getPromoterFromMap = lambda x: [x[z] for z in list(x.keys())]

def constructPhenotype(stratSettings, chrconf, Individue):
    Settings = {}
    GeneSize=2
    R = lambda V, lim: (lim[1]-lim[0]) * V/(33*chrconf['GeneSize']) + lim[0]
    PromotersPath = {v: k for k, v in Individue.PromoterMap.items()}
    #print(PromotersPath)
    #print(Individue[:])
    Promoters = list(PromotersPath.keys())

    for C in Individue:
        for BP in range(len(C)):
            if C[BP] in Promoters:
                read_window = C[BP+1:BP+1+GeneSize]
                read_window = [ V for V in read_window if type(V) == int and V < 33 ]
                Value = sum(read_window)
                ParameterName = PromotersPath[C[BP]]

                Value = R(Value, stratSettings[ParameterName])

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
    toolbox.register("newind", initInd, creator.Individual, PromoterMap, genconf.chromosome)
    toolbox.register("population", tools.initRepeat, list, toolbox.newind)

    toolbox.register("constructPhenotype", constructPhenotype, Attributes, genconf.chromosome)
    return toolbox

def initPromoterMap(ParameterRanges):
    PRK = list(ParameterRanges.keys())


    Promoters = [x for x in PRK]
    PromoterMap = {}
    for W in Promoters:
        promoter = None
        while not promoter or promoter in PromoterMap:
            promoter = random.randrange(120, 210)
        PromoterMap[W] = promoter

    print(ParameterRanges)
    print(PromoterMap)
    assert(len(PRK) == len(list(PromoterMap.keys())))
    return PromoterMap

def initChromosomes(PromoterMap, chrconf):
    Promoters = getPromoterFromMap(PromoterMap)
    PromoterPerChr = round(len(Promoters)/chrconf['Density'])+1

    _promoters = deepcopy(Promoters)
    Chromosomes = [[] for k in range(PromoterPerChr)]


    while _promoters:
        for c in range(len(Chromosomes)):
            if random.random() < 0.3:
                if _promoters:
                    promoter = _promoters.pop(random.randrange(0,len(_promoters)))
                    Chromosomes[c].append(promoter)
            for G in range(chrconf['GeneSize']):
                Chromosomes[c].append(random.randrange(0, 33))

    return Chromosomes

def initInd(Individual, PromoterMap, chrconf):

    i = Individual()
    i[:] = initChromosomes(PromoterMap, chrconf)
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
