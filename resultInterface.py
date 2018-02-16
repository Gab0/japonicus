#!/bin/python

import os
import datetime
import random
import json
import pandas as pd
from deap import tools
import numpy as np

import promoterz
from Settings import getSettings

def showResults(World):
    ValidationDataset =\
        promoterz.evaluation.gekko.globalEvaluationDataset(World.EnvironmentParameters,
                                                           World.genconf.deltaDays,
                                                           World.genconf.proofSize)
    for LOCALE in World.locales:
        LOCALE.population = [ ind for ind in LOCALE.population if ind.fitness.valid ]
        B = World.genconf.finaltest['NBBESTINDS']
        BestIndividues = tools.selBest(LOCALE.population,B)

        Z = min(World.genconf.finaltest['NBADDITIONALINDS'], len(LOCALE.population)-B)
        Z = min(0, Z)
        print("Selecting %i+%i individues, random test;" % (B,Z))
        AdditionalIndividues = promoterz.evolutionHooks.Tournament(LOCALE.population, Z, Z*2)

        print("%i selected;" % len(AdditionalIndividues))
        AdditionalIndividues = [ x for x in AdditionalIndividues\
                                 if x not in BestIndividues ]

        FinalIndividues = BestIndividues + AdditionalIndividues

        print("%i selected;" % len(FinalIndividues))
        for FinalIndividue in FinalIndividues:
            proof = stratSettingsProofOfViability
            AssertFitness, FinalProfit = proof(World,
                                              FinalIndividue,
                                              ValidationDataset)
            print("Testing Strategy:\n")
            if AssertFitness or FinalProfit > 50:
                print("Following strategy is viable.")
            else:
                print("Strategy Fails.")
            FinalIndividueSettings = World.tools.constructPhenotype(
                    FinalIndividue)

            Show = json.dumps(FinalIndividueSettings, indent=2)
            logInfo("~" * 18)
            
            logInfo(" %.3f final profit ~~~~" % FinalProfit)
            print(" -- Settings for Gekko config.js -- ")
            print(Show)
            print(" -- Settings for Gekko --ui webpage -- ")
            logInfo(parametersToTOML(FinalIndividueSettings))
            
            print("\nRemember to check MAX and MIN values for each parameter.")
            print("\tresults may improve with extended ranges.")


def stratSettingsProofOfViability(World, Individual, GlobalDataset):
    AllProofs = []
    GlobalDataset = [[x] for x in GlobalDataset]
    Results = World.parallel.evaluateBackend(GlobalDataset, 0, [Individual])

    for W in Results[0]:
        ((q, s), m) = W
        AllProofs.append(q)
        print('Testing monthly profit %.3f \t nbTrades: %.1f' % (q, m))

    testMoney = 100
    for value in AllProofs:
        testMoney +=  (value/100*testMoney)

    check = [ x for x in AllProofs if x > 0 ]
    Valid = sum(check) == len(check)

    testMoney = testMoney - 100

    print("Annual profit %.3f%%" % (testMoney))
    return Valid, testMoney

def parametersToTOML(Settings):
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


