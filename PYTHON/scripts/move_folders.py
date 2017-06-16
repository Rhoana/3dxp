import os
import sys
import time
import argparse
import numpy as np

def parseArgv(argv):
    
    help = {
        'step': 'Current step',
        'runs': 'Total number of steps',
        'help': 'Move stl files to new folder structure',
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('-r', '--runs', type=int, default=100, help=help['runs'])
    parser.add_argument('-s', '--step', type=int, default=0, help=help['step'])

    return vars(parser.parse_args(argv))

if __name__ == '__main__':

    # Get the arguments
    args = parseArgv(sys.argv[1:])
    RUNS = args['runs']
    STEP = args['step']

    SOURCE="/n/coxfs01/thejohnhoffer/R0/ids-2017-05-11_ids-0z-3xy_mesh-6xyz/meshes/stl/"

    TARGET="/n/coxfs01/thejohnhoffer/R0/ids-2017-05-11_ids-0z-3xy_mesh-8xyz/meshes/stl/" 

    # Get all stl files in directory
    old_stl = os.listdir(SOURCE)
    n_stl = len(old_stl)

    # Find all IDs to make for this trial
    step_ids = np.linspace(0, n_stl, RUNS + 1, dtype=np.uint64)
    start, stop = np.uint64(step_ids[STEP:][:2])
    msg = """
    Moving all stl files for all files from {} to {}
    """.format(start, stop)
    print(msg)

    # Allow for all jobs to sync
    time.sleep(120) 

    # Move each id
    for old_name in old_stl[start:stop]:

        # Get the full old file path
        old_path = os.path.join(SOURCE, old_name)
        # Get the neuron from the file name
        old_parts = old_name.split('_')
        neuron = old_parts[0]

        # Make the new folder if doesn't exist
        new_folder = os.path.join(TARGET, neuron)
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)

        # Rename the old file with the new name
        new_name = '_'.join(old_parts[1:])
        new_path = os.path.join(new_folder, new_name)

        # Declare the renaming of this file
        msg = "Moving {} to {}".format(old_path, new_path)
        print(msg)
        # Actually move the files
        os.rename(old_path, new_path)
