#!/bin/python
from .utils import flattenParameters

def checkPhenotypeParameterIntegrity(TargetParameters, phenotype):
    cmp = [TargetParameters, phenotype]

    cmp = [flattenParameters(x) for x in cmp]
    #print(cmp)
    cmp = [list(x.keys()) for x in cmp]
    #print("%i ---- %i" % (len(cmp[0]), len(cmp[1])))
    for w in cmp[0]:
        if not w in cmp[1]:
            return w
    return None

def checkPhenotypeAttributeRanges(TargetParameters, phenotype, tolerance=0.3):
    cmp = [TargetParameters, phenotype]
    cmp = [flattenParameters(x) for x in cmp]

    for K in cmp[0].keys():
        high_bound = cmp[0][K][1] + (tolerance * abs(cmp[0][K][1]))
        low_bound = cmp[0][K][0]  - (tolerance * abs(cmp[0][K][0]))
        higher = cmp[1][K] > high_bound
        lower = cmp[1][K] < low_bound
        if higher or lower:
            return "%f %s %f" % (low_bound, K, high_bound)
    return None

def validatePopulation(IndividualToSettings, TargetParameters, population):
    ErrMsg = "--destroying invalid citizen--\n\t({ErrType} {ErrParameter})\n"
    for p in range(len(population)):
        phenotype=IndividualToSettings(population[p])

        Err = checkPhenotypeParameterIntegrity(TargetParameters, phenotype)
        if Err:
            print(ErrMsg.format(ErrType='missing parameter', ErrParameter=Err))
            population[p] = None
            continue
        Err = checkPhenotypeAttributeRanges(TargetParameters, phenotype)
        if Err:
            print(ErrMsg.format(ErrType=' invalid values on', ErrParameter=Err))
            population[p] = None

        if not population[p]:
            print(phenotype)
            pass

    population = [x for x in population if x]
    return population

