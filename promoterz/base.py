#!/bin/python
import random
from deap import base
from deap import creator
from deap import tools
from copy import deepcopy

getPromoterFromMap = lambda x: [x[z] for z in list(x.keys())]

def getToolbox(genconf, Attributes):
    toolbox = base.Toolbox()
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax, PromoterMap=None, Strategy=genconf.Strategy)

    toolbox.register("mate", pachytene)
    toolbox.register("mutate", mutate)

    PromoterMap = initPromoterMap(Attributes)
    toolbox.register("newind", initInd, creator.Individual, PromoterMap)
    toolbox.register("population", tools.initRepeat, list, toolbox.newind)

    return toolbox

def initPromoterMap(ParameterRanges):
    Promoters = [x for x in list(ParameterRanges.keys())]
    PromoterMap = {}
    for W in Promoters:
        promoter = random.randrange(120,150)
        PromoterMap[W] = promoter


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
                    Chromosomes[c].append(_promoters.pop(0))
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

def chromossomeCrossover(chr1, chr2):
    if len(chr1) != len(chr2):
        top_bottom = 1 if random.random() < 0.5 else -1
        len_diff = abs(len(chr1) - len(chr2))
    else:
        top_bottom = 1
        len_diff = 0

    offset = random.randrange(0, len_diff+1)
    minor = chr1 if len(chr1) < len(chr2) else chr2
    major = chr2 if len(chr1) < len(chr2) else chr1
    cut_point = random.randrange(0, len(minor))

    for k in range(cut_point, len(minor)):
        Buffer = major[k+offset]
        major[k+offset] = minor[k]
        minor[k] = Buffer

def pachytene(ind1, ind2):
    if len(ind1) != len(ind2):
        return

    ind1 = deepcopy(ind1)
    ind2 = deepcopy(ind2)

    ind1[:] = sorted(ind1, key=len)
    ind2[:] = sorted(ind2, key=len)

    childChr = []
    for W in range(len(ind1)):
        chromossomeCrossover(ind1[W], ind2[W])
        childChr.append(random.choice([ind1[W], ind2[W]]))

    return ind1, ind2
def mutate(ind, mutpb=0.001, mutagg=12):
    for C in range(len(ind)):
        for BP in range(len(ind[C])):
            if BP < 100: # case BP is common base value;
                if random.random() < mutpb:
                    ind[C][BP]+=random.choice(range(-mutagg, mutagg))
            else: # case BP is in fact a promoter;
                pass

    return ind,
def clone(Chr):
    cut_point = random.randrange(-len(Chr), len(Chr))
    if not cut_point:
        cut_point = 1
    if cut_point > 0:
        new_chr = chr[:cut_point]
    if cut_point < 0:
        new_chr = chr[cut_point:]

    Chr += new+Chr

def reconstructTradeSettings(Individue):
    Settings = {}

    PromotersPath = {v: k for k, v in Individue.PromoterMap.items()}
    #print(PromotersPath)
    #print(Individue[:])
    Promoters = list(PromotersPath.keys())
    for C in Individue:
        for BP in range(len(C)):
            if C[BP] in Promoters:
                read_window = C[BP+1:BP+3]
                read_window = [V for V in read_window if type(V) == int and V < 33]
                Value = sum(read_window)
                Settings[PromotersPath[C[BP]]] = Value

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

