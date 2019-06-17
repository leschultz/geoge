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
            l = str(vol**(1/3))

            steps += 'change_box all'
            steps += ' x final 0.0 '+l
            steps += ' y final 0.0 '+l
            steps += ' z final 0.0 '+l
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
