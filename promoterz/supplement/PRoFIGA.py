#!/bin/python

def calculatePRoFIGA(beta, EPOCH, NBEPOCH, oldstats, Stats):
    X = beta * (NBEPOCH-EPOCH) * \
        (Stats['max'] - oldstats['max']) / oldstats['max']
    return X
