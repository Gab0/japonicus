This is a barebones implementation of genetic algorithm evolution to develop strategies for digital coin trading bot Gekko.

It generates some random configs, and evolve them by backtesting on a Gekko session via the REST API of the bot's --ui mode.

Recommended usage:
```
Open two terminals:

1st$ cd [gekko dir] && node gekko --ui

2nd$ cd [japonicus dir] && python evolution.py
```
If you use a UI port which is not :3000, adjust accordingly on gekkoWrapper.py.

The backtesting is serial (one at a time). I'm not aware of node.js multicore capabilities, if it is possible to increase speed by running multiple parallel backtestings, would be not hard to just open multiple Gekkos on diverse ports and develop this script to follow. So fork it or let me know..

This is written on python because of the nice DEAP module for genetic algorithm. It's worth it.. available on PIP.

