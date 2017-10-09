#!/bin/python
import random

import locale

class World():
    def __init__(self, NB_LOCALE=3):
        globaltools = None

        self.locales = []
    def generateLocale(self):
        name = 'Locale%i' % len(self.locales+1)
        L = locale.Locale(name, loop)

def migration(source, target, number_range):
    number = random.randrange(*number_range)

    for W in range(number):
        index = random.randrange(0,len(source.population))
        individual = source.population.pop(index)
        del individual.fitness.values
        target.population.append(individual)

