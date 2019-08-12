#!/bin/python
import evaluation



def showTitleDisclaimer(backtestsettings, VERSION):
    TITLE = """
        ██╗ █████╗ ██████╗  ██████╗ ███╗   ██╗██╗ ██████╗██╗   ██╗███████╗
        ██║██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██║██╔════╝██║   ██║██╔════╝
        ██║███████║██████╔╝██║   ██║██╔██╗ ██║██║██║     ██║   ██║███████╗
   ██   ██║██╔══██║██╔═══╝ ██║   ██║██║╚██╗██║██║██║     ██║   ██║╚════██║
   ╚█████╔╝██║  ██║██║     ╚██████╔╝██║ ╚████║██║╚██████╗╚██████╔╝███████║
    ╚════╝ ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
    """

    TITLE += "\t EVOLUTIONARY GENETIC ALGORITHMS"

    try:
        print(TITLE, end="")
    except UnicodeEncodeError or SyntaxError:
        print("\nJAPONICUS\n")
    print('\t' * 4 + 'v%.2f' % VERSION)
    print()

    profitDisclaimer = "The profits reported here depends on backtest interpreter function;"
    interpreterFuncName = backtestsettings['interpreteBacktestProfit']
    interpreterInfo = evaluation.gekko.backtest.getInterpreterBacktestInfo(
        interpreterFuncName)

    print("%s \n\t%s\n" % (profitDisclaimer, interpreterInfo))

