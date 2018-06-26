#!/bin/python
import json
import pytoml
import random


class strategyRanker():
    def __init__(self):
        self.Strategies = []

    def loadStrategyRankings(self):
        W = json.load(open("gekkoStrategyRankings.json"))
        self.Strategies = []
        for s in W:
            S = strategyParameterSet(s)
            self.Strategies.append(S)

    def saveStrategyRankings(self):
        outputList = []

        for strategy in self.Strategies:
            outputList.append(strategy.toJson())

        json.dump(outputList, open("gekkoStrategyRankings.json", 'w'))

    def selectStrategyToRun(self, sigma=10):
        # SELECT AND LAUNCH TRADING BOT BATCH WITH SELECTED STRATEGY;
        if random.random() < sigma / 100:
            Strategy = sorted(self.Strategies,
                              key=lambda s: s.getScore(), reverse=True)[0]
        else:
            Strategy = random.choice(self.Strategies)

        return Strategy


class strategyParameterSet():
    def __init__(self, jsonData):
        self.Attributes = ['strategy', 'parameters', 'profits']
        self.fromJson(jsonData)

    def fromJson(self, jsonData):
        for Name in self.Attributes:
            self.__dict__[Name] = jsonData[Name]

    def toJson(self):
        jsonData = {}
        for Name in self.Attributes:
            jsonData[Name] = self.__dict__[Name]
        return jsonData

    def loadParameterSet(self):
        self.parameterSet = pytoml.load(open(self.parameters))

    def getScore(self):
        if self.profits:
            return sum(self.profits) / len(self.profits)
        else:
            return 0
