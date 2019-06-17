#!/usr/bin/env python3

from matplotlib import pyplot as pl
from os.path import join

import pandas as pd

import sys
import os

dataname = 'ico_fraction_vs_temperature.txt'

datapath = sys.argv[1]  # The path containing ICO fractions for all runs
exportpath = sys.argv[2]  # The path to export analysis for mean

df = []
for path, subdirs, files in os.walk(datapath):

    if dataname not in files:
        continue

    run = path.strip(datapath)

    df.append(pd.read_csv(join(path, dataname)))

df = pd.concat(df)
groups = df.groupby('temp')

mean = groups.mean().add_suffix('_mean').reset_index()
std = groups.std().add_suffix('_std').reset_index()
sem = groups.sem().add_suffix('_sem').reset_index()
count = groups.count().add_suffix('_count').reset_index()

dfmean = mean.merge(std)
dfmean = dfmean.merge(sem)
dfmean = dfmean.merge(count)

export = join(exportpath, 'ico')
if not os.path.exists(export):
    os.makedirs(export)

dfmean.to_csv(
              join(export, 'mean_ico_vs_temperature.txt'),
              index=False
              )

fig, ax = pl.subplots()

ax.errorbar(
            dfmean['temp'],
            dfmean['fracs_mean'],
            dfmean['fracs_std'],
            marker='.',
            linestyle='none',
            ecolor='r',
            label='std'
            )

ax.errorbar(
            dfmean['temp'],
            dfmean['fracs_mean'],
            dfmean['fracs_sem'],
            marker='.', 
            linestyle='none', 
            ecolor='y', 
            label='sem'
            )

ax.set_xlabel('Temperature [K]')
ax.set_ylabel('Mean ICO Fractions')

ax.legend()
ax.grid()

fig.tight_layout()
fig.savefig(join(export, 'mean_ico_vs_temperature'))
