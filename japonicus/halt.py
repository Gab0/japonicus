#!/bin/python

import signal
import sys

import psutil
import os
import time

M = sys.version_info.major
m = sys.version_info.minor
if not M >= 3 or not m >= 6:
    message = 'check your python version before running japonicus.'
    message += ' Python>=3.6 is required. Python==%i.%i detected.' % (M, m)
    print(message)
    exit(1)


Aware = False


def userExit(x, y):

    parent = psutil.Process(os.getpid())
    global Aware
    if not Aware:
        print("\n\nAborted by user. (SIGINT)\n\n")
        Aware = True
    try:
        for child in parent.children(recursive=True): 
            child.kill()
        time.sleep(2)
        exit(0)
    except (SystemExit):
        raise


signal.signal(signal.SIGINT, userExit)
