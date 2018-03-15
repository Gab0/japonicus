#!/bin/python
from .API import httpPost


def interpreteBacktestProfitv1(backtest):
    return backtest['relativeProfit']


def interpreteBacktestProfitv2(backtest):
    return backtest['relativeProfit'] - backtest['market']


def interpreteBacktestProfitv3(backtest):
    if backtest['relativeProfit'] < 0 and backtest['market'] < 0:
        return backtest['relativeProfit']

    else:
        return backtest['relativeProfit'] - backtest['market']


def runBacktest(
    GekkoInstanceUrl,
    TradeSetting,
    Database,
    DateRange,
    candleSize=10,
    gekko_config=None,
    Debug=False,
):
    gekko_config = createConfig(
        TradeSetting, Database, DateRange, candleSize, gekko_config, Debug
    )
    url = GekkoInstanceUrl + '/api/backtest'
    result = httpPost(url, gekko_config)
    # sometime report is False(not dict)
    if type(result['report']) is bool:
        print("Warning: report not found, probable Gekko fail!")
        print(DateRange)
        # That fail is so rare that has no impact.. still happens randomly;
        return {
            'relativeProfit': 0, 'market': 0, 'trades': 0, 'sharpe': 0
        }  # fake backtest report

    # rProfit = result['report']['relativeProfit']
    #nbTransactions = result['report']['trades']
    #market = result['report']['market']
    return result['report']


def Evaluate(genconf, Database, DateRange, phenotype, GekkoInstanceUrl):
    # IndividualToSettings(IND, STRAT) is a function that depends on GA algorithm,
    # so should be provided;
    result = [
        runBacktest(
            GekkoInstanceUrl,
            phenotype,
            Database,
            DR,
            candleSize=genconf.candleSize,
            Debug=genconf.gekkoDebug,
        )
        for DR in DateRange
    ]
    interpreter = {
        'v1': interpreteBacktestProfitv1,
        'v2': interpreteBacktestProfitv2,
        'v3': interpreteBacktestProfitv3,
    }
    # --INTERPRETE BACKTEST RESULT;
    RelativeProfits = [interpreter[genconf.interpreteBacktestProfit](R) for R in result]
    avgTrades = sum([R['trades'] for R in result]) / len(DateRange)
    mRelativeProfit = sum(RelativeProfits) / len(RelativeProfits)
    avgSharpe = sum([R['sharpe'] for R in result if R['sharpe']]) / len(DateRange)
    return {'relativeProfit': mRelativeProfit, 'sharpe': avgSharpe, 'trades': avgTrades}


def createConfig(
    TradeSetting, Database, DateRange, candleSize=10, gekko_config=None, Debug=False
):
    TradeMethod = list(TradeSetting.keys())[0]
    CONFIG = {
        "gekkoConfig": {
            "debug": Debug,
            "info": Debug,
            "watch": Database,
            "paperTrader": {
                "fee": 0.25,  # declare deprecated 'fee' so keeps working w/ old gekko;
                "feeMaker": 0.15,
                "feeTaker": 0.25,
                "feeUsing": 'maker',
                "slippage": 0.05,
                "simulationBalance": {"asset": 1, "currency": 100},
                "reportRoundtrips": True,
                "enabled": True,
            },
            "tradingAdvisor": {
                "enabled": True,
                "method": TradeMethod,
                "candleSize": candleSize,  # candleSize: smaller = heavier computation + better possible results;
                "historySize": 10,
            },
            TradeMethod: TradeSetting[TradeMethod],
            "backtest": {"daterange": DateRange},
            "performanceAnalyzer": {"riskFreeReturn": 2, "enabled": True},
            "valid": True,
        },
        "data": {
            "candleProps": [
                "id", "start", "open", "high", "low", "close", "vwp", "volume", "trades"
            ],
            "indicatorResults": True,
            "report": True,
            "roundtrips": False,
            "trades": True,
        },
    }
    if gekko_config == None:
        gekko_config = CONFIG
    return gekko_config
