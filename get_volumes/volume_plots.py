#!/usr/bin/env python3

from matplotlib import pyplot as pl
from ast import literal_eval

import pandas as pd
import os

systemfilename = 'system.txt'
inputfilename = 'steps.in'

fig, ax = pl.subplots()

for path, subdir, files in os.walk('./'):

    if systemfilename not in files:
        continue

    datapath = os.path.join(path, systemfilename)

    data = []
    with open(datapath) as f:
        for line in f:
            line = line.strip().split(' ')

            if line[0] == '#':
                columns = line[1:]

            else:
                line = list(map(literal_eval, line))
                data.append(line)
    
    data = pd.DataFrame(data, columns=columns)

    inputpath = os.path.join(path, inputfilename)

    with open(inputpath) as f:
        for line in f:
            line = line.strip().split(' ')

            if 'mytimestep' in line:
                timestep = float(line[-1])

    data['time'] = data['TimeStep']*timestep

    time = data['time'].values
    vol = data['v_myvol'].values

    ax.plot(time, vol, marker='.', linestyle='none', label=path)

ax.set_xlabel('Time [ps]')
ax.set_ylabel(r'Volume $[A^{3}]$')
ax.legend()
ax.grid()

fig.tight_layout()
fig.savefig('volume_comparisons')
