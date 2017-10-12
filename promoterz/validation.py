#!/bin/python
from .utils import flattenParameters

def checkPhenotypeIntegrity(Settings, TargetParameters):
    cmp = [TargetParameters, Settings]

    cmp = [flattenParameters(x) for x in cmp]
    #print(cmp)
    cmp = [list(x.keys()) for x in cmp]
    for w in cmp[0]:
        if not w in cmp[1]:
            return False
    return True

def checkPhenotypeAttributeRanges(TargetParameters, phenotype):
    cmp = [TargetParameters, phenotype]
    cmp = [flattenParameters(x) for x in cmp]

    for K in cmp[0].keys():
        higher = cmp[1][K] > cmp[0][K][1]
        lower = cmp[1][K] < cmp[0][K][0]
        if higher or lower:
            return False
    return True

def validatePopulation(IndividualToSettings, TargetParameters, population):

    for p in range(len(population)):
        phenotype=IndividualToSettings(population[p])
        if not(checkPhenotypeIntegrity(phenotype, TargetParameters)):
            population[p] = None
        elif not (checkPhenotypeAttributeRanges(TargetParameters, phenotype)):
            population[p] = None

        if not population[p]:
            print('--destroying invalid citizen--')
            print(phenotype)
            
    population = [x for x in population if x]
    return population
