#!/bin/python
import pytoml

NBP = 30
PRANGE = [-1.28, 1.28]

PARAMETERS = {}
for P in range(NBP):
    PNAME = 'P%i' % P
    PARAMETERS.update({PNAME: PRANGE})

TOMLTEXT = pytoml.dumps(PARAMETERS)
open('config.toml', 'w').write(TOMLTEXT)
