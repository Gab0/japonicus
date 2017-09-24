This is a barebones implementation of genetic algorithm evolution to develop strategies for digital coin trading bot Gekko. [https://github.com/askmike/gekko]

It generates random configs, and evolve them by backtesting on a Gekko session via the REST API of gekko's user interface. Genetic algorithm and bayesian optimization are evolution choices.

Recommended usage:
```
Open two terminals;

T.1 -> run Gekko on ui mode.

T.2 -> $cd [japonicus dir]
       $python japonicus.py [-g|-b] [-c] [-k] [--repeat <X>] [--strat <Strategy>] [-w]
       
    -g for genetic algorithm;
    -b for bayesian optimization;

    -c to use alternative genetic algorithm;
    
    -k launches a child gekko instance, so no need for the first terminal;
    --strat choose one strat to run;
    --repeat to run genetic algorithm X times; then just check evolution.log;
    
    -w launches a neat dash/flask web server @ your local machine, which can be accessed via  webbrowser. 
           Address is shown on the first line of console output. (likely http://localhost:5000)
       
    
```
If your Gekko UI http port is not :3000, adjust accordingly on gekkoWrapper.py.

Backtesting is parallel. It runs five at a time, or adjust it on settings.py

This is written on python because of the nice DEAP module for genetic algorithm. It's worth it.. available on PIP.

