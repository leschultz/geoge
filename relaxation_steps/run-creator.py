#!/usr/bin/env python3
from ast import literal_eval

import numpy as np
import sys
import os

from functions import *

runs = int(sys.argv[1])  # The number of runs to generate
template = sys.argv[2]  # Template file path
elements = sys.argv[3]  # Elements
fraction = sys.argv[4]  # Fraction of second element
potential = sys.argv[5]  # The potential used
potential_type = sys.argv[6]  # The type of potential
side = sys.argv[7]  # The length of the cubic simulation box
unit_cell_type = sys.argv[8]  # fcc, hcp, or bcc
lattice_param = sys.argv[9]  # The lattice paramter
timestep = sys.argv[10]  # The timestep
dump_rate = sys.argv[11]  # The rate to dump data
ensemble = sys.argv[12]  # The ensemble for the holds
vols = sys.argv[13]  # The volume for nvt holds (write None for npt)
holds = sys.argv[14:]  # temperature and holds as tuples

# Open and read template
template = open(template)
template_contents = template.read()
template.close()

# Format the holds
holds = list(map(literal_eval, holds))

# Format the volumes
try:
    vols = literal_eval(vols)

except Exception:
    pass

runs = np.arange(runs)
runs = ['run_'+str(i) for i in runs]

for run in runs:
    contents = run_creator(
                           template_contents,
                           elements,
                           fraction,
                           potential,
                           potential_type,
                           side,
                           unit_cell_type,
                           lattice_param,
                           timestep,
                           dump_rate,
                           ensemble,
                           vols,
                           holds,
                           )

    # Write the input file
    path = os.path.join(run, 'steps.in')

    if not os.path.exists(run):
        os.makedirs(run)

    file_out = open(path, 'w')
    file_out.write(contents)
    file_out.close()
