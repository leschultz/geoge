#!/usr/bin/env python3

from matplotlib import pyplot as pl

from ast import literal_eval
from scipy import stats

import pandas as pd
import numpy as np
import os

from functions import *

systemfilename = 'system.txt'
inputfilename = 'steps.in'
sigma = 2

fig0, ax0 = pl.subplots()
fig1, ax1 = pl.subplots()

for path, subdir, files in os.walk('./'):

    if (systemfilename not in files) and (inputfilename not in files):
        continue

    run = path.split('./')[-1]

    print(path)
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

    holdsteps = []
    holdtemps = []
    with open(inputpath) as f:
        for line in f:
            line = line.strip().split(' ')

            if 'mytimestep' in line:
                timestep = float(line[-1])

            if 'run' == line[0]:
                holdsteps.append(int(line[-1]))

            if 'iso' in line:
                holdtemps.append(float(line[5]))

    data['time'] = data['TimeStep']*timestep

    time = data['time'].values
    vol = data['v_myvol'].values

    volsplit = np.array_split(vol, len(holdsteps))

    # Remove a percent of beginning data
    volcut = [i[abs(i-np.mean(i)) < sigma*np.std(i)] for i in volsplit]
    volmeans = [np.mean(i) for i in volcut]

    stdev = list(map(np.std, volcut))
    volmeans = list(map(np.mean, volcut))

    df = pd.DataFrame(np.stack((holdtemps, volmeans)).T, columns=['temp', 'vol'])
    df['l'] = df['vol']**(1/3)
    df['run'] = run
    df.to_csv('volume_all_steps_dfvol.txt' , index=False)
    print(df)

    fit = stats.linregress(df['temp'], df['vol'])
    m, b, r = fit[:3]

    tempfit = np.linspace(min(holdtemps), max(holdtemps))
    volfit = tempfit*m+b

    ax0.plot(time, vol, marker='.', linestyle='none', label=run)
    ax1.errorbar(holdtemps, volmeans, stdev, marker='.', linestyle='--', label='STDEV '+run)
    ax1.plot(tempfit, volfit, label='Linear fit (r='+str(r)+') '+run)


ax0.set_xlabel('Time [ps]')
ax0.set_ylabel(r'Volume $[A^{3}]$')
ax0.legend()
ax0.grid()

ax1.set_xlabel('Temperature [K]')
ax1.set_ylabel(r'Mean Step Volume within '+str(sigma)+ '$\sigma$ $[A^{3}]$')
ax1.legend()
ax1.grid()

fig0.tight_layout()
fig1.tight_layout()

fig0.savefig('volume_all_steps')
fig1.savefig('volume_all_steps_means')

pl.show()
