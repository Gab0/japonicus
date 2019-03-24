#!/bin/python
import evaluation


def showBacktestResult(backtestResult, dataset=None):
    messageBackbone = ''.join([
        'Test on random candles...  ',
        'relativeProfit: %.3f \t',
        'nbTrades: %.1f\t',
        'sharpe: %.2f'
    ])

    message = messageBackbone % (
        backtestResult['relativeProfit'],
        backtestResult['trades'],
        backtestResult['sharpe']
    )

    if dataset:
        message += "\n\t\t%s\t%s" % (dataset.textDaterange(),
                                     dataset.textSpecifications())

    return message


def parseDatasetInfo(purpose, candlestickDataset):
    textdaterange = evaluation.gekko.datasetOperations.dateRangeToText(
        candlestickDataset.daterange)
    print()
    Text = "\n%s candlestick dataset %s\n" % (purpose, textdaterange)
    Text += candlestickDataset.textSpecifications() + '\n'
    return Text


def showTitleDisclaimer(backtestsettings, VERSION):
    TITLE = """\tGEKKO
        ██╗ █████╗ ██████╗  ██████╗ ███╗   ██╗██╗ ██████╗██╗   ██╗███████╗
        ██║██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██║██╔════╝██║   ██║██╔════╝
        ██║███████║██████╔╝██║   ██║██╔██╗ ██║██║██║     ██║   ██║███████╗
   ██   ██║██╔══██║██╔═══╝ ██║   ██║██║╚██╗██║██║██║     ██║   ██║╚════██║
   ╚█████╔╝██║  ██║██║     ╚██████╔╝██║ ╚████║██║╚██████╗╚██████╔╝███████║
    ╚════╝ ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═════╝ ╚══════╝"""
    try:
        print(TITLE)
    except UnicodeEncodeError or SyntaxError:
        print("\nJAPONICUS\n")
    print('\t' * 8 + 'v%.2f' % VERSION)
    print()

    profitDisclaimer = "The profits reported here depends on backtest interpreter function;"
    interpreterFuncName = backtestsettings['interpreteBacktestProfit']
    interpreterInfo = evaluation.gekko.backtest.getInterpreterBacktestInfo(
        interpreterFuncName)

    print("%s \n\t%s" % (profitDisclaimer, interpreterInfo))

