#!/bin/python

statisticsNames = {'avg': 'Average profit',
                   'std': 'Profit variation',
                   'min': 'Minimum profit',
                   'max': 'Maximum profit',
                   'size': 'Population size',
                   'maxsize': 'Max population size'}

def getStatisticsMeter():
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)


    return stats
