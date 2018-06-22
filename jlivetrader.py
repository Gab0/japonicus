#!/bin/python
import os
import optparse

import livetrader.exchangeMonitor
import livetrader.gekkoTrigger
import livetrader.gekkoChecker

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


options, args = parser.parse_args()


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if options.balanceChecker:
        totalUSD = livetrader.exchangeMonitor.getUserBalance()
        print("net weight at %s: US$T%.2f" % (livetrader.exchangeMonitor.Binance.name,
                                              totalUSD))

    if options.botTrigger:
        allPairs = livetrader.exchangeMonitor.getAssets(livetrader.exchangeMonitor.Binance)
        assetCurrencyPairs = livetrader.exchangeMonitor.parseAssets(allPairs)
        Stratlist = [options.botTrigger]

        livetrader.gekkoTrigger.launchBatchTradingBots(
            assetCurrencyPairs,
            Stratlist,
            parameterName=options.alternativeParameters
        )
    if options.runningBotChecker:
        livetrader.gekkoChecker.checkGekkoRunningBots()
