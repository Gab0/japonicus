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
        self.Online = False

    def log(self, message, target="Body", show=True, replace=False):
        if target == "Body":
            # now the log has value to be written.
            self.Online = True

        if replace:
            self.__dict__[target] = message
        else:
            self.__dict__[target] += message + '\n'
        if show:
            print(message)

    def updateFile(self):
        if not self.Online:
            return
        File = open('logs/%s.log' % self.logfilename, 'w')
        File.write(self.Header)
        File.write(self.Summary)
        File.write(self.Body)
        File.close()

    def write_evolution_logs(self, i, stats, localeName):
        filename = "logs/%s_%s.csv" % (self.logfilename, localeName)
        df = pd.DataFrame(stats)
        df.to_csv(filename)
