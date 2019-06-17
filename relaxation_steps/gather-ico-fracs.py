#!/usr/bin/env python3

from PyQt5 import QtGui  # Added to be able to import ovito

from ovito.modifiers import VoronoiAnalysisModifier
from ovito.io import import_file

from os.path import join

import pandas as pd

import sys
import os

from functions import *

runpath = sys.argv[1]  # The top directory of runs
infilename = sys.argv[2]  # The name for the LAMMPS input file
trajfilename = sys.argv[3]  # The name for the trajectory file
sysfilename = sys.argv[4]  # The name for the thermodynamic data file
threshold = float(sys.argv[5])  # The edge threshold for VP analysis
sigma = int(sys.argv[6])  # The cutoff for population filtering

# Modifier for VP analysis on Ovito
voro = VoronoiAnalysisModifier(
                               compute_indices=True,
                               use_radii=False,
                               edge_threshold=threshold
                               )


# Count the number of runs for progress status
paths = []

runs = -1
for path, subdirs, files in os.walk(runpath):

    # Only paths containing files needed
    condition = (infilename in files) 
    condition = condition and (trajfilename in files)
    condition = condition and (sysfilename in files)
    
    if not condition:
        continue

    paths.append(path)  # The path for viable job
    runs += 1

runs = str(runs)  # Only convert to string once

# Loop through runs and gather ICO fractions
count = 0
for path in paths:

    # Status update
    print('Analyzing ('+str(count)+'/'+runs+ '): '+path)

    # Relevant files
    infile = join(path, infilename)
    trajffile = join(path, trajfilename)
    sysfile = join(path, sysfilename)

    # Parse input file for parameters
    inputparameters = input_parse(infile)

    # Assign parameters to shorter variables
    holdsteps = inputparameters['holdsteps']
    dumprate = inputparameters['dumprate']
    elements = inputparameters['elements']
    fraction =  inputparameters['fraction']
    temperatures = inputparameters['temperatures']

    # Gather the thermodynamic data
    cols, data = system_parse(sysfile)

    df = pd.DataFrame(data, columns=cols)

    df['frames'] = df['TimeStep']//dumprate

    # Load input data and create an ObjectNode with a data pipeline.
    node = import_file(trajffile, multiple_frames=True)
    node.modifiers.append(voro)

    fractions = []  # The ICO fraction for each step

    i = 0
    for step, temp in zip(holdsteps, temperatures):
        cut1 = sum(holdsteps[:i])
        cut2 = sum(holdsteps[:i+1])

        d = df[(df['TimeStep'] >= cut1) & (df['TimeStep'] <= cut2)]

        # Remove data outside of x*sigma of temperature
        t = d['c_mytemp']
        d = d[abs(t-np.mean(t)) < sigma*np.std(t)]

        all_indexes = []
        for frame in d['frames']:
            out = node.compute(frame)
            indexes = out.particle_properties['Voronoi Index'].array
            all_indexes.append(indexes)

        # Combine all the frames
        all_indexes = [pd.DataFrame(i) for i in all_indexes]
        dfvp = pd.concat(all_indexes)
        dfvp = dfvp.fillna(0)  # Make cure indexes are zero if not included
        dfvp = dfvp.astype(int)  # Make sure all counts are integers

        # Count the number of unique VP
        coords, counts = np.unique(dfvp.values, axis=0, return_counts=True)

        dfvp = pd.DataFrame(coords)
        dfvp['counts'] = counts
        dfvp['fractions'] = dfvp['counts']/sum(dfvp['counts'])
        dfvp = dfvp.sort_values(by=['counts'], ascending=False)

        # Count ICO fractions
        dfico = dfvp[dfvp[4] >= 10]
        fraction = sum(dfico['fractions'])

        fractions.append(fraction)

        i += 1

    fracs = np.stack((temperatures, fractions)).T
    dffracs = pd.DataFrame(fracs, columns=['temp', 'fracs'])
    
    print(dffracs)

    count += 1
