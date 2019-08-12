#!/bin/python
import time
import random
import itertools

from multiprocessing import Pool, TimeoutError
from multiprocessing.pool import ThreadPool


class EvaluationPool():

    def __init__(self,
                 World,
                 Urls, poolsize, individual_info):
        self.World = World

        self.Urls = Urls
        self.lasttimes = [0 for x in Urls]
        self.lasttimesperind = [0 for x in Urls]
        self.poolsizes = [poolsize for x in Urls]
        self.individual_info = individual_info

    def evaluateBackend(self, datasets, I, inds):
        stime = time.time()
        dateInds = list(itertools.product(datasets, inds))
        # print(list(dateInds))
        Q = [
            ([dataset], Ind, self.Urls[I])
            for dataset, Ind in dateInds
        ]
        P = Pool(self.poolsizes[I])
        fitnesses = P.starmap(self.World.tools.Evaluate, Q)
        P.close()
        P.join()
        delta_time = time.time() - stime
        return fitnesses, delta_time

    def evaluatePopulation(self, locale):
        individues_to_simulate = [
            ind for ind in locale.population if not ind.fitness.valid
        ]
        props = self.distributeIndividuals(individues_to_simulate)
        args = [
            [
                locale.Dataset,
                I,
                props[I],
            ]
            for I in range(len(self.Urls))
        ]
        pool = ThreadPool(len(self.Urls))
        results = []
        try:
            for A in args:
                results.append(pool.apply_async(self.evaluateBackend, A))
            pool.close()
        except (SystemExit, KeyboardInterrupt):
            print("Aborted by user.")
            exit(0)
        TimedOut = []
        for A in range(len(results)):
            try:
                perindTime = 3 * self.lasttimesperind[A]\
                             if self.lasttimesperind[A] else 12
                timeout = perindTime * len(props[A])\
                    if A else None  # no timeout for local machine;
                results[A] = results[A].get(timeout=timeout)
            except TimeoutError:  # Timeout: remote machine is dead;
                print("Machine timeouts!")
                args[A][1] = 0  # Set to evaluate @ local machine
                results[A] = self.evaluateBackend(* args[A])
                TimedOut.append(A)
        pool.join()
        TotalNumberOfTrades = 0
        for PoolIndex in range(len(results)):
            for i, fit in enumerate(results[PoolIndex][0]):
                if self.individual_info:
                    print(self.World.tools.showIndividue(fit))
                self.World.tools.ApplyResult(fit, props[PoolIndex][i])

                TotalNumberOfTrades += fit['trades']
            self.lasttimes[PoolIndex] = results[PoolIndex][1]
            L = len(props[PoolIndex])
            self.lasttimesperind[PoolIndex] =\
                self.lasttimes[PoolIndex] / L if L else 5
        F = [x.fitness.valid for x in individues_to_simulate]
        assert (all(F))
        for T in TimedOut:
            self.ejectURL(T)
        N = len(individues_to_simulate)
        # RECORD NUMBER OF EVALUATIONS;
        locale.World.totalEvaluations += N
        # CALCULATE AVERAGE TRADE NUMBER;
        averageTrades = TotalNumberOfTrades / max(1, N)
        return N, averageTrades
