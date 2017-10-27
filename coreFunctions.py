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
        q,=World.tools.Evaluate(W, Individual, 'http://localhost:3000')
        AllProofs.append(q)
        print('Testing monthly profit %.3f' % q)

    iValue = 100
    for W in AllProofs:
        iValue += iValue * (W/100)
    check = [x for x in AllProofs if x > 0]
    Valid = len(check) == len(AllProofs)
    print("Annual profit %.3f%%" % (iValue-100))
    return Valid, iValue
 
def pasteSettingsToUI(Settings):
    text = []
    toParameter = lambda name, value: "%s = %f" % (name,value)
    Strat = list(Settings.keys())[0]
    text.append('{ %s }' % Strat)
    # print("{{ %s }}" % Settings[Strat])
    Settings = Settings[Strat]
    Settingskeys = Settings.keys()
    Settingskeys = sorted(list(Settingskeys),
                          key= lambda x: type(Settings[x]) ==dict, reverse=False)
    for W in Settingskeys:
        Q = Settings[W]
        if type(Q) == dict:
            text.append('\n[%s]' % W)
            for Z in Q.keys():
                text.append(toParameter(Z, Q[Z]))
            text.append('')
        else:
            text.append(toParameter(W, Q))
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


