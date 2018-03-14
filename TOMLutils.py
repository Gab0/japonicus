#!/bin/python
import re

def preprocessTOMLFile(filepath):
    f = open(filepath)
    f = f.read()
    f = f.split('\n')
    return f

def TOMLToParameters(TOMLLines):
    Parameters = {}
    subkey = None
    parseTuple = lambda s: (float(x) for x in s[1:-1].split(','))
    for Line in TOMLLines:
        
        if Line.startswith('#'):
            continue
        sub = re.findall("\[\w+\]", Line)
        if sub:
            subkey = sub[0][1:-1]
            if subkey not in Parameters.keys():
                Parameters[subkey] = {}
        elif '=' in Line:

            target = Parameters[subkey] if subkey else Parameters
            L = Line.split(' = ') if ' = ' in Line else Line.split('=')
            
            target[L[0]] = parseTuple(L[1]) if '(' in L[1] else float(L[1]) 
            
        else:
            subkey = None

    return Parameters

def parametersToTOML(Settings):
    text = []
    toParameter = lambda name, value: "%s = %f" % (name,value)

    # print("{{ %s }}" % Settings[Strat])
    def iterate(base):

        Settingskeys = base.keys()
        Settingskeys = sorted(list(Settingskeys),
                          key= lambda x: type(base[x]) == dict, reverse=False)

        for W in Settingskeys:
            Q = base[W]
            if type(Q) == dict:
                text.append("[%s]" % W)
                iterate(Q)
                text.append('')
            else:
                text.append("%s = %s" % (W, Q))

    iterate(Settings)
    return '\n'.join(text)

