from ast import literal_eval
import numpy as np
import random


def run_creator(
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
                holds
                ):
    '''
    Generate a LAMMPS input file
    '''

    # Random number used by LAMMPS
    seed = random.randint(0, 9999999)

    # Replace keywords within a template document
    contents = template_contents
    contents = contents.replace('#replace_elements#', elements)
    contents = contents.replace('#replace_second_element_fraction#', fraction)
    contents = contents.replace('#replace_potential#', potential)
    contents = contents.replace('#replace_potential_type#', potential_type)
    contents = contents.replace('#replace_side#', side)
    contents = contents.replace('#replace_unit_cell_type#', unit_cell_type)
    contents = contents.replace('#replace_lattice_param#', lattice_param)
    contents = contents.replace('#replace_timestep#', timestep)
    contents = contents.replace('#replace_dumprate#', dump_rate)

    # Randomize initial velocites
    steps = (
             'velocity all create ' +
             str(holds[0][0]) +
             ' ${seed} rot yes dist gaussian' +
             2*'\n'
             )

    # Create a step for every temperature and hold defined
    if ensemble == 'npt':
        for temp, step in holds:
            temp = str(temp)
            step = str(step)

            steps += (
                      'fix step all npt temp ' +
                      temp +
                      ' ' +
                      temp +
                      ' '
                      '0.1 ' +
                      'iso 0 0 1\n' +
                      'run ' +
                      step +
                      '\n' +
                      'unfix step\n'
                      )

    if ensemble == 'nvt':
        for hold, vol in zip(holds, vols):
            temp = str(hold[0])
            step = str(hold[1])
            side_l = str(vol**(1/3))

            steps += 'change_box all'
            steps += ' x final 0.0 '+side_l
            steps += ' y final 0.0 '+side_l
            steps += ' z final 0.0 '+side_l
            steps += ' units box'
            steps += '\n'

            steps += (
                      'fix step all nvt temp ' +
                      temp +
                      ' ' +
                      temp +
                      ' '
                      '0.1\n' +
                      'run ' +
                      step +
                      '\n' +
                      'unfix step\n'
                      )

    contents = contents.replace('#replace_holds#', steps)
    contents = contents.replace('#replace_seed#', str(seed))

    return contents


def input_parse(infile):
    '''
    Parse the input file for important parameters

    inputs:
        infile = The name and path of the input file
    outputs:
        param = Dictionary containing run paramters
    '''

    holdsteps = []
    temperatures = []
    with open(infile) as f:
        for line in f:

            line = line.strip().split(' ')

            if 'run' == line[0]:
                holdsteps.append(int(line[-1]))

            if 'mydumprate' in line:
                line = [i for i in line if i != '']
                dumprate = int(line[-1])

            if 'pair_coeff' in line:
                line = [i for i in line if i != '']
                elements = line[4:]

            if 'fraction' in line:
                line = [i for i in line if i != '']
                fraction = float(line[-1])

            if ('temp' in line) and ('fix' in line):
                line = [i for i in line if i != '']
                temperatures.append(float(line[5]))

    param = {
             'holdsteps': holdsteps,
             'dumprate': dumprate,
             'elements': elements,
             'fraction': fraction,
             'temperatures': temperatures,
             }

    return param


def system_parse(sysfile):
    '''
    Parse the thermodynamic data file

    inputs:
        sysfile = The name and path of the thermodynamic data file
    outputs:
        columns = The columns for the data
        data = The data from the file
    '''

    data = []
    with open(sysfile) as f:
        line = next(f)
        for line in f:

            if '#' in line:
                values = line.strip().split(' ')
                columns = values[1:]

            else:
                values = line.strip().split(' ')
                values = list(map(literal_eval, values))
                data.append(values)

    return columns, data
