#!/bin/python
import os
import random

gekkoStratFolder = "/home/gabs/Gekko/strategies/"

AllowedIndicators = ["PPO", "DEMA", "LRC", "RSI"]

stdResult = ["> this.settings.{i}.thresholds.up", "< this.settings.{i}.thresholds.down"]
IndicatorResults = {"PPO": {"PPOhist": stdResult },
           "DEMA": {"result": stdResult},
           "RSI": {"result": stdResult},
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

    Indicators = [ x for x in AllIndicators if (phenotype[x] == dict) if phenotype[x]['active'] > 0.8 ]
    if not Indicators:
        Indicators = [random.choice(AllIndicators)]

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

    BASE = BASE.replace("//BUYCONDITIONS;", "var BuyConditions = [%s];" % ','.join(BuyConditions))
    BASE = BASE.replace("//SELLCONDITIONS;", "var SellConditions = [%s];" % ','.join(SellConditions))

    StrategyFileName = 'j' + ''.join(sorted(Indicators))
    FILE = open(gekkoStratFolder + StrategyFileName+'.js', 'w')
    FILE.write(BASE)
    FILE.close()

    return StrategyFileName
def getTargetParameters():
    pass
