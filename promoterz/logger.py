#!/bin/bash

import datetime

class Logger():
    def __init__(self):
        date = datetime.datetime.now()
        self.logfilename = "logs/genetic%s" % str(date)

        self.File = open(self.logfilename, 'w')

    def log(self, message):
        self.File.write(message+'\n')
        print(message)
