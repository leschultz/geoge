#!/usr/bin/env python3

import subprocess
import os

runname = 'steps.in'
for path, subdirs, files in os.walk('./'):

    if runname not in files:
        continue

    print(path)
    subprocess.run(['lmp_serial', '-in', runname], cwd=path)
