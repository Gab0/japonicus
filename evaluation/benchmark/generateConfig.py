#!/bin/python
import pytoml

NBP = 30
PRANGE = [-1.28, 1.28]

NBP = 25
PRANGE = [-65536, 65536]

NBP = 10
PRANGE = [-500, 500]

NBP = 20
PRANGE = [-5.12, 5.12]

#NBP = 10
#PRANGE = [-600, 600]

#NBP = 2
#PRANGE = [-2.048, 2.048]

PARAMETERS = {}
for P in range(NBP):
    PNAME = 'P%i' % P
    PARAMETERS.update({PNAME: PRANGE})

TOMLTEXT = pytoml.dumps(PARAMETERS)
open('config.toml', 'w').write(TOMLTEXT)
