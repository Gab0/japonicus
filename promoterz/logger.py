#!/bin/python
import datetime
import os
import csv


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
            if not self.Online:
                os.mkdir('logs/%s' % self.logfilename)
                os.mkdir('logs/%s/results' % self.logfilename)
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
        File = open('logs/%s/japonicus.log' % self.logfilename, 'w')
        for segment in [self.Header, self.Summary, self.Body]:
            File.write(segment + '\n')

        File.close()

    def write_evolution_logs(self, i, stats, localeName):
        filename = "logs/%s/%s.csv" % (self.logfilename, localeName)
        if stats:
            fieldnames = list(stats[0].keys())
            with open(filename, 'w') as f:
                df = csv.DictWriter(f, fieldnames)
                df.writeheader()
                df.writerows(stats)

    def saveParameters(self, filename, content):
        filename = "logs/%s/results/%s.toml" % (self.logfilename, filename)
        File = open(filename, 'w')
        File.write(content)
        File.close()
