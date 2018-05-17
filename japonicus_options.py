
import optparse
import Settings

parser = optparse.OptionParser()
parser.add_option(
    '-g', '--genetic', dest='genetic_algorithm', action='store_true', default=False,
    help="Genetic Algorithm evolution mode."
)
parser.add_option(
    '-c', '--chromosome', dest='chromosome_mode', action='store_true', default=False,
    help="Alternative internal representation of parameters for Genetic Algorithm mode."
)
parser.add_option(
    '-b', '--bayesian', dest='bayesian_optimization', action='store_true', default=False,
    help='Bayesian evolution mode.'
)
parser.add_option(
    '-k', '--gekko', dest='spawn_gekko', action='store_true', default=False,
    help="Launch gekko instance."

)
parser.add_option(
    '-r', '--random', dest='random_strategy', action='store_true', default=False,
    help="Run on random strategy."
)
parser.add_option(
    '-e', '--benchmark', dest='benchmarkMode', action='store_true',
    default=False,
    help="Run GA benchmark mode. Strategy names are restricted to specific strats."
)
parser.add_option(
    '-w', '--web', dest='spawn_web', action='store_true', default=False,
    help="Launch japonicus web server showing evolutionary statistics."
)
parser.add_option('--repeat <x>', dest='repeater', type=int, default=1)
parser.add_option('--strat <strat>', dest='strategy', default=None)
parser.add_option('--skeleton <skeleton>', dest='skeleton', default=None)
genconf = Settings.getSettings()['generations']
'''
for config in genconf.keys():
    if type(genconf[config]) not in [dict, list, bool, tuple]:
        parser.add_option(
            "--%s <value>" % config,
            dest=config,
            type=type(genconf[config]),
            default=None,
        )
'''
