#!/bin/python
from deap import tools
import numpy as np
import os
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

def write_evolution_logs(i, stats, filename="output/evolution_gen.csv"):
    #print(i, stats)
    if type(stats) == dict:
        message = ','.join([str(x) for x in [i,stats['avg'],
                                             stats['std'],
                                             stats['min'],
                                             stats['max'],
                                             stats['dateRange']]])
    elif type(stats) == list:
        raise # DEBUG;;
        message = ','.join([str(x) for x in [i,stats[1],stats[2],stats[3],stats[4],stats[5]]])
    else:
        raise
    #print(message)

    if i == 0 and os.path.isfile(filename):
        os.remove(filename)
    f=open(filename, 'a+')
    f.write(message+"\n")
    #print(message)
    f.close()



