import os
import sys
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
    MAX_ID = 7179095
    N_BLOCKS = 8

    TARGET="/n/coxfs01/thejohnhoffer/R0/ids-2017-05-11_ids-0z-3xy_mesh-8xyz/meshes/stl/" 

    # Get grid of all smaller stl files
    blocksize = (N_BLOCKS, N_BLOCKS, N_BLOCKS)
    blocklist = range(np.prod(blocksize))
    all_blocks =  zip(*np.unravel_index(blocklist, blocksize))

    # Find all IDs to make for this trial
    step_ids = np.linspace(0, MAX_ID+1, RUNS + 1, dtype=np.uint64)
    start, stop = np.uint64(step_ids[STEP:][:2])
    msg = """
    Moving all stl files for ids from {} to {}
    """.format(start, stop)
    print(msg)

    # Move each id
    for i in range(start,stop):
        # Make the new folder if doesn't exist
        new_folder = os.path.join(TARGET, str(i))
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
        # For all the blocks
        for bz,by,bx in all_blocks:
            # Move to a new folder
            old_name = '{}_{}_{}_{}.stl'.format(i,bz,by,bx)
            old_path = os.path.join(SOURCE, old_name)
            # If the old path exists
            if os.path.exists(old_path):
                # Rename the old file with the new name
                new_name = '{}_{}_{}.stl'.format(bz,by,bx)
                new_path = os.path.join(new_folder, new_name)
                # Declare the renaming of this file
                msg = "Moving {} to {}".format(old_path, new_path)
                print(msg)
                # Actually move the files
                #os.rename(old_path, new_path)
