#!/usr/bin/env python3

from matplotlib import pyplot as pl
from os.path import join
from scipy import stats

import pandas as pd
import numpy as np

import sys
import os

dataname = 'ico_fraction_vs_temperature.txt'

datapath = sys.argv[1]  # The path containing ICO fractions for all runs
exportpath = sys.argv[2]  # The path to export analysis for mean

count = 0
for path, subdirs, files in os.walk(datapath):

    if dataname not in files:
        continue

    run = path.strip(datapath)

    if count == 0:
        df = pd.read_csv(join(path, dataname))
        cols = list(df.columns)
        col = cols[-1]+'_'
        cols[-1] = col+str(count)
        df.columns = cols

    else:
        df[col+str(count)] = pd.read_csv(
                                         join(path, dataname)
                                         )['fracs']

    count += 1

means = []
stds = []
sems = []
counts = []

count = 0
data = df.values.T
for i in data:

    if count > 1:
        mean = np.mean(data[1:count+1], axis=0)
        std = np.std(data[1:count+1], axis=0)
        sem = stats.sem(data[1:count+1], ddof=1, axis=0)

        means.append(mean)
        stds.append(std)
        sems.append(sem)
        counts.append(count)

    count += 1

fig, ax = pl.subplots()

for mean, std, sem, count in zip(means, stds, sems, counts):

    ax.errorbar(
                df['temp'],
                mean,
                std,
                marker='.', 
                ecolor='r',
                linestyle='none',
                label='std'
                )

    ax.errorbar(
                df['temp'],
                mean,
                sem,
                marker='.',
                ecolor='y',
                linestyle='none',
                label='sem'
                )

ax.set_xlabel('Temperature [K]')
ax.set_ylabel('Mean ICO Fractions [-]')

ax.legend()
ax.grid()

pl.show()
