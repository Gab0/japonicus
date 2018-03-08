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

        self.Header = ""
        self.Summary = ""
        self.Body = ""


    def log(self, message, target="Body", show=True):
        self.__dict__[target] += message+'\n'
        if show:
            print(message)

    def updateFile(self):
        File = open('logs/%s.log' % self.logfilename, 'w')

        File.write(self.Header)
        File.write(self.Summary)
        File.write(self.Body)

        File.close()

    def write_evolution_logs(self, i, stats, localeName):
        filename = "logs/%s_%s.csv" % (self.logfilename, localeName)
        df = pd.DataFrame(stats)
        df.to_csv(filename)
