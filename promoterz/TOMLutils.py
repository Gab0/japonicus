#!/bin/python
import re
import pytoml

def preprocessTOMLFile(filepath):
    f = open(filepath)
    return f


def TOMLToParameters(TOMLDATA):
    Parameters = pytoml.load(TOMLDATA)

    for Parameter in Parameters.keys():
        if type(Parameter) == str:
            if '=' in Parameter:
                Parameter = Parameter.replace('=', '')
                Parameter = float(Parameter)
            
    return Parameters


def parametersToTOML(Settings):
    Text = pytoml.dumps(Settings)
    
    return Text
