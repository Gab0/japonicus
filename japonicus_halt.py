#!/bin/python

import signal
import sys

if not sys.version_info.major >= 3 or not sys.version_info.minor >= 6:
    exit('check your python version before running japonicus.' +
         ' Python>=3.6 is required.')

signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))
