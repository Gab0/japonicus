#!/bin/python
from deap import base
from deap import tools

from copy import deepcopy
import random

from .. import parameterOperations

from . import Creator

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

    _Settings = parameterOperations.expandNestedParameters(Settings)

    return _Settings

def getToolbox(Strategy, genconf, Attributes):
    toolbox = base.Toolbox()

    creator = Creator.init(base.Fitness, {'promoterMap': None,
                                          'Strategy': Strategy})
    #creator.create("FitnessMax", base.Fitness, weights=(1.0, 3))

    toolbox.register("mate", pachytene)
    toolbox.register("mutate", mutate)

    PromoterMap = initPromoterMap(Attributes)
    toolbox.register("newind", initInd, creator.Individual, PromoterMap, genconf.chromosome)
    toolbox.register("population", tools.initRepeat, list, toolbox.newind)

    toolbox.register("constructPhenotype", constructPhenotype, Attributes, genconf.chromosome)
    return toolbox

def initPromoterMap(ParameterRanges):
    PRK = list(ParameterRanges.keys())

    Promoters = [ x for x in PRK ]
    space = list(range(120,240))
    random.shuffle(space)

    PromoterValues = [ space.pop() for x in Promoters ]
    PromoterMap = dict(zip(Promoters, PromoterValues))


    #print(ParameterRanges)

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

def clone(Chr): #!!review this
    cut_point = random.randrange(-len(Chr), len(Chr))
    if not cut_point:
        cut_point = 1
    if cut_point > 0:
        new_chr = chr[:cut_point]
    if cut_point < 0:
        new_chr = chr[cut_point:]

    Chr += new+Chr
