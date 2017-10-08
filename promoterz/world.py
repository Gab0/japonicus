#!/bin/python
import random

def migration(source, target, number_range):
    number = random.randrange(*number_range)

    for W in range(number):
        index = random.randrange(0,len(source.population))
        individual = source.population.pop(index)
        target.population.append(individual)

