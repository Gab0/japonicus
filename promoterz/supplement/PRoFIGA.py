#!/bin/python

def calculatePRoFIGA(beta, EPOCH, NBEPOCH, oldstats, Stats):
    remainingEPOCH_NB = NBEPOCH - EPOCH

    X = beta * remainingEPOCH_NB * (Stats['max'] - oldstats['max']) / oldstats['max']
    return X
