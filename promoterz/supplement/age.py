#1/bin/python

from deap import base

def _maturePopulation(population):
    for W in range(len(population)):
        try:
            assert(population[W].Age)
        except:
            population[W].Age = 0
        population[W].Age += 1

def _checkRetirement(individue, statistics, ageBoundary):
    # (Minetti, 2005)
    indscore = individue.fitness.values[0]
    N = (ageBoundary[1] - ageBoundary[0]) /2
    aptitude = indscore - statistics['avg']

    if aptitude > 0:
        ABC = sum(ageBoundary)/2
        RSB = statistics['max'] - statistics['avg']
    else:
        ABC = ageBoundary[0]
        RSB = statistics['avg'] - statistics['min']

    RSB= max(1,RSB)
    survival = ABC + (N * aptitude / RSB)

    #oldenough = individue.Age > ageBoundary[0]
    #relativeAge = (individue.Age-ageBoundary[0]) / (ageBoundary[1]-ageBoundary[0]) 

    retires = individue.Age - survival > ageBoundary[1]
    #print(survival)
    return retires

def _killElders(population, statistics, ageBoundary):
    for I in range(len(population)):
        if _checkRetirement(population[I], statistics, ageBoundary):
            population[I] = None

    population = [ x for x in population if x ]
    return population

def ageZero(population):
    for q in range(len(population)):
        population[q].Age=0

def populationAges(ageBoundary, population, averageScore):
    _maturePopulation(population)
    population=_killElders(population, averageScore, ageBoundary)
    return population







