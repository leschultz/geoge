#!/usr/bin/env python3

from matplotlib import pyplot as pl
from os.path import join
from scipy import stats

import pandas as pd
import numpy as np

import copy
import sys
import os

dataname = 'ico_fraction_vs_temperature.txt'

datapath = sys.argv[1]  # The path containing ICO fractions for all runs
exportpath = sys.argv[2]  # The path to export analysis for mean

fig, ax = pl.subplots()

i = 1
for path, subdirs, files in os.walk(datapath):

    if dataname not in files:
        continue

    run = path.strip(datapath)

    if i == 1:
        df = pd.read_csv(join(path, dataname))

    else:
        df = df.merge(
                      pd.read_csv(join(path, dataname)),
                      on=['temp'],
                      suffixes=(i-1, i)
                      )

        fracs = df.loc[:, df.columns != 'temp']

        temps = df['temp']
        mean = fracs.mean(axis=1)
        std = fracs.std(axis=1)
        sem = fracs.sem(axis=1)
        count = fracs.count(axis=1)

        ax.errorbar(
                    count,
                    mean,
                    std,
                    marker='.', 
                    ecolor='r',
                    linestyle='none',
                    )

        ax.errorbar(
                    count,
                    mean,
                    sem,
                    marker='.',
                    ecolor='y',
                    linestyle='none',
                    )

    i += 1

ax.set_xlabel('Count of Runs [-]')
ax.set_ylabel('Mean ICO Fractions [-]')
ax.grid()

fig.tight_layout()

export = join(exportpath, 'ico')
if not os.path.exists(export):
    os.makedirs(export)

fig.savefig(join(export, 'mean_ico_vs_population'))
