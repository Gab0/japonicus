#!/bin/python

# source https://www.researchgate.net/publication/27382766_On_benchmarking_functions_for_genetic_algorithm
import random


def evalFunctionFour(parameters):
    Result = 0
    for w in range(30):
        W = w+1
        Result += W * pow(parameters[w], 4) + random.gauss(0, 1)

    return Result


def evalFoxHole(parameters):
    Result = 0.002
    for w in range(25):
        W = 1+w
        Result += 1/W
        for K in range(1, 2):
            Result += pow(parameters[w] - a[w][j], 6)

    return Result


def Evaluate(genconf, phenotype):
    evalFunctionName = list(phenotype.keys())[0]
    parameters = phenotype[evalFunctionName]
    parameters = [parameters[N] for N in sorted(list(parameters.keys()))]

    evalFunctions = {
        'functionfour': evalFunctionFour,
        'foxhole': evalFoxHole
    }
    result = 100-evalFunctions[evalFunctionName](parameters)
    print(result)
    return {
        'relativeProfit': result,
        'sharpe': 1,
        'trades': 25
    }
