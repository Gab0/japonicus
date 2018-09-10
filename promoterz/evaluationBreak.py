#!/bin/python
import random
import json
import csv
from deap import tools


import promoterz
import evaluation
import TOMLutils

from interface import showBacktestResult


def showResults(World):
    validationDatasets = []
    # IS EVALUATION DATASET LOADED? USE IT;
    if World.EnvironmentParameters['evaluation']:
        useSecondary = 'evaluation'
    else:
        useSecondary = 'evolution'

    # LOAD EVALUATION DATASET;
    sourceDataset = random.choice(World.EnvironmentParameters[useSecondary])
    getter = evaluation.gekko.datasetOperations.getRandomSectorOfDataset
    for NB in range(World.evalbreakconf.proofSize):
        newDataset = getter(sourceDataset, World.backtestconf.deltaDays)
        validationDatasets.append(newDataset)

    for LOCALE in World.locales:
        LOCALE.population = [ind for ind in LOCALE.population
                             if ind.fitness.valid]

        # SELECT BEST INDIVIDUALS;
        B = World.evalbreakconf.NBBESTINDS
        BestIndividues = tools.selBest(LOCALE.population, B)
        Z = min(World.evalbreakconf.NBADDITIONALINDS,
                len(LOCALE.population) - B)
        Z = max(0, Z)

        # SELECT ADDITIONAL INDIVIDUALS;
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

        currentSessionBreakResults = []
        # EVALAUTE EACH SELECTED INDIVIDUE;
        for FinalIndividue in setOfToEvaluateIndividues:
            GlobalLogEntry = {}
            proof = stratSettingsProofOfViability
            AssertFitness, FinalProfit, Results = proof(
                World, FinalIndividue, validationDatasets
            )
            LOCALE.lastEvaluation = FinalProfit
            GlobalLogEntry['evaluation'] = FinalProfit
            World.logger.log(
                "\n\n\nTesting Strategy of %s @ EPOCH %i:\n" % (
                    LOCALE.name,
                    LOCALE.EPOCH)
            )

            for R, Result in enumerate(Results):
                World.logger.log(
                    showBacktestResult(Result,
                                       validationDatasets[R]) + '\n')

            World.logger.log(
                '\nRelative profit on evolution dataset: %.3f' %
                FinalProfit)
            if AssertFitness or FinalProfit > 50:
                World.logger.log("Current parameters are viable.")
            else:
                World.logger.log("Current parameters fails.")
                if not World.globalconf.showFailedStrategies:
                    World.logger.log(
                        "Skipping further tests on current parameters.",
                        show=False)
                    continue

            FinalIndividueSettings = World.tools.constructPhenotype(
                FinalIndividue)

            # --EVALUATION DATASET TEST AND REPORT;
            if World.EnvironmentParameters['evaluation']:
                evalDataset = random.choice(
                    World.EnvironmentParameters['evaluation'])
                evalDataset = getter(evalDataset, 0)
                secondaryResults = World.parallel.evaluateBackend(
                    [evalDataset], 0, [FinalIndividue]
                )
                print()
                # print(secondaryResults)
                backtestResult = secondaryResults[0][0]
                World.logger.log(
                    "Relative profit on evaluation dataset: \n\t%s" %
                    showBacktestResult(backtestResult))
                LOCALE.lastEvaluationOnSecondary = backtestResult['relativeProfit']
                GlobalLogEntry['secondary'] = backtestResult['relativeProfit']
            else:
                print("Evaluation dataset is disabled.")

            # LOG AND SHOW PARAMETERS;
            Show = json.dumps(FinalIndividueSettings, indent=2)
            print("~" * 18)
            World.logger.log(" %.3f final profit ~~~~" % FinalProfit)
            print(" -- Settings for Gekko config.js -- ")
            World.logger.log(Show)
            print(" -- Settings for Gekko --ui webpage -- ")
            TOMLSettings = TOMLutils.parametersToTOML(
                FinalIndividueSettings)
            World.logger.log(TOMLSettings)
            currentSessionBreakResults.append((backtestResult['relativeProfit'], TOMLSettings))
            paramsFilename = "%s-EPOCH%i" % (LOCALE.name,
                                             LOCALE.EPOCH)
            World.logger.saveParameters(paramsFilename, TOMLSettings)
            GlobalLogEntry['filename'] = paramsFilename
            print("\nRemember to check MAX and MIN values for each parameter.")
            print("\tresults may improve with extended ranges.")
            World.EvaluationStatistics.append(GlobalLogEntry)

    # SAVE GLOBAL EVALUATION LOGS;
    evaluationBreaksFilename = 'logs/evaluation_breaks.csv'

    if World.EvaluationStatistics:
        fieldnames = list(World.EvaluationStatistics[0].keys())
        with open(evaluationBreaksFilename, 'w') as f:
            GlobalEvolutionSummary = csv.DictWriter(f, fieldnames)
            GlobalEvolutionSummary.writeheader()
            World.logger.log('\t'.join(GlobalEvolutionSummary.fieldnames),
                             target="Summary",
                             show=False, replace=True)

            for n in World.EvaluationStatistics:
                GlobalEvolutionSummary.writerow(n)
        with open(evaluationBreaksFilename) as f:
            GlobalEvolutionSummary = csv.DictReader(f)
            for row in GlobalEvolutionSummary:
                World.logger.log('\t'.join([row[x] for x in row.keys()]),
                                 target="Summary",
                                 show=False, replace=False)

    World.logger.updateFile()

    # UPDATE WEB SERVER VISUALIZATION;
    if World.web:
        World.web.updateEvalBreakGraph(World.web, World.EvaluationStatistics)
        World.web.resultParameters += currentSessionBreakResults


def stratSettingsProofOfViability(World, Individual, Datasets):
    AllProofs = []
    # Datasets = [[x] for x in Datasets]
    Results = World.parallel.evaluateBackend(Datasets, 0, [Individual])
    for W in Results[0]:
        AllProofs.append(W['relativeProfit'])
    testMoney = 0
    for value in AllProofs:
        testMoney += value
    check = [x for x in AllProofs if x > 0]
    Valid = sum(check) == len(AllProofs)
    return Valid, testMoney, Results[0]
