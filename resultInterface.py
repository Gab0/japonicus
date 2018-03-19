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
import TOMLutils

from Settings import getSettings


def showResults(World):
    ValidationDateranges = []
    useSecondary = 1 if World.EnvironmentParameters[1] else 0
    ValidationSpecifications = World.EnvironmentParameters[useSecondary].specifications
    for NB in range(World.genconf.proofSize):
        Daterange = evaluation.gekko.dataset.getRandomDateRange(
            World.EnvironmentParameters[useSecondary].daterange, World.genconf.deltaDays
        )
        ValidationDateranges.append(Daterange)

    for LOCALE in World.locales:
        LOCALE.population = [ind for ind in LOCALE.population if ind.fitness.valid]
        B = World.genconf.finaltest['NBBESTINDS']
        BestIndividues = tools.selBest(LOCALE.population, B)
        Z = min(World.genconf.finaltest['NBADDITIONALINDS'], len(LOCALE.population) - B)
        Z = max(0, Z)
        AdditionalIndividues = promoterz.evolutionHooks.Tournament(
            LOCALE.population, Z, Z * 2
        )
        print("%i selected;" % len(AdditionalIndividues))
        AdditionalIndividues = [
            x for x in AdditionalIndividues if x not in BestIndividues
        ]
        setOfToEvaluateIndividues = BestIndividues + AdditionalIndividues
        print("%i selected;" % len(setOfToEvaluateIndividues))
        print("Selecting %i+%i individues, random test;" % (B, Z))
        for FinalIndividue in setOfToEvaluateIndividues:
            GlobalLogEntry = {}
            proof = stratSettingsProofOfViability
            AssertFitness, FinalProfit, Results = proof(
                World, FinalIndividue, ValidationSpecifications, ValidationDateranges
            )
            LOCALE.lastEvaluation = FinalProfit
            GlobalLogEntry['evaluation'] = FinalProfit
            World.logger.log(
                "\n\n\nTesting Strategy of %s @ EPOCH %i:\n" % (LOCALE.name, LOCALE.EPOCH)
            )

            for Result in Results:
                World.logger.log(
                    'Testing monthly profit %.3f \t nbTrades: %.1f' %
                    (Result['relativeProfit'], Result['trades'])
                )

            World.logger.log('\nRelative profit on evolution dataset: %.3f' % FinalProfit )
            if AssertFitness or FinalProfit > 50:
                World.logger.log("Current parameters are viable.")
            else:
                World.logger.log("Current parameters fails.")
                if not World.globalconf.showFailedStrategies:
                    World.logger.log("Skipping further tests on current parameters.", show=False)
                    continue

            FinalIndividueSettings = World.tools.constructPhenotype(FinalIndividue)
            # --EVALUATION DATASET TEST AND REPORT;
            if World.EnvironmentParameters[1]:
                Dataset = World.EnvironmentParameters[1]
                evaluationDaterange = evaluation.gekko.dataset.getRandomDateRange(
                    Dataset.daterange, 0
                )
                secondaryResults = World.parallel.evaluateBackend(
                    Dataset.specifications, [[evaluationDaterange]], 0, [FinalIndividue]
                )
                print()
                # print(secondaryResults)
                score = secondaryResults[0][0]['relativeProfit']
                World.logger.log("Relative profit on evaluation dataset: %.3f " % score)
                LOCALE.lastEvaluationOnSecondary = score
                GlobalLogEntry['secondary'] = score
            else:
                print("Evaluation dataset is disabled.")
            Show = json.dumps(FinalIndividueSettings, indent=2)
            print("~" * 18)
            World.logger.log(" %.3f final profit ~~~~" % FinalProfit)
            print(" -- Settings for Gekko config.js -- ")
            World.logger.log(Show)
            print(" -- Settings for Gekko --ui webpage -- ")
            World.logger.log(TOMLutils.parametersToTOML(FinalIndividueSettings))
            print("\nRemember to check MAX and MIN values for each parameter.")
            print("\tresults may improve with extended ranges.")
            World.EvaluationStatistics.append(GlobalLogEntry)
    GlobalEvolutionSummary = pd.DataFrame(World.EvaluationStatistics)
    if not GlobalEvolutionSummary.empty:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            GlobalEvolutionSummary = str(GlobalEvolutionSummary)
            World.logger.log(GlobalEvolutionSummary, target="Summary", show=False, replace=True)
    World.logger.updateFile()


def stratSettingsProofOfViability(World, Individual, specification, Dateranges):
    AllProofs = []
    Dateranges = [[x] for x in Dateranges]
    Results = World.parallel.evaluateBackend(specification, Dateranges, 0, [Individual])
    for W in Results[0]:
        AllProofs.append(W['relativeProfit'])
    testMoney = 0
    for value in AllProofs:
        testMoney += value
    check = [ x for x in AllProofs if x > 0 ]
    Valid = sum(check) == len(AllProofs)
    return Valid, testMoney, Results[0]


def loadGekkoConfig():
    pass


def getFromDict(DataDict, Indexes):
    return reduce(operator.getitem, Indexes, DataDict)


def writeToDict(DataDict, Indexes, Value):
    getFromDict(DataDict, Indexes[:-1])[Indexes[-1]] = Value
