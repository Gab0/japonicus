#!/bin/python

# this file contains functions for 'meta genetic algorithm',
# this acts to allow settings value manipulation via command line,
# making possible a simple GA of GAs under bash.

# TBD
from .parameterOperations import flattenParameters, expandNestedParameters


def generateCommandLineArguments(parser, settings):
    flatSettings = flattenParameters(settings)
    for Setting in flatSettings.keys():
        if type(flatSettings[Setting])  in [list, bool, tuple]:
            pass
        else:
            originalValue = flatSettings[Setting]
            parameterType = type(originalValue)
            if parameterType.__name__ == 'NoneType':
                parameterType = str
            parser.add_option("--%s" % Setting,
                              dest=Setting,
                              type=parameterType.__name__,
                              default=originalValue)

    return parser


def applyCommandLineOptionsToSettings(options, settings):
    flatSettings = flattenParameters(settings)

    for Setting in flatSettings.keys():
        if Setting in options.__dict__.keys():
            flatSettings[Setting] = options.__dict__[Setting]

    Settings = expandNestedParameters(flatSettings)
    return Settings
