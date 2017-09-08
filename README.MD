This is a barebones implementation of genetic algorithm evolution to develop strategies for digital coin trading bot Gekko.

It generates some random configs, and evolve them by backtesting on a Gekko session via the REST API of the bot's --ui mode.

Recommended usage:
```
Open two terminals:

first, run Gekko on ui mode.

second, $cd [japonicus dir] && python evolution.py
```
If you use a UI port which is not :3000, adjust accordingly on gekkoWrapper.py.

Backtesting is parallel. It runs five at a time, or adjust it on evolution.py:90

This is written on python because of the nice DEAP module for genetic algorithm. It's worth it.. available on PIP.

