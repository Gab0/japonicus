#!/bin/python

import optparse
from time import sleep
from random import choice
from subprocess import Popen, PIPE

from Settings import getSettings
from evolution_generations import gekko_generations

from os import chdir, path
chdir(path.dirname(path.realpath(__file__)))

settings = getSettings()
#from evolution_bayes import gekko_bayesian
parser = optparse.OptionParser()

parser.add_option('-g', '--genetic', dest='GeneticAlgorithm',
                  action='store_true', default=False)
parser.add_option('-b', '--bayesian', dest='BayesianOptimization',
                  action='store_true', default=False)
parser.add_option('-k', '--gekko', dest='SpawnGekko',
                  action='store_true', default=False)
parser.add_option('--repeat <X>', dest='Repeater',
                  type=int, default=1)
parser.add_option('--strat <strat>', dest='Strategy',
                  default=settings['generations']['Strategy'])
                  
options, args = parser.parse_args()

G=None
if options.SpawnGekko:
   if options.GeneticAlgorithm or options.BayesianOptimization:
        GekkoArgs = ['node',
                     '--max-old-space-size=8192',
                     settings['global']['gekkoPath']+'/web/server.js']

        G = Popen(GekkoArgs, stdin=PIPE, stdout=PIPE)
        sleep(2)
if options.GeneticAlgorithm:
    for S in range(options.Repeater):
        Strat = choice(settings['global']['Strategies'])\
                if options.Strategy == 'all'\
                else options.Strategy
        gekko_generations(Strat)
elif options.BayesianOptimization:
    import evolution_bayes
    evolution_bayes.gekko_bayesian()

if G:
    G.kill()
