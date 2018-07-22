#!/bin/python

import signal
import sys

M = sys.version_info.major
m = sys.version_info.minor
if not M >= 3 or not m >= 6:
    exit('check your python version before running japonicus.' +
         ' Python>=3.6 is required. Python==%i.%i detected.' % (M, m))

signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
