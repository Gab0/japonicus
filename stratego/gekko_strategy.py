#!/bin/python
import os
import random
import hashlib
import re
from collections import OrderedDict
#from . import Settings
from .indicator_properties import *

#gekkoStratFolder = Settings('').Global['gekkoDir']+'/strategies/'


simplifyIndicators = lambda name: "var {I} = this.indicators.{i};".format(i=name.lower(), I=name.upper())



addIndicatorText = lambda name: "this.addIndicator('{i}', '{I}', this.settings.{I}{A});".format(i=name.lower(),
                                                                                                I=name.upper(),
                                                                                                A=IndicatorProperties[name]['input'])

onlyLetters = lambda message: re.sub(r"[^A-Za-z]+", '', message)

class StrategyFileManager():
    def __init__(self, gekkoPath, indicatorSettings):
        self.gekkoStratFolder = gekkoPath + '/strategies/japonicus/'
        self.gekkoIndicatorFolder = gekkoPath + '/strategies/indicators/'
        if not os.path.isdir(self.gekkoStratFolder):
            os.mkdir(self.gekkoStratFolder)

        AllowedIndicators = list(IndicatorProperties.keys())
        AllowedIndicators = [ ind for ind in AllowedIndicators if\
                              indicatorSettings[ind]['active'] ]

        baseContent = open('stratego/skeleton/ontrend.js').read()
        self.baseMD5 = hashlib.md5(baseContent.encode('utf-8')).hexdigest()
        self.sessionCreatedFiles = []

        self.skeletonHeader = [ l for l in baseContent.split('\n') if '//JAPONICUS' in l ][0]
        self.skeletonHeader = self.interpreteSkeletonHeader(self.skeletonHeader)

        for I in range(len(AllowedIndicators)):
            if not os.path.isfile("%s%s.js" %\
                                  (self.gekkoIndicatorFolder,
                                   AllowedIndicators[I])):
                print("Indicator %s doesn't exist!" % AllowedIndicators[I])
                AllowedIndicators[I] = None
        self.AllowedIndicators = [ x for x in AllowedIndicators if x ]

        if not self.AllowedIndicators:
            exit("No usable indicators detected.")

    def selectIndicator(self, chosenIndicators, phenotype, Type):
        indicatorsOnPhenotype = [ ind for ind in phenotype.keys()\
                                  if ind in IndicatorProperties.keys() ]
        allOfType = [ ind for ind in indicatorsOnPhenotype\
                      if IndicatorProperties[ind]['group'] == Type ]

        Indicators = sorted(allOfType, key=lambda ind: phenotype[ind]['active'], reverse=True)

        chosenIndicatorNames = [ chosenIndicators[name] for name in chosenIndicators.keys() ]


        for Ind in Indicators:
            if Ind not in chosenIndicatorNames:
                return Ind

        raise RuntimeError("not enough indicators for strategy %s;" % Indicators)

    def checkStrategy(self, phenotype):
        AllIndicators = self.AllowedIndicators
        Indicators = {}

        for indicatorInternalName in self.skeletonHeader.keys():
            selectedIndicatorType = self.skeletonHeader[indicatorInternalName]
            selectedIndicator = self.selectIndicator(Indicators, phenotype, selectedIndicatorType)
            Indicators.update({ indicatorInternalName: selectedIndicator })



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

        IndicatorNames = [ Indicators[slot] for slot in Indicators.keys() ]

        StrategyFileName = 'j' + self.baseMD5[-4:] + ''.join(IndicatorNames)
        stratpath= self.gekkoStratFolder + StrategyFileName + '.js'
        if not os.path.isfile(stratpath):
            print(self.sessionCreatedFiles)
            self.createStrategyFile(Indicators, stratpath)

        return 'japonicus/'+StrategyFileName

    def interpreteSkeletonHeader(self, header):
        Header = OrderedDict()
        header = header.replace('//JAPONICUS:', '')

        for segment in header.split(','):
            if '|' in segment:
                segment = segment.strip(' ').split('|')
                print(segment)
                Header[segment[0]] = onlyLetters(segment[1].lower())

        return Header

    def createStrategyFile(self, Indicators, stratpath):
        BASE = open("stratego/skeleton/ontrend.js").read()

        for Indicator in Indicators.keys():
            BASE = BASE.replace(Indicator, Indicators[Indicator])

        FILE = open(stratpath, 'w')
        FILE.write(BASE)
        print("Creating strategy %s file." % stratpath)
        self.sessionCreatedFiles.append(stratpath)
        FILE.close()

    def _createStrategyFile(self, Indicators, stratpath):
        BASE = open("stratego/skeleton/dumbsum.js").read()


        InitIndicators = [ addIndicatorText(ind) for ind in Indicators ]
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




