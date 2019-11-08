### What is japonicus and what it does
This is an implementation of genetic algorithm & bayesian evolution to develop strategies for digital coin trading bot <a href="https://github.com/askmike/gekko">Gekko</a>.

So you make a good strat, or get one from the internetz. Make sure its good, because this is not about miracles.

If you get good profit on strat standard settings or some random settings you made up, japonicus can find some setting set that improves the strategy, on some specific market/currency or overall.

Discord Group: `https://discord.gg/kYKHXnV`

## Instructions
Japonicus works on `python>=3.6`!
Check wiki for instructions on setup, workflow, methods, etc.

## Disclaimer

No matter how many years your training candles span or how convoluted or simple is your strategy,
your strategies/parameters that were profitable on backtest runs probably won't translate well to live trading.<br>
Altough japonicus is a fairly competent GA and will find a capable set of parameters in a few epoches,
we're yet to discover why the live trading runs seem an environment completely unrelated to backtest env, where
strategies/parameters that seemed good offline turn into live daily losses or below market gains.

You can send me a few coins to help me develop some ideas for binance trading bots,
as this kind of research involves a steady negative profit so I cannot sustain it indefinitely...
If something starts working I will share here or in our discord group. Those are my binance wallets:

```
LTC	LVhThMzJMC6aKBcA1KX4q3yk2ryBjfPGfH
ETH	0xceaa9bb655ed80ba36b55532fdd6e11e6e5b681b
```

## User Feedback

You all users of japonicus should report notable runs under an issue.
If some strat seems to be viable, send feedback so users can have a better point of entry for their own runs.<br>

## Future

Genetic Algorithms are a good way to fetch a good set of settings to run a strategy on gekko. <br>
But the real gamechanger is the strategy itself.<br>
The ideal evolution method would be a Genetic Programming that modifies strategy logic. <br>
This somewhat corresponds to `--skeleton` mode of japonicus, which lets the GA select indicators on a base strategy.


# Changelog

The changelog is important for the user as following modifications can cause bugs on related areas. Please report 'em ;)

```
v0.92
- Moving all gekko related functions to evaluation.gekko module. The purpose is making japonicus a general purpose
GA framework.


v0.91

- the evolution candle date ranges are now defined by given area in the map, instead of attached at each locale.


v0.90 

- web interface reworked - now it is the recommended method to run the ga's.
- locale creation/destruction chances updated.
- bayesian evolution method deprecated.

v0.80 

- supports gekko v0.6.X (only).
- Dockerfile and docker-compose methods revisited.
- automatic filter for multiple remote gekko urls (urls defined inside settings/global)
- live trading bot watcher at `jlivetrader.py`. For binance only, undocumented and experimental.


v0.70 

- log folder restructured
- configStrategies.py DEPRECATED; use only TOML parameters at the folder strategy_parameters.
    check TOML special syntax for parameter ranges at the wiki
- GA benchmark mode added
- Settings.py refactor
- Roundtrip exposure time filter


v0.58

- runs in Windows (not confirmed)
- Settings parameters can be passed on command line (check the --help)
- Multiple evolution datasets can be passed. `@Settings.py:dataset ->
  dataset_source is the first, add dataset_source1; dataset_source2 and so forth
for multiple datasets.`
- filter individues for minimum trade count (default: enabled@16 trades)
- backtest scores (profit and sharpe) to individue final score method is now a sum, not multiplication

v0.56 

- japonicus settings for strategies can be stored at strategy_parameters folder as .toml files
- automated refactor on entire codebase
- wiki is online, check it for instructions.
- various bugfixes
- log & results improvements
- daterange for locales now on locale logs (.csv)
- statistics methods remade.

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
