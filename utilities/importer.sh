#!/bin/bash

# To run GAs one needs candlestick datasets to backtest.
# Grabbing that data on a VPS can be a pain, so thats an automated tool that grabs some interesting datasets;

GekkoPath="${HOME}/gekko"
japonicusRelativeToGekko="../japonicus"
configs=($(ls|grep ".js"))
echo $configs

for conf in "${configs[@]}"
do
node ${GekkoPath}/gekko.js -i -c ${japonicusRelativeToGekko}/utilities/${conf}
done



