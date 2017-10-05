#!/bin/python

def checkDifference(constructPhenotype, indA, indB):
    indA, indB = constructPhenotype(indA), constructPhenotype(indB)
    score = 0
    for w in indA.keys():

        if indA[w] != indB[w]:
            score +=1

    return score
