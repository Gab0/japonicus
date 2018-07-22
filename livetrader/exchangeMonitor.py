#!/bin/python
import ccxt
import json
import Settings
import time


class Exchange():
    def __init__(self, name):
        self.name = name
        self.conf = Settings.makeSettings(Settings.loadTomlSettings(name))
        secret = open(self.conf.credentialsFilePath).read()
        secret = secret.split('\n')
        self.API = ccxt.binance({
            'apiKey': secret[0],
            'secret': secret[1]
        })
        self.API.load_markets()

    def getCotations(self):
        return self.fetchAssetPrices(self.getMarketsOfCurrency())

    def parseAsset(self, Asset):
        P = [float(Asset[code]) for code in ['free', 'locked']]
        return P[0], P[1]

    def fetchAssetPrices(self, Symbols):
        Prices = {}
        for Symbol in Symbols:
            Cotation = self.API.fetch_ticker(Symbol)
            Prices[Symbol] = float(Cotation['info']['lastPrice'])

        return Prices

    def getAveragePrices(self):
        Cotations = self.getCotations()
        AllCotations = list(Cotations.keys())

        averagePrices = sum([Cotations[S] for S in AllCotations]) / len(AllCotations)
        return averagePrices

    def getMarketsOfCurrency(self, currency='USDT'):
        return [S for S in self.API.symbols if '/%s' % currency in S]

    def getUserBalance(self, Verbose=False):
        Balance = self.API.fetch_balance()['info']['balances']
        totalUSD = 0
        Cotations = self.getCotations()

        for Asset in Balance:
            Free, Locked = self.parseAsset(Asset)
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
                    if Symbol in self.API.symbols:
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

    def getAssets(self):
        Assets = [A for A in self.API.symbols if 'USDT' in A]
        return Assets

    def parseAssets(self, assets):
        LIST = []
        for Asset in assets:
            N = Asset.split('/')
            A = {
                'EXCHANGE': self.name,
                'ASSET': N[0],
                'CURRENCY': N[1]
            }
            LIST.append(A)

        return LIST

    def generateMarketsJson(self, Assets):
        Assets = self.getAssets()
        marketData = []
        assetList = []
        exchangeAssetInfo = self.API.publicGetExchangeInfo()['symbols']

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

    def getRecentOrders(self, pastTimeRangeDays=2):
        userOrderHistory = {}
        for Market in self.getAssets():
            pastTimeRange = pastTimeRangeDays * 24 * 3600
            sinceTimestamp = (time.time() - pastTimeRange) * 1000
            Orders = self.API.fetch_my_trades(Market, since=sinceTimestamp)

            userOrderHistory[Market] = Orders

        return userOrderHistory

    def getPriceHistory(self):
        candlestickData = {}
        for Market in self.getAssets():
            candlestickData[Market] = self.API.fetch_ohlcv(Market)

        return candlestickData
