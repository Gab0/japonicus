#!/bin/python

import optparse
from time import sleep
from random import choice, randrange
from subprocess import Popen, PIPE
from threading import Thread
from Settings import getSettings
from evolution_generations import gekko_generations

import datetime
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
                  action='store_true', default=False),
parser.add_option('-r', '--random', dest='random_strategy',
                  action='store_true', default=False)
parser.add_option('-w', '--web', dest='spawn_web',
                  action='store_true', default=False)
parser.add_option('--repeat <x>', dest='repeater',
                  type=int, default=1)
parser.add_option('--strat <strat>', dest='strategy', default=None)

options, args = parser.parse_args()

gekko_server = None
web_server = None

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
   P = Thread(target=APP.server.run, kwargs={'debug':False, 'host':'0.0.0.0'})
   P.start()

   sleep(2)

markzero_time = datetime.datetime.now()
print("The profits reported here are in relation to market price change;\n"+\
      "\ti.e shown profit = { backtest profit } - { market profit in evaluated candlestick period };")

if options.genetic_algorithm:
   GenerationMethod = 'chromosome' if options.chromosome_mode else 'oldschool'

   if options.random_strategy:
      Strategy = choice(list(settings['strategies'].keys()))
   else:
      Strategy = options.strategy

   for s in range(options.repeater):
      gekko_generations(Strategy, GenerationMethod)

elif options.bayesian_optimization:
   import evolutio_bayes
   if options.strat:
      settings['bayesian']['Strategy'] = options.strat
   for s in range(options.repeater):
      evolution_bayes.gekko_bayesian(strat)

deltatime = datetime.datetime.now() - markzero_time
print("Running took %i seconds." % deltatime.seconds)

if options.spawn_web:
    print('Statistics info server still runs...')

