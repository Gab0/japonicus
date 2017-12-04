#!/bin/python
import os
import random
import hashlib
#from . import Settings

#gekkoStratFolder = Settings('').Global['gekkoDir']+'/strategies/'


simplifyIndicators = lambda name: "var {I} = this.indicators.{i};".format(i=name.lower(), I=name.upper())

stdResult = ["> this.settings.{i}.thresholds.up",
             "< this.settings.{i}.thresholds.down"]
againstPrice = ["> price", "< price"]

Reverse = lambda x: [x[1], x[0]]
IndicatorProperties = {
            "PPO": {"input": '',
                    "attrname": "PPOhist",
                    "result": stdResult },

            "DEMA": {"attrname": "result",
                     "result": stdResult,
                     "input": ''},

            "RSI": {"result": Reverse(stdResult),
                    "input": '',
                    "attrname": "result"},

            "TSI": {"input": '',
                    "result": stdResult,
                    "attrname": "result"},

            "LRC": {"result": againstPrice,
                    "attrname": "result",
                    "input": '.depth'},

            "SMMA": {"input": '',
                     "attrname": 'result',
                     "result": stdResult},
            "CCI": {"input": '',
                    "result": stdResult,
                    "attrname": 'result'}
        }


addIndicatorText = lambda name: "this.addIndicator('{i}', '{I}', this.settings.{I}{A});".format(i=name.lower(),
                                                                                                I=name.upper(),
                                                                                                A=IndicatorProperties[name]['input'])

class StrategyFileManager():
    def __init__(self, gekkoPath):
        self.gekkoStratFolder = gekkoPath + '/strategies/japonicus/'
        self.gekkoIndicatorFolder = gekkoPath + '/strategies/indicators/'
        if not os.path.isdir(self.gekkoStratFolder):
            os.mkdir(self.gekkoStratFolder)
        
        AllowedIndicators = ["PPO", "DEMA", "LRC", "RSI", "SMMA", "CCI", "TSI"]

        baseContent = open('stratego/base_strategy.js').read()
        self.baseMD5 = hashlib.md5(baseContent.encode('utf-8')).hexdigest()
        self.sessionCreatedFiles = []
        for I in range(len(AllowedIndicators)):
            if not os.path.isfile("%s%s.js" %\
                                  (self.gekkoIndicatorFolder,
                                   AllowedIndicators[I])):
                print("Indicator %s doesn't exist!" % AllowedIndicators[I])
                AllowedIndicators[I] = None
        self.AllowedIndicators = [ x for x in AllowedIndicators if x ]

        if not self.AllowedIndicators:
            exit("No usable indicators detected.")
    def checkStrategy(self, phenotype):
        AllIndicators = self.AllowedIndicators
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



        FallbackIndicators = [x for x in AllIndicators\
                              if x in phenotype.keys()]

        if not Indicators:
            Indicators = sorted(FallbackIndicators,
                                key=sortIndicators, reverse=True)[0:2]

        if not Indicators:
            exit("NO INDICATORS")
        StrategyFileName = 'j' + self.baseMD5[-4:] + ''.join(sorted(Indicators))
        stratpath= self.gekkoStratFolder + StrategyFileName + '.js'
        if not os.path.isfile(stratpath):
            print(self.sessionCreatedFiles)
            self.createStrategyFile(Indicators, stratpath)

        return 'japonicus/'+StrategyFileName

    def createStrategyFile(self, Indicators, stratpath):
        BASE = open("stratego/base_strategy.js").read()


        InitIndicators = [addIndicatorText(ind) for ind in Indicators]
        BASE = BASE.replace("//ADD_INDICATORS;", ('\n'.join(InitIndicators)))

        SimplifyIndicators = [ simplifyIndicators(ind) for ind in Indicators ]
        BASE = BASE.replace("//SIMPLIFY_INDICATORS;", ('\n'.join(SimplifyIndicators)))

        BuyConditions = []
        SellConditions = []

        for ind in Indicators:
            Bc = "%s.%s %s" % (ind, IndicatorProperties[ind]['attrname'],
                               IndicatorProperties[ind]['result'][0].format(i=ind))

            Sc = "%s.%s %s" % (ind, IndicatorProperties[ind]['attrname'],
                               IndicatorProperties[ind]['result'][1].format(i=ind))

            BuyConditions.append(Bc)
            SellConditions.append(Sc)

        BASE = BASE.replace("//BUYCONDITIONS;",
                            "var BuyConditions = [%s];" % ', '.join(BuyConditions))
        BASE = BASE.replace("//SELLCONDITIONS;",
                            "var SellConditions = [%s];" % ', '.join(SellConditions))

        FILE = open(stratpath, 'w')
        FILE.write(BASE)
        print("Creating strategy %s file." % stratpath)
        self.sessionCreatedFiles.append(stratpath)
        FILE.close()




