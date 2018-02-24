#!/bin/bash

import datetime
import os

class Logger():
    def __init__(self):
        date = datetime.datetime.now()
        if not os.path.isdir('logs'):
            os.mkdir('logs')
        self.logfilename = "logs/genetic%s" % str(date)

        self.File = open(self.logfilename, 'w')

    def log(self, message):
        self.File.write(message+'\n')
        print(message)
