#!/bin/python

import datetime
import os
import pandas as pd
class Logger():
    def __init__(self, logfilename):
        date = datetime.datetime.now()
        if not os.path.isdir('logs'):
            os.mkdir('logs')

        self.logfilename = logfilename

        self.File = open('logs/%s.log' % self.logfilename, 'w')

    def log(self, message, show=True):
        self.File.write(message+'\n')
        print(message)

    def write_evolution_logs(self, i, stats, localeName):
        filename = "logs/%s_%s.csv" % (self.logfilename, localeName)
        df = pd.DataFrame(stats)
        df.to_csv(filename)
