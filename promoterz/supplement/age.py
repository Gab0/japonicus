#1/bin/python

from deap import base
def _maturePopulation(population):
    for W in range(len(population)):
        try:
            assert(population[W].Age)
        except:
            population[W].Age = 0
        population[W].Age += 1

def _checkRetirement(individue, averageScore, ageBoundary):
    inaptitude = individue.fitness.values[0] < averageScore/2
    oldenough = individue.Age > ageBoundary[0]

    dies = (inaptitude and oldenough) or individue.Age > ageBoundary[1]
    return dies

def _killElders(population, averageScore, ageBoundary):
    for I in range(len(population)):
        if _checkRetirement(population[I], averageScore, ageBoundary):
            population[I] = None

    population = [ x for x in population if x ]
    return population

def ageZero(population):
    for q in range(len(population)):
        population[q].Age=0

def populationAges(ageBoundary, population, averageScore):
    _maturePopulation(population)
    _killElders(population, averageScore, ageBoundary)
    return population

def getToolbox(ageBoundaries):
    toolbox = base.Toolbox()

    toolbox.register('zero', ageZero)
    toolbox.register('populationAges', populationAges, ageBoundaries)

    return toolbox
