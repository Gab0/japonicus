#!/bin/python

from promoterz import *

from coreFunctions import Evaluate

def reconstructTradeSettings(Individue):
    Settings = {}

    PromotersPath = {v: k for k, v in Individue.PromoterMap.items()}
    #print(PromotersPath)
    #print(Individue[:])
    Promoters = list(PromotersPath.keys())
    for C in Individue:
        for BP in range(len(C)):
            if C[BP] in Promoters:
                read_window = C[BP+1:BP+3]
                read_window = [V for V in read_window if type(V) == int and V < 33]
                Value = sum(read_window)
                Settings[PromotersPath[C[BP]]] = Value

    _Settings = {}

    for K in Settings.keys():
        if '.' in K:
            Q = K.split('.')
            if not Q[0] in _Settings.keys():
                _Settings[Q[0]] = {}
            _Settings[Q[0]][Q[1]] = Settings[K]
        else:
            _Settings[K] = Settings[K]

    Settings = {Individue.Strategy: _Settings}
    return Settings

