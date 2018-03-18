


### What is japonicus and what it does
This is an implementation of genetic algorithm & bayesian evolution to develop strategies for digital coin trading bot <a href="https://github.com/askmike/gekko">Gekko</a>.

So you make a good strat, or get one from the internetz. Make sure its good, because this is not about miracles.

If you get good profit on strat standard settings or some random settings you made up, japonicus can find some setting set that improves the strategy, on some specific market/currency or overall.

## Instructions
Japonicus works on `python>=3.6`!
Check wiki for instructions on setup, workflow, methods, etc.


## User Feedback

You all users of japonicus should create issues about your japonicus runs.
If some strat seems to be viable, send feedback so users can have a better point of entry for their own runs.<br>
Should be like `Supertrend strat: very good, tried to broaden parameter ranges, etc`.


## Future

Genetic Algorithms are a good way to fetch a good set of settings to run a strategy
on gekko. But the real gamechanger is the strategy itself. The ideal evolution method
would be a Genetic Programming that modifies strategy logic. This somewhat
corresponds to `--skeleton` mode of japonicus, which lets the GA select indicators on a base strategy.


# Changelog

```
Changelogs 
v0.56 (under construction)

- japonicus settings for strategies can be stored at strategy_parameters folder as .toml files
- automated refactor on entire codebase
- wiki is online, check it for instructions.

v0.54

- Variation of Backtest result interpretation. check Settings.py -> genconf.interpreteBacktestProfit
- Focus on selecting best individues. Periodic evaluation on more candidates. Bugfixes on that department. 
- Result interface actually readable.
- Log better structured, with the summary at the top.
- Small clarifications on code.

v0.53

- Major aesthetics rework on code itself; now we can even have collaborators.
- Pretty run logs @ logs folder;
- Interchangeable backtest result interpretation (promoterz.evaluation.gekko:25)
- gekko API is now organized - backtest & dadataset functions separated.
- Genetic Algorithm settings controllable via command line. Check --help.
- Web interface more stable

v0.51
- Started tracking updates on changelog;

```
