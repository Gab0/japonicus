#!/bin/python

import matplotlib
import matplotlib.pyplot as plt



def plotEvolutionSummary(DATA, filename):
    for w in list(DATA.keys()).sort():
        _X=w
        _Y=DATA[w]
        plt.plot([_X], [_Y], 'go')
    
    plt.savefig('%s.png' % filename, format='png')
