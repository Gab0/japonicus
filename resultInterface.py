#!/bin/python

import os
import datetime
import random
import json
import pandas as pd
from deap import tools
import numpy as np

import promoterz
import evaluation

from Settings import getSettings

def showResults(World):
    ValidationDateranges = []
    useSecondary = 1 if World.EnvironmentParameters[1] else 0
    ValidationSpecifications = World.EnvironmentParameters[useSecondary].specifications

    for NB in range(World.genconf.proofSize):
        Daterange = evaluation.gekko.dataset.getRandomDateRange(
            World.EnvironmentParameters[useSecondary].daterange,
            World.genconf.deltaDays )
        ValidationDateranges.append(Daterange)


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
                                               ValidationSpecifications,
                                               ValidationDateranges)
            LOCALE.lastEvaluation = FinalProfit
            print("Testing Strategy:\n")
            if AssertFitness or FinalProfit > 50:
                print("Following strategy is viable.")
            else:
                print("Strategy Fails.")
            FinalIndividueSettings = World.tools.constructPhenotype(
                    FinalIndividue)

            # --EVALUATION DATASET TEST AND REPORT;
            if World.EnvironmentParameters[1]:
                Dataset = World.EnvironmentParameters[1]
                print(Dataset.__dict__)
                evaluationDaterange = evaluation.gekko.dataset.getRandomDateRange(
                    Dataset.daterange, 0)
                print(evaluationDaterange)
                secondaryResults = World.parallel.evaluateBackend(
                    Dataset.specifications,
                    [ [evaluationDaterange]] , 0, [FinalIndividue])
                print()
                print(secondaryResults)
                score = secondaryResults[0][0][0][0]
                World.logger.log("Relative profit on evaluation dataset: %.3f " % score)
                LOCALE.lastEvaluationOnSecondary = score
            else:
                print("Evaluation dataset is disabled.")

            Show = json.dumps(FinalIndividueSettings, indent=2)
            logInfo("~" * 18)

            logInfo(" %.3f final profit ~~~~" % FinalProfit)
            print(" -- Settings for Gekko config.js -- ")
            World.logger.log(Show)
            print(" -- Settings for Gekko --ui webpage -- ")
            logInfo(parametersToTOML(FinalIndividueSettings))

            print("\nRemember to check MAX and MIN values for each parameter.")
            print("\tresults may improve with extended ranges.")


def stratSettingsProofOfViability(World, Individual, specification, Dateranges):
    AllProofs = []
    Dateranges = [[x] for x in Dateranges]
    Results = World.parallel.evaluateBackend(specification, Dateranges, 0, [Individual])

    for W in Results[0]:
        ((q, s), m) = W
        AllProofs.append(q)
        World.logger.log('Testing monthly profit %.3f \t nbTrades: %.1f' % (q, m))

    testMoney = 0
    for value in AllProofs:
        testMoney += value

    check = [ x for x in AllProofs if x > 0 ]
    Valid = sum(check) == len(check)

    testMoney = testMoney

    World.logger.log("Annual profit %.3f%%" % (testMoney))
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

def getFromDict(DataDict, Indexes):
    return reduce(operator.getitem, Indexes, DataDict)
def writeToDict(DataDict, Indexes, Value):
    getFromDict(DataDict, Indexes[:-1])[Indexes[-1]] = Value


