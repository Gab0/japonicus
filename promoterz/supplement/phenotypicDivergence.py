#!/bin/python

from deap import tools
from promoterz import *

def individualPhenotypicDivergence(constructPhenotype, indA, indB):

    cmp = [indA, indB]
    cmp = [constructPhenotype(x) for x in cmp]
    cmp = [flattenParameters(x) for x in cmp]

    score = 0
    for w in cmp[0].keys():

        if cmp[0][w] != cmp[1][w]:
            score +=1

    return score

def populationPhenotypicDivergence(population, constructPhenotype):
    model = tools.selTournament(population,1, len(population)//3)[0]
    PDDmedian = 0
    for IND in population:
        if IND == model:
            IND.PDDscore = 1000
            continue
        IND.PDDscore = individualPhenotypicDivergence(constructPhenotype, model, IND)
        PDDmedian += IND.PDDscore
    PDDmedian = PDDmedian/(len(population)-1)
    for I in range(len(population)):
        if population[I].PDDscore < PDDmedian/3:
            if random.random() < 0.3:
                population[I] = None

    population = [x for x in population if x]
    return population
