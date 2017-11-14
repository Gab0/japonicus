#!/bin/python
import random
from deap import base
from deap import creator
from deap import tools
from copy import deepcopy

import importlib

def PrepareAndEvaluate(constructPhenotype, evaluationMethod, Individual):
    phenotype = constructPhenotype(Individual)
    return evaluationMethod(phenotype)

def selectRepresentationMethod(methodname):
    M = importlib.import_module("promoterz.representation.%s" % methodname)
    return M

def expandNestedParameters(Parameters):
    _Parameters = {}

    for K in Parameters.keys():
        if '.' in K:
            Q = K.split('.')
            cursor = 0
            base = _Parameters
            while cursor < len(Q)-1:
                if not Q[cursor] in base.keys():
                    base[Q[cursor]] = {}
                base = base[Q[cursor]]
                cursor +=1
            base[Q[cursor]] = Parameters[K]
        else:
            _Parameters[K] = Parameters[K]
    return _Parameters

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


