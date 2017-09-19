#!/bin/python

import os
import datetime
import random
import pandas as pd

from gekkoWrapper import runBacktest
from Settings import getSettings

def reconstructTradeSettings(IND, Strategy):
    Settings = {
        Strategy:{
            "short": IND[0]//5+1,
            "long": IND[1]//3+10,
            "signal": IND[2]//10+5,
            "interval": IND[3]//3,
            "thresholds": {
                "down": (IND[4]//1.5-50)/60,
                "up": (IND[5]//1.5-5)/60,
                "low": IND[6]//2+10,
                "high": IND[7]//2+45,
                "persistence": IND[8]//25+1,
                "fibonacci": (IND[9]//11+1)/10
            }
        }
    }
    
        
    return Settings

def Evaluate(DateRange, Individual, Strategy):
    Settings = reconstructTradeSettings(Individual, Strategy)
    #print(Settings)
    Profit = runBacktest(Settings, DateRange)
    return Profit,

def getDateRange(Limits, deltaDays=3):
    DateFormat="%Y-%m-%d %H:%M:%S"

    epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime(DateFormat)
    deltams=deltaDays * 24 * 60 * 60

    DateRange = {
        "from": "%s" % epochToString(Limits['to']-deltams),
        "to": "%s" % epochToString(Limits['to'])
    }
    return DateRange

def getRandomDateRange(Limits, deltaDays, testDays=0):
    DateFormat="%Y-%m-%d %H:%M:%S"

    epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime(DateFormat)
    FLms = Limits['from']
    TLms = Limits['to']
    deltams=deltaDays * 24 * 60 * 60
    testms=testDays * 24 * 60 * 60

    Starting= random.randint(FLms,TLms-deltams-testms)
    DateRange = {
        "from": "%s" % epochToString(Starting),
        "to": "%s" % epochToString(Starting+deltams)
    }

    return DateRange


def stratSettingsProofOfViability(Settings, DatasetLimits):
    AllProofs = []
    for W in range(10):
        DateRange = getRandomDateRange(DatasetLimits, 30)
        q=runBacktest(Settings, DateRange)
        AllProofs.append(q)
        print('Month PoV %.3f' % q)
        
    check = [x for x in AllProofs if x > 0]
    Valid = len(check) == len(AllProofs)
    return Valid   
 
def pasteSettingsToUI(Settings):
    text = []
    toParameter = lambda name, value: "%s = %f" % (name,value)
    Strat = list(Settings.keys())[0]
    text.append('{ %s }' % Strat)
    #rint("{{ %s }}" % Settings[Strat])
    Settings = Settings[Strat]
    for W in Settings.keys():
        Q = Settings[W]
        if type(Q) == dict:
            text.append('\n[%s]' % W)
            for Z in Q.keys():
                text.append(toParameter(Z, Q[Z]))
        else:
            text.append(toParameter(W, Q))
    return '\n'.join(text)

def loadGekkoConfig():
    pass

def logInfo(message, filename="evolution_gen.log"):
    gsettings = getSettings()['global']
    filename = os.path.join(gsettings['save_dir'], filename)
    F=open(filename, 'a+')
    F.write(message)
    print(message)
    F.close()

def write_evolution_logs(i, stats, filename="evolution_gen.csv"):
    print(i, stats)
    if type(stats) == dict:
        message = ','.join([str(x) for x in [i,stats['avg'],stats['std'],stats['min'],stats['max']]])
    elif type(stats) == list:
        message = ','.join([str(x) for x in [i,stats[1],stats[2],stats[3],stats[-1]]])
    else:
        raise
    print(message)
    gsettings = getSettings()['global']
    filename = os.path.join(gsettings['save_dir'], filename)
    if i == 0:
        os.remove(filename)
    f=open(filename, 'a+')
    f.write(message+"\n")
    print(message)
    f.close()
