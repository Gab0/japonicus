#!/bin/python
import promoterz
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


