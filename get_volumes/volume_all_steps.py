#!/usr/bin/env python3

from matplotlib import pyplot as pl

from ast import literal_eval
from scipy import stats

import pandas as pd
import numpy as np
import os

from functions import *

path = 'volume_all_steps'
systemfilename = 'system.txt'
inputfilename = 'steps.in'
sigma = 2

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

batch_errs = []
for i in volcut:
    r = autocorrelation(i)
    k = np.argmax(np.array(r) <= 0)

    err = batch_means(i, k)
    batch_errs.append(err)

stdev = list(map(np.std, volcut))
volmeans = list(map(np.mean, volcut))

df = pd.DataFrame(np.stack((holdtemps, volmeans)).T, columns=['temp', 'vol'])
df.to_csv('volume_all_steps_dfvol.txt' , index=False)
print(df)
print(df['vol']**(1/3))

fit = stats.linregress(df['temp'], df['vol'])
m, b, r = fit[:3]

tempfit = np.linspace(min(holdtemps), max(holdtemps))
volfit = tempfit*m+b

fig, ax = pl.subplots()

ax.plot(time, vol, marker='.', linestyle='none')

ax.set_xlabel('Time [ps]')
ax.set_ylabel(r'Volume $[A^{3}]$')
ax.grid()

fig.tight_layout()
fig.savefig('volume_all_steps')

fig, ax = pl.subplots()

ax.errorbar(holdtemps, volmeans, batch_errs, marker='.', linestyle='--', label='SEM')
ax.errorbar(holdtemps, volmeans, stdev, marker='.', linestyle='--', label='STDEV')
ax.plot(tempfit, volfit, label='Linear fit (r='+str(r)+')')

ax.set_xlabel('Temperature [K]')
ax.set_ylabel(r'Mean Step Volume within '+str(sigma)+ '$\sigma$ $[A^{3}]$')
ax.legend()
ax.grid()

fig.tight_layout()
fig.savefig('volume_all_steps_means')

pl.show()
