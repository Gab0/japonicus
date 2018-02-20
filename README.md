This is an implementation of genetic algorithm evolution to develop strategies for digital coin trading bot <a href="https://github.com/askmike/gekko">Gekko</a>. 

It generates random configs & evolve them by backtesting on a Gekko session via the REST API of gekko's user interface. <br>
Genetic algorithm and quick bayesian optimization are evolution choices.

### What is japonicus and what it does
A genetic algorithm & bayesian evolution tool designed to evolve the parameters of strategies to be used on gekko trading bot.
So you make a good strat, or get one from the internetz. Make sure its good, because this is not about miracles.
If you get good profit on strat standard settings or some random settings you made up, japonicus can find some setting set that
improves the strategy, on some specific market/currency or overall.

## Setup
Japonicus works on `python>=3.6`!

#### General
```
> Install gekko, then clone this repo and install dependencies:

$ git clone https://git.com/Gab0/japonicus.git
$ cd japonicus
$ sudo pip install -r requirements.txt
   > make sure pip session runs for python3.6 --> $sudo pip3 install -r requirements.txt
```

#### Full stack on Linux Mint 18.3 (propably same on Ubuntu 16.04)
```
$ sudo add-apt-repository ppa:jonathonf/python-3.6
$ sudo apt update
$ sudo apt install python3.6
$ sudo apt install python3.6-dev
$ sudo apt install python3.6-tk
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python3.6 get-pip.py
$ cd /usr/lib/python3/dist-packages 
$ sudo cp apt_pkg.cpython-35m-x86_64-linux-gnu.so apt_pkg.so (where 35m-x86_64 put your version)
$ cd /home/f/gekko/
$ git clone https://github.com/Gab0/japonicus.git
$ cd japonicus
$ sudo pip3.6 install -r requirements.txt
```

## Usage

```
Open two terminals;

T.1 -> run Gekko on ui mode, or just its webserver:
$node gekko.js --ui
        or
$node web/server.js

T.2 -> $cd [japonicus dir]
       $python japonicus.py [-g|-b] [-c] [-k] [--repeat <X>] [ [-i|-r|--strat <Strategy>] [-w]

    [main optimization options]
    -g for genetic algorithm;
    -b for bayesian optimization;
    
    [optional GA methods]
    -c to use an alternative ~experimental genetic algorithm;

    [strategy selector] 
    -r run with random strategy
    --strat choose one strat to run;
    -i Genetic algorithm create strategies w/ combined indicators on the fly and run 'em.
    
    [repeat runs]    
    --repeat to run genetic algorithm X times; then just check evolution.log;

    [evolution visualization options]
    -w launches a neat dash/flask web server @ your local machine, which can be accessed via  webbrowser.
           Address is shown on the first line of console output. (likely http://localhost:5000)

    -k launches a child gekko instance, so no need for the first terminal;
```

This is written on python because of the nice DEAP module for genetic algorithm, and was worth it. DEAP is required, available on PIP.

All settings are set at Settings.py;

If your Gekko UI http port is not :3000, adjust it;

Backtesting is parallel, running a pool of five workers, adjustable.

Bayesian optimization is a quick method to get and idea of some strat settings, while Genetic Algorithm is a rather detailed parallel GA method that takes a long run time, on standard settings, to try to get a very good setting set on chosen strat.

Remember to review/set parameter ranges for chosen strategy name on `configStrategies.py`.

## Results

For genetic algorithm `-g`, results are visible at the end of last epoch, as dict and Gekko UI-friendly format (TOML).
Results can also be visible in middle epoches.. check `generations.evaluateSettingsPeriodically` @ `Settings.py` to set that interval.

On bayesian method `-b`, current best setings are visible at every step, ending on the same info as `-g`.

### Gekko Strategies

To run japonicus you must select a strat via `--strat <strategy>`, where `<strategy>` corresponds to any working strategy present on gekko `strategies` folder.
The settings ranges for given strategy must be present as a key on `configStrategies.py`. A random strategy may be also selected with `-r` arg.

