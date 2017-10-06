def gekko_generations(Strategy, GenerationMethod='standard'):

    genconf=getSettings('generations')
    conf=getSettings('global')
    TargetParameters=getSettings()['strategies'][Strategy]
    # GENERATION METHOD SELECTION;
    # to easily employ various GA algorithms,
    # this base EPOCH processor loads a GenerationMethod file,
    # which should contain a genToolbox function to generate
    # fully working DEAP toolbox, and a reconstructTradeSettings
    # function to convert parameters from individue to usable strategy Settings;
    # Check promoterz/representation;

    genconf.Strategy = Strategy # ovrride strat defined on settings if needed;
    GenerationMethod = promoterz.selectRepresentationMethod(GenerationMethod)
    toolbox = GenerationMethod.getToolbox(genconf, TargetParameters)

    ageTools = promoterz.supplement.age.getToolbox(genconf.ageBoundaries)
    parallel = Pool(genconf.ParallelBacktests)

    POP = toolbox.population(n=genconf.POP_SIZE)
    W=0
    availableDataRange = getAvailableDataset(exchange_source=genconf.dataset_source)
    print("using candlestick dataset %s" % availableDataRange)
    print("%s strategy;" % Strategy)

    EvolutionStatistics={}

    stats = coreFunctions.getStatisticsMeter()

    InitialBestScores, FinalBestScores = [], []
    FirstEpochOfDataset = False
    Stats = None
    # settings_debug_min = GenerationMethod.constructPhenotype([0 for x in range(10)], Strategy)
    # settings_debug_max = GenerationMethod.constructPhenotype([100 for x in range(10)], Strategy)

    # print("DEBUG %s" % json.dumps(settings_debug_min, indent=2))
    # print("DEBUG %s" % json.dumps(settings_debug_max, indent=2))

    HallOfFame = tools.HallOfFame(30)
    bestScore = 0
    Deviation = 0
    POP_SIZE = genconf.POP_SIZE
    coreTools = promoterz.getEvolutionToolbox(HallOfFame, toolbox.population)

    print("evaluated parameters ranges %s" % promoterz.utils.flattenParameters(TargetParameters))
    while W < genconf.NBEPOCH:

        FirstEpochOfDataset = False

        # -- periodically change environment
        Z = not W % genconf.DRP and bestScore > 0.3 and not Deviation
        K = not W % (genconf.DRP*3)
        if Z or K: # SELECT NEW DATERANGE;
            if W:# SEND BEST IND TO HoF;
                BestSetting = tools.selBest(POP, 1)[0]
                HallOfFame.insert(BestSetting)
                #print(EvolutionStatistics)

                FinalBestScores.append(Stats['max'])

            DateRange = coreFunctions.getRandomDateRange(availableDataRange, genconf.deltaDays)
            print("Loading new date range;")

            print("\t%s to %s" % (DateRange['from'], DateRange['to']))
            for I in range(len(POP)):
                del POP[I].fitness.values
            toolbox.register("evaluate", coreFunctions.Evaluate,
                             GenerationMethod.constructPhenotype, DateRange)
            FirstEpochOfDataset = True
            bestScore = 0


        assert(None not in POP)
        # --hall of fame immigration;
        if random.random() < 0.2:
            POP = coreTools.ImmigrateHoF(POP)

        # --randomic immigration;
        if random.random() < 0.5:
            POP = coreTools.ImmigrateRandom((2,7), POP)


        assert(len(POP))
        # --select best individues to procreate
        offspring = tools.selTournament(POP, genconf._lambda, 2*genconf._lambda)
        offspring = [deepcopy(x) for x in offspring]

        # --modify and integrate offspring;
        offspring = algorithms.varAnd(offspring, toolbox,
                                      genconf.cxpb, genconf.mutpb)
        ageTools.zero(offspring)
        POP += offspring


        POP=promoterz.validation.validatePopulation(GenerationMethod.constructPhenotype,
                                        {Strategy:TargetParameters}, POP)
        # --evaluate individuals;
        nb_evaluated=promoterz.evaluatePopulation(POP, toolbox.evaluate, parallel)


        # --get proper evolution statistics;
        Stats=stats.compile(POP)

        # --calculate new POPSIZE;
        if W and not FirstEpochOfDataset:
            PRoFIGA = promoterz.supplement.PRoFIGA.calculatePRoFIGA(
                genconf.PRoFIGA_beta, W, genconf.NBEPOCH, EvolutionStatistics[W-1], Stats)
            POP_SIZE += int(round( POP_SIZE * PRoFIGA ))

        # --filter best inds;
        POP[:] = tools.selBest(POP, POP_SIZE)

        # --log statistcs;
        if FirstEpochOfDataset:
            InitialBestScores.append(Stats['max'])
            Stats['dateRange'] = "%s ~ %s" % (DateRange['from'], DateRange['to'])
        else:
            Stats['dateRange'] = None

        Stats['maxsize'] = POP_SIZE
        Stats['size'] = len(POP)
        EvolutionStatistics[W] = Stats
        coreFunctions.write_evolution_logs(W, Stats)

        # show information;
        print("EPOCH %i/%i\t&%i" % (W, genconf.NBEPOCH, nb_evaluated))
        statnames = [ 'max', 'avg', 'min', 'std', 'size', 'maxsize' ]

        statText = ""
        for s in range(len(statnames)):
            SNAME = statnames[s]
            SVAL = Stats[SNAME]
            statText += "%s" % coreFunctions.statisticsNames[SNAME]
            if not SVAL % 1:
                statText += " %i\t" % SVAL
            else:
                statText += " %.3f\t" % SVAL
            if s % 2:
                statText += '\n'
        print(statText)
        print('')



        bestScore = Stats['max']
        Deviation = Stats['std']
        assert(None not in POP)

        #print("POPSIZE %i" % len(POP))

        # --population ages
        qpop=len(POP)
        POP=ageTools.populationAges(POP, Stats)
        wpop=len(POP)
        print('elder %i' % (qpop-wpop))

        assert(len(POP))
        assert(None not in POP)

        W+=1
