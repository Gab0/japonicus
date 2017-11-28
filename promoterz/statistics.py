#!/bin/python
from deap import tools
import numpy as np
import os
statisticsNames = {
    'avg': 'Average profit',
    'std': 'Profit variation',
    'min': 'Minimum profit',
    'max': 'Maximum profit',
    'size': 'Population size',
    'maxsize': 'Max population size',
    'avgTrades': 'Avg trade number',
    'sharpe': 'Avg sharpe ratio'
}

def getStatisticsMeter():
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
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
        message = ','.join([str(x) for x in [i] + stats])
    else:
        raise
    #print(message)

    if i == 0 and os.path.isfile(filename):
        os.remove(filename)
    f=open(filename, 'a+')
    f.write(message+"\n")
    #print(message)
    f.close()



def compileStats(locale):
    # --get proper evolution statistics;
    Stats=locale.stats.compile(locale.population)
    Stats['dateRange'] = None
    Stats['maxsize'] = locale.POP_SIZE
    Stats['size'] = len(locale.population)
    Stats['avgTrades'] = locale.extraStats['avgTrades']
    Stats['sharpe'] = np.mean([x.fitness.values[1] for x in locale.population])
    
    locale.EvolutionStatistics[locale.EPOCH] = Stats
    
    LOGPATH ="output/evolution_gen_%s.csv" % locale.name
    write_evolution_logs(locale.EPOCH,
                                              Stats, LOGPATH)
    
def showStats(locale):
    # show information;
    Stats = locale.EvolutionStatistics[locale.EPOCH]
    print("EPOCH %i\t&%i" % (locale.EPOCH,
                             locale.extraStats['nb_evaluated']))

    statnames = [ 'max', 'avg', 'min', 'std', 'size',
                  'maxsize', 'avgTrades', 'sharpe' ]

    statText = ""
    for s in range(len(statnames)):
        SNAME = statnames[s]
        SVAL = Stats[SNAME]
        statText += "%s" % statisticsNames[SNAME]
        if not SVAL % 1:
            statText += " %i\t" % SVAL
        else:
            statText += " %.3f\t" % SVAL
        if s % 2:
            statText += '\n'
    print(statText)
    print('Elder dies %i' % locale.extraStats['elder'])
    print('')

