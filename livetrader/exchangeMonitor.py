#!/bin/python
import ccxt
import json
import Settings
import os
import pytoml
import time
os.chdir(os.path.dirname(os.path.realpath(__file__)))

binanceconf = Settings.makeSettings(Settings.loadTomlSettings('binance'))
secret = open(binanceconf.credentialsFilePath).read()

secret = secret.split('\n')
Binance = ccxt.binance({'apiKey': secret[0],
                        'secret': secret[1]})
Binance.load_markets()


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


def parseAsset(Asset):
    P = [float(Asset[code]) for code in ['free', 'locked']]
    return P[0], P[1]


def fetchAssetPrices(Symbols):
    Prices = {}
    for Symbol in Symbols:
        Cotation = Binance.fetch_ticker(Symbol)
        Prices[Symbol] = float(Cotation['info']['lastPrice'])

    return Prices


def getAveragePrices():
    Cotations = fetchAssetPrices(getRelevantSymbols())
    AllCotations = list(Cotations.keys())

    averagePrices = sum([Cotations[S] for S in AllCotations]) / len(AllCotations)
    return averagePrices


def getRelevantSymbols():
    return [S for S in Binance.symbols if '/USDT' in S]


def getUserBalance(Verbose=False):
    Balance = Binance.fetch_balance()['info']['balances']
    totalUSD = 0
    Cotations = fetchAssetPrices(getRelevantSymbols())
    for Asset in Balance:
        Free, Locked = parseAsset(Asset)
        if Free or Locked:
            if Verbose:
                print(Asset)
            if Asset['asset'] == 'USDT':
                Symbol = 'USDT'
                totalAsset = Free + Locked
                assetValue = totalAsset
                if Verbose:
                    print("%.2f USDT" % totalAsset)
            else:
                Symbol = '%s/USDT' % Asset['asset']
                if Symbol in Binance.symbols:
                    price = Cotations[Symbol]
                    if Verbose:
                        print("%s price %.2f" % (Asset['asset'], price))
                    totalAsset = Free + Locked
                    assetValue = (totalAsset * price)
                else:
                    continue

            totalUSD += assetValue
            if Verbose:
                print('--')
                print(totalAsset)
                print(assetValue)
                print(totalUSD)
                print()

    return totalUSD


def loadStrategyRankings():
    W = json.load(open("gekkoStrategyRankings.json"))
    Strategies = []
    for s in W:
        S = strategyParameterSet(s)
        Strategies.append(S)
    return Strategies


def saveStrategyRankings(rankingList):
    outputList = []

    for strategy in rankingList:
        outputList.append(strategy.toJson())

    json.dump(outputList, open("gekkoStrategyRankings.json", 'w'))


def getAssets(Exchange):
    Assets = [A for A in Exchange.symbols if 'USDT' in A]
    return Assets


def parseAssets(exchangeList):
    LIST = []
    for Asset in exchangeList:
        N = Asset.split('/')
        A = {
            'EXCHANGE': 'binance',
             'ASSET': N[0],
             'CURRENCY': N[1]
        }
        LIST.append(A)

    return LIST


def generateMarketsJson(Assets, Exchange):
    Assets = getAssets(Exchange)
    marketData = []
    assetList = []
    exchangeAssetInfo = Exchange.publicGetExchangeInfo()['symbols']

    for Asset in Assets:
        pair = Asset.split('/')
        assetList.append(pair[0])
        pair.reverse()
        orderInfo = None
        for pairInfo in exchangeAssetInfo:
            if pairInfo['symbol'] == Asset.replace('/', ''):
                allFilters = {}

                for Filter in pairInfo['filters']:
                    del Filter['filterType']
                    allFilters.update(Filter)

                orderInfo = {
                    "amount": allFilters['minQty'],
                    "price": allFilters['minPrice'],
                    "order": 1
                }

                break

        if orderInfo is None:
            print("Failed to grab data for %s" % Asset)
            continue

        pairEntry = {
            "pair": pair,
            "minimalOrder": orderInfo
        }

        marketData.append(pairEntry)

    fullMarketData = {
        "assets": assetList,
        "currencies": ["USDT"],
        "markets": marketData
    }

    return fullMarketData


def getRecentOrders(Exchange, pastTimeRangeDays=2):
    userOrderHistory = []
    for Market in getAssets(Exchange):
        sinceTimestamp = (time.time() - pastTimeRangeDays * 24 * 3600) * 1000
        Orders = Exchange.fetch_my_trades(Market, since=sinceTimestamp)

        for Order in Orders:
            print(json.dumps(Order, indent=2))
            userOrderHistory.append(Order)


if __name__ == '__main__':
    totalUSD = getUserBalance()
    Strategies = loadStrategyRankings()

    getRecentOrders(Binance)
    Assets = getAssets(Binance)
    print(Assets)
    marketGekkoData = generateMarketsJson(Assets, Binance)

    with open('binance-markets.json', 'w') as F:
        json.dump(marketGekkoData, F, indent=4)

    print(totalUSD)
