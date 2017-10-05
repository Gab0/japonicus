#!/bin/python

from promoterz import *

def checkDifference(constructPhenotype, indA, indB):

    cmp = [indA, indB]
    cmp = [constructPhenotype(x) for x in cmp]
    cmp = [flattenParameters(x) for x in cmp]

    score = 0
    for w in cmp[0].keys():

        if cmp[0][w] != cmp[1][w]:
            score +=1

    return score

