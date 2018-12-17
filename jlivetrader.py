#!/bin/python
import os
import optparse
import json

import livetrader.exchangeMonitor
import livetrader.gekkoTrigger
import livetrader.gekkoChecker

try:
    import livetrader.strategyRanker
except Exception:
    pass

parser = optparse.OptionParser()

parser.add_option('-b', '--balance',
                  dest='balanceChecker', action='store_true', default=False)

parser.add_option('-t', '--trigger <strategy>',
                  dest='botTrigger', type='str', default='')

parser.add_option('-c', dest='runningBotChecker',
                  action='store_true', default=False)

parser.add_option('-l', dest='tradingBot', action='store_true',
                  default=False)

parser.add_option('--candleSize <cs>',
                  dest='candleSize', type='int', default=5)

parser.add_option('--strat <strategy>', dest='strategy',
                  type='str', default='')

parser.add_option('--param <parameters>', dest='alternativeParameters',
                  type='str', default=None)

parser.add_option('-k', dest='killGekkoBots', action='store_true',
                  default=False,
                  help='Destroy all running gekko bot instances.')

parser.add_option('-s', dest='viewLastTrades', action='store_true',
                  default=False,
                  help='Show last trades done by bots.')

options, args = parser.parse_args()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    exchange = livetrader.exchangeMonitor.Exchange('binance')

    if options.balanceChecker:
        totalUSD = exchange.getUserBalance()

        print("net weight at %s: US$T%.2f" % (
            exchange.name,
            totalUSD)
        )

    if options.botTrigger:
        allPairs = exchange.getAssets()
        assetCurrencyPairs = exchange.parseAssets(allPairs)
        Stratlist = [options.botTrigger]

        exchangeConfPath =\
            exchange.conf.binanceAssetCurrencyTargetFilePath
        if exchangeConfPath:
            exchangeMarketData = exchange.generateMarketsJson(
                assetCurrencyPairs)
            exchangeConfPath = os.path.join(exchangeConfPath,
                                            'binance-markets.json')

            with open(exchangeConfPath, 'w') as F:
                json.dump(exchangeMarketData, F, indent=2)

        livetrader.gekkoTrigger.launchBatchTradingBots(
            assetCurrencyPairs,
            Stratlist,
            options
        )

    if options.runningBotChecker:
        ranker = livetrader.strategyRanker.strategyRanker()
        ranker.loadStrategyRankings()
        userOrderHistory = exchange.getRecentOrders()
        for M in userOrderHistory.keys():
            marketOrderHistory = userOrderHistory[M]
            if marketOrderHistory:
                information = json.dumps(marketOrderHistory, indent=2)
                print(information)

        livetrader.gekkoChecker.checkGekkoRunningBots(exchange,
                                                      ranker, options)
    if options.killGekkoBots:
        livetrader.gekkoChecker.stopGekkoBots()

    if options.viewLastTrades:
        Orders = exchange.getRecentOrders()
        print(json.dumps(Orders, indent=2))


