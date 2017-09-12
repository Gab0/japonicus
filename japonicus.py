#!/bin/python

import optparse
from time import sleep

from subprocess import Popen, PIPE

from Settings import getSettings
from evolution_generations import gekko_generations

from os import chdir, path
chdir(path.dirname(path.realpath(__file__)))

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
                  
options, args = parser.parse_args()

settings = getSettings()['global']
G=None
if options.SpawnGekko:
   if options.GeneticAlgorithm or options.BayesianOptimization:
        GekkoArgs = ['node',
                     '--max-old-space-size=8192',
                     settings['gekkoPath']+'/web/server.js']

        G = Popen(GekkoArgs, stdin=PIPE, stdout=PIPE)
        sleep(2)
if options.GeneticAlgorithm:
    for S in range(options.Repeater):
        gekko_generations()
elif options.BayesianOptimization:
    import evolution_bayes
    evolution_bayes.gekko_bayesian()

if G:
    G.kill()
