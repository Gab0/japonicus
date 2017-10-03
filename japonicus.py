#!/bin/python

import optparse
from time import sleep
from random import choice, randrange
from subprocess import Popen, PIPE
from threading import Thread
from Settings import getSettings
from evolution_generations import gekko_generations

from os import chdir, path
chdir(path.dirname(path.realpath(__file__)))

import web
settings = getSettings()
#from evolution_bayes import gekko_bayesian
parser = optparse.OptionParser()

parser.add_option('-g', '--genetic', dest='genetic_algorithm',
                  action='store_true', default=False)
parser.add_option('-c', '--chromosome', dest='chromosome_mode',
                  action='store_true', default=False)
parser.add_option('-b', '--bayesian', dest='bayesian_optimization',
                  action='store_true', default=False)
parser.add_option('-k', '--gekko', dest='spawn_gekko',
                  action='store_true', default=False)
parser.add_option('-w', '--web', dest='spawn_web',
                  action='store_true', default=False)
parser.add_option('--repeat <x>', dest='repeater',
                  type=int, default=1)
parser.add_option('--strat <strat>', dest='strategy')

options, args = parser.parse_args()

gekko_server = None
web_server = None
strat = choice(settings['global']['Strategies'])\
        if options.strategy == 'all'\
        else options.strategy

if options.spawn_gekko:
   if options.genetic_algorithm or options.bayesian_optimization:
        gekko_args = ['node',
                     '--max-old-space-size=8192',
                     settings['global']['gekkoPath']+'/web/server.js']

        gekko_server = Popen(gekko_args, stdin=PIPE, stdout=PIPE)
        sleep(2)

if options.spawn_web:
   #web_args = ['python', 'web.py']
   #web_server = Popen(web_args, stdin=PIPE, stdout=PIPE)
   print("WEBSERVER MODE")
   APP = web.run_server()
   P = Thread(target=APP.server.run, kwargs={'debug':False})
   P.start()

   sleep(2)

if options.genetic_algorithm:
   GenerationMethod = 'chromosome' if options.chromosome_mode else 'standard'
   if strat == None:
      strat = settings['generations']['Strategy']
   for s in range(options.repeater):
      gekko_generations(strat, GenerationMethod)

elif options.bayesian_optimization:
    import evolution_bayes
    if strat == None:
       strat = settings['bayesian']['Strategy']
    for s in range(options.repeater):
       evolution_bayes.gekko_bayesian(strat)

if options.spawn_web:
    print('Statistics info server still runs...')

