#!/bin/python

# source https://www.researchgate.net/publication/27382766_On_benchmarking_functions_for_genetic_algorithm
import random
import math


def evalRosenbrock(parameters):
    Result = pow(1-parameters[0], 2)
    Result += 100 * pow(pow(parameters[0], 2) - parameters[1], 2)

    return -Result


def evalGriewangk3(parameters):
    Dimensions = 10
    Result = 1

    for w in range(Dimensions):
        W = w + 1
        Result += pow(parameters[w], 2) / 4000

    COSs = math.cos(parameters[0])
    for z in range(1, Dimensions):
        Z = z + 1
        COSs *= (math.cos(parameters[z]) / math.sqrt(Z))

    Result -= COSs

    return -Result


def evalGriewangk2(parameters):
    Result = 200

    for w in range(20):
        W = w + 1
        Result += pow(parameters[w], 2)
        Result -= 10 * (math.cos(2*math.pi*parameters[w]))

    return -Result


def evalGriewangk1(parameters):
    A = 4189.829101
    Open = 10 * A
    Result = Open
    for w in range(10):
        W = w + 1
        Result += -parameters[w] * math.sin(math.sqrt(abs(parameters[w])))

    return -Result


def evalFunctionFour(parameters):
    Result = 0
    for w in range(30):
        W = w + 1
        Result += W * pow(parameters[w], 4) + random.gauss(0, 1)

    return -Result


def evalFoxHole(parameters):
    Result = 0.002
    a = [
        [-32, -16, 0, 16, 32, -32, -16, 0, 16, 32, -32, -16, 0, 16,
         32, -32, -16, 0, 16, 32, -32, -16, 0, 16, 32],
        [-32, -32, -32, -32, -32, -16, -16, -16, -16, -16, 0,
         0, 0, 0, 0, 16, 16, 16, 16, 16, 32, 32, 32, 32, 32]
    ]

    for w in range(25):
        W = 1+w
        D = W
        for k in range(2):
            D += pow(parameters[k] - a[k][w], 6)
        Result += 1/D

    return Result


def Evaluate(genconf, phenotype):
    evalFunctionName = list(phenotype.keys())[0]
    parameters = phenotype[evalFunctionName]
    parameters = [parameters[N] for N in sorted(list(parameters.keys()))]

    evalFunctions = {
        'functionfour': evalFunctionFour,
        'foxhole': evalFoxHole,
        'griewangk1': evalGriewangk1,
        'griewangk2': evalGriewangk2,
        'griewangk3': evalGriewangk3,
        'rosenbrock': evalRosenbrock
    }
    result = evalFunctions[evalFunctionName](parameters)

    return {
        'relativeProfit': result,
        'sharpe': 0,
        'trades': 25
    }
