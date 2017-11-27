#!/bin/python

import os
import datetime
import random
import pandas as pd
from deap import tools
import numpy as np

import promoterz
from Settings import getSettings


def stratSettingsProofOfViability(World, Individual, GlobalDataset):
    AllProofs = []
    for W in GlobalDataset:
        (q, s), m = World.tools.Evaluate([W], Individual, 'http://localhost:3000')
        AllProofs.append(q)
        print('Testing monthly profit %.3f \t nbTrades: %.1f' % (q, m))

    iValue = 100
    for W in AllProofs:
        iValue += iValue * (W/100)
    check = [x for x in AllProofs if x > 0]
    Valid = sum(check) == len(check)
    print("Annual profit %.3f%%" % (iValue-100))
    return Valid, iValue
 
def pasteSettingsToUI(Settings):
    text = []
    toParameter = lambda name, value: "%s = %f" % (name,value)

    # print("{{ %s }}" % Settings[Strat])
    def iterate(base):

        Settingskeys = base.keys()
        Settingskeys = sorted(list(Settingskeys),
                          key= lambda x: type(base[x]) == dict, reverse=False)

        for W in Settingskeys:
            Q = base[W]
            if type(Q) == dict:
                text.append("[%s]" % W)
                iterate(Q)
                text.append('')
            else:
                text.append("%s = %s" % (W, Q))

    iterate(Settings)
    return '\n'.join(text)

def loadGekkoConfig():
    pass

def logInfo(message, filename="evolution_gen.log"):
    gsettings = getSettings()['Global']
    filename = os.path.join(gsettings['save_dir'], filename)
    F=open(filename, 'a+')
    F.write(message)
    print(message)
    F.close()



def getFromDict(DataDict, Indexes):
    return reduce(operator.getitem, Indexes, DataDict)
def writeToDict(DataDict, Indexes, Value):
    getFromDict(DataDict, Indexes[:-1])[Indexes[-1]] = Value


