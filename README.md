This is a barebones implementation of genetic algorithm evolution to develop strategies for digital coin trading bot Gekko. [https://github.com/askmike/gekko]

It generates random configs, and evolve them by backtesting on a Gekko session via the REST API of gekko's user interface. Genetic algorithm and bayesian optimization are evolution choices.

Recommended usage:
```
Open two terminals;

T.1 -> run Gekko on ui mode, or just its webserver:
$node gekko.js --ui
or
$node web/server.js

T.2 -> $cd [japonicus dir]
       $python japonicus.py [-g|-b] [-c] [-k] [--repeat <X>] [--strat <Strategy>] [-w]
       
    -g for genetic algorithm;
    -b for bayesian optimization;

    -c to use an alternative, experimental (probably weaker) genetic algorithm;
    
    -k launches a child gekko instance, so no need for the first terminal;
    
    --strat choose one strat to run [deprecated, set it on Settings.py];
    --repeat to run genetic algorithm X times; then just check evolution.log;
    
    -w launches a neat dash/flask web server @ your local machine, which can be accessed via  webbrowser. 
           Address is shown on the first line of console output. (likely http://localhost:5000)
       
    
```
If your Gekko UI http port is not :3000, adjust accordingly on gekkoWrapper.py.

Backtesting is parallel. It runs five at a time, or adjust it on Settings.py

This is written on python because of the nice DEAP module for genetic algorithm. It's worth it.. available on PIP.

The full parallel backtesting is now complete. It sends backtest requests across the internet to several machines running Gekko. 
Intended to use with Ansible-playbook + Amazon EC2 AWS machines. <br>
At japonicus side, you should provide Ansible's `hosts` inventory file, containing
the IPs of running machines (a simple list). <br>
Those machines should be already fully configured, running Gekko, and loaded with the same candlestick data (history)
files you have on local Gekko;<br>
I can't make a tutorial for this yet, anyone interested pm me. An AWS slave machine with same
capacity as local machine can cut EPOCH runningtimes to 66% the original time. Yet very experimental stuff...<br>
YML playbook file to get gekko running on Amazon AMI Linux is at root folder (set the path to your local gekko history @ line 57); 


Known good gekko strategies to run with this (choose @ Settings.py):
 - PPO
 - RSI
 
Better avoid those:
- DEMA
- MACD
