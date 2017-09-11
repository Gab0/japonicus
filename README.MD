This is a barebones implementation of genetic algorithm evolution to develop strategies for digital coin trading bot Gekko.

It generates some random configs, and evolve them by backtesting on a Gekko session via the REST API of the bot's --ui mode. Genetic algorithm and bayesian optimization are evolution choices.

Recommended usage:
```
Open two terminals:

T.1 -> run Gekko on ui mode.

T.2 -> $cd [japonicus dir]
       $python evolution.py [-g|-b] [-k] [--repeat <X>]
       
    -g for genetic algorithm;
    -b for bayesian optimization;

    -k launches a child gekko instance, so no need for the first terminal;
    
    --repeat to run genetic algorithm X times; then just check evolution.log;
```
If you use a UI port which is not :3000, adjust accordingly on gekkoWrapper.py.

Backtesting is parallel. It runs five at a time, or adjust it on settings.py

This is written on python because of the nice DEAP module for genetic algorithm. It's worth it.. available on PIP.