Those strategies present in a fresh clone of gekko are no good, ditch them. 
With genetic algorithm optimization, those strats can get to a level of profit that is above the market base price change 
for given period. Even then, that power will be only shown at the dataset it was optimized for, so the settings
will fail on different candlesticks which include real time trading.

A good thing to do is to create a strategy that combines two indicators, IE you buy when both results are above buying thresolds,
you sell when both are below selling thresholds. So dual or even triple indicator strategies are a good path to go.
Strategy must go beyond simple logic of indicator results on thresholds to have
meaningfun results.

Custom strategies should be added to configStrat.py, by strategy name.


#### Notable Strategies

Some custom strategies for which japonicus got settings covered:

https://github.com/Gab0/gekko-supertrend-strategy/ by dodo33. Original strat uses TA-Lib ATR indicator.
Modified on this fork for usability with GA. Remember to put the native indicator `ATR.js`on correspondent folder. 
That strategy does not get very good results.

https://github.com/tommiehansen/gekko_tools by tommiehansen. A couple of multiple indicator strategies, they use
tulind so backtests can take awhile, but HEY thats some good strats of high trading rate and high profit.

#### User Feedback

You all users of japonicus should create issues about your japonicus runs.
If some strat seems to be viable, send feedback so users can have a better point of entry for their own runs.<br>
Should be like `Supertrend strat: very good, tried to broaden parameter ranges, etc`.

### Special usage methods

#### Remote Amazon EC2 Cluster

Japonicus can send backtest requests across the internet to several machines running Gekko.
This method can greatly cut EPOCH times.
Intended to use with Ansible-playbook + Amazon EC2 AWS machines. <br>
At japonicus side, you should provide Ansible's `hosts` inventory file path (on settings.generations), containing
the IPs of running machines (a simple list). <br>
Those machines should be already fully configured, running Gekko, and loaded with the same candlestick history data
files you have on local Gekko;<br>
YML playbook file to get gekko running on Amazon AMI Linux is at root folder (set the path to your local gekko history @ line 57);

```
steps to put your GA online on clusters;

1- Create how many EC2 instances you want - spot requests are cheaper;

2- Make sure port 3000 TCP is open on them. This is configurable on security groups.
    Theres a nice tutorial at https://www.google.com/search?q=amazon+aws+security+groups XD
    
3- Find a way to install node and gekko on them. Copy your local gekko/history folder to them;
(there is a ansible playbook on the repo that can help you cover this steps)

4- Make a list of your remote machine addrs and inform the path to it at Settings.py->Global.GekkoURLs. A hosts file used by ansible can be used as it is.

5- Run japonicus.py in any GA mode;

```

#### Docker Compose

You can include japonicus to gekko image by adding the following snippet to gekkos docker-compose file

```yml
  japonicus:
    build: relative-path-from-gekko-to-the-japonicus-repo/
    volumes:
      - ./volumes/gekko-japonicus:/usr/src/app/output
    links:
      - gekko
    ports:
      - 5000:5000
```

and by setting the `GekkoURLs` config to the container gekko name
```python
# Settings.py
'GekkoURLs': ['http://gekko:3000']
```

japonicus will choose a random item of the list to fetch candles and scansets.

# Future

Genetic Algorithms are a good way to fetch a good set of settings to run a strategy
on gekko. But the real gamechanger is the strategy itself. The ideal evolution method
would be a Genetic Programming that modifies strategy logic. This somewhat
corresponds to `-i` option of japonicus, still barebones yet - only 'sums' indicators.

I'm doing an effort to port the most usable indicator from TA-Lib to native gekko, for faster computing and better usability on genetic algorithms.
Anyone interested on this work or that would like to suggest an important indicator should message me or send pull requests etc. Those are important for `-i` method improvement.

<br>

Indicators roadmap: <br>
~~- Bollinger Bands~~<br>
~~- Average True Range~~<br>
- Parabolic Stop and Reverse<br>
- Directional Movement Concept <br>
- ADX <br>
- Ichimoku clouds
