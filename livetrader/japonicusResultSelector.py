#!/bin/python
import os
import csv
import shutil
import names

import binanceMonitor


def readResultFolder(strategyName, runLogFolderPath, retrievalCount=1):
    evalBreaksLogFilename = os.path.join(runLogFolderPath, 'evaluation_breaks.csv')
    if not os.path.isfile(evalBreaksLogFilename):
        print("Evaluation break log file not found.")
        return False

    evalBreakLogs = open(evalBreaksLogFilename)

    evalBreakLogs = csv.DictReader(evalBreakLogs)

    positiveResults = []
    for result in evalBreakLogs:
        if result['evaluation'] > 0 and result['secondary'] > 0:
            if len(list(result.keys())) > 2:
                result['score'] = result['evaluation'] + result['secondary']
                positiveResults.append(result)
            else:
                print("Naive logging system detected, from older japonicus version.")
                print("Unable to check result file.")

    if not positiveResults:
        print("No positive results found!")
        return False

    positiveResults = sorted(positiveResults,
                             key=lambda r: r['score'], reverse=True)


    parameterName = strategyName + names.get_full_name()

    R = positiveResults[0]
    stratPath = os.path.join(R['filepath'])
    shutil.copy()

    strategyRankings = binanceMonitor.loadStrategyRankings()

    newEntry = binanceMonitor.strategyParameterSet(
        {
            'strategy': strategyName,
            'parameters': parameterName,
            'profits': []
        }
    )

    strategyRankings.append(newEntry)

    binanceMonitor.saveStrategyRankings(strategyRankings)
    
    return True


def sweepLogFolder():
    availableLogs = os.listdir('logs')
    for folder in availableLogs:
        print(folder)
        strategyName = ''
        readResult = readResultFolder(strategyName, folder)
