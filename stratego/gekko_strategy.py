#!/bin/python
import os
import random

gekkoStratFolder = "/home/gabs/Gekko/strategies/"

AllowedIndicators = ["PPO", "DEMA", "LRC", "RSI", "SMMA"]

stdResult = ["> this.settings.{i}.thresholds.up", "< this.settings.{i}.thresholds.down"]
Reverse = lambda x: [x[1], x[0]]
IndicatorResults = {
    "PPO": {"PPOhist": stdResult },
               "DEMA": {"result": stdResult},
           "RSI": {"result": Reverse(stdResult)},
           "TSI": {"result": stdResult},
           "LRC": {"result": stdResult},
           "SMMA": {"result": stdResult}
}



for I in range(len(AllowedIndicators)):
    if not os.path.isfile("%s/indicators/%s.js" % (gekkoStratFolder, AllowedIndicators[I])):
        print("Indicator %s doesn't exist!" % AllowedIndicators[I])
        AllowedIndicators[I] = None
AllowedIndicators = [ x for x in AllowedIndicators if x ]

addIndicatorText = lambda name: "this.addIndicator('{i}', '{I}', this.settings.{I});".format(i=name.lower(),
                                                                           I=name.upper())
simplifyIndicators = lambda name: "var {I} = this.indicators.{i}".format(i=name.lower(), I=name.upper())

def createStrategyFile(phenotype):
    BASE = open("stratego/base_strategy.js").read()
    AllIndicators = AllowedIndicators

    Indicators = []
    for I in AllIndicators:
        if I in phenotype.keys():
            if phenotype[I] == dict:
                if phenotype[I]['active'] > 0.8:
                    Indicators.append(I)

    def sortIndicators(ind):
        if ind in phenotype.keys():
            return phenotype[ind]['active']
        else:
            return 0

    if not Indicators:
        Indicators = sorted(AllIndicators, key=sortIndicators, reverse=True)[0:2]


    InitIndicators = [addIndicatorText(ind) for ind in Indicators]
    BASE = BASE.replace("//ADD_INDICATORS;", ('\n'.join(InitIndicators)))

    SimplifyIndicators = [ simplifyIndicators(ind) for ind in Indicators ]
    BASE = BASE.replace("//SIMPLIFY_INDICATORS;", ('\n'.join(SimplifyIndicators)))

    BuyConditions = []
    SellConditions = []
    for ind in Indicators:
        for condition in IndicatorResults[ind].keys():
            Bc = "%s.%s %s" % (ind, condition, IndicatorResults[ind][condition][0].format(i=ind))
            Sc = "%s.%s %s" % (ind, condition, IndicatorResults[ind][condition][1].format(i=ind))
            BuyConditions.append(Bc)
            SellConditions.append(Sc)

    BASE = BASE.replace("//BUYCONDITIONS;", "var BuyConditions = [%s];" % ', '.join(BuyConditions))
    BASE = BASE.replace("//SELLCONDITIONS;", "var SellConditions = [%s];" % ', '.join(SellConditions))

    StrategyFileName = 'j' + ''.join(sorted(Indicators))
    FILE = open(gekkoStratFolder + StrategyFileName+'.js', 'w')
    FILE.write(BASE)
    FILE.close()

    return StrategyFileName
def getTargetParameters():
    pass
