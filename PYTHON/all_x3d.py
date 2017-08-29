import glob
import os, h5py
import numpy as np
import sys, argparse
from threed import ThreeD
from scripts import biggest
from scripts import deepest
from scripts import highest
from scripts import widest
from scripts import sides

def start(_argv):

    args = parseArgv(_argv)
    # expand all system paths
    homepath = lambda pathy: os.path.expanduser(pathy)
    realpath = lambda pathy: os.path.realpath(homepath(pathy))
    sharepath = lambda share,pathy: os.path.join(share, homepath(pathy))

    RUNS = args['runs']
    TRIAL = args['trial']
    TOP_TYPE = args['deep']
    N_TOP_IDS = args['number'] + 1
    WWW = realpath(args['www'])
    IMGS = realpath(args['img'])
    IMAGE = realpath(args['raw'])
    ROOTOUT = realpath(args['out'])
    STLFOLDER = sharepath(ROOTOUT, 'stl')
    X3DFOLDER = sharepath(ROOTOUT, 'x3d')

    # Calculate raw image and id mesh scales
    V_SCALE = np.float64([args['Vratio'], 1])
    I_SCALE = 2**np.float64(args['Iratio'].split(':'))
    R_SCALE = 2**np.float64(args['Rratio'].split(':'))
    # Store the 3 element scales as strings
    i_scale = ( V_SCALE * I_SCALE )[[(0,1,1)]]
    r_scale = ( V_SCALE * R_SCALE )[[(0,1,1)]]
    # Get keywords for making website
    www_keys = {
        'www': WWW,
        'i_scale': ' '.join(i_scale.astype(str)),
        'r_scale': ' '.join(r_scale.astype(str)),
    }
    print www_keys
    #
    # IF A LIST OF IDS IS PASSED
    #
    if args['list'] != '':
        # If list is range, actualize it
        if '-' in args['list']:
            LIST = [int(v) for v in args['list'].split('-')]
            LIST = range(*LIST)
        else:
            LIST = [int(v) for v in args['list'].split(':')]

        # Find all IDs to make for this trial
        trial_ids = np.linspace(0, len(LIST), RUNS + 1)
        start, stop = np.uint32(trial_ids[TRIAL:][:2])
        # Narrow the list by the chosen ids
        LIST = LIST[start:stop]
        msg = "from {} to {}".format(LIST[0], LIST[-1])
        print(msg)

        # Load ids and make x3d files
        if os.path.exists(IMAGE):
            with h5py.File(IMAGE, 'r') as df:
                full_shape = df[df.keys()[0]].shape

        # Load stl (and cached x3d) to make x3dom html
        ThreeD.create_website(STLFOLDER, X3DFOLDER, LIST, *full_shape, **www_keys)
        # Link full image stack and create cube sides
        sides(X3DFOLDER, IMAGE, IMGS)

        return

    # Count the biggest and the deepest ids 
    BIG_IDS, BIG_COUNTS = biggest('', sharepath(ROOTOUT, 'spread_count.txt'), 1)
    if TOP_TYPE == 0:
        TOP_IDS = BIG_IDS
    elif TOP_TYPE == 1:
        TOP_IDS = deepest('', sharepath(ROOTOUT, 'deep_count.txt'), 1)[0]
    elif TOP_TYPE == 2:
        TOP_IDS = highest('', sharepath(ROOTOUT, 'high_count.txt'), 1)[0]
    elif TOP_TYPE == 3:
        TOP_IDS = widest('', sharepath(ROOTOUT, 'wide_count.txt'), 1)[0]
    # Get the id numbers to use to generate meshes
    top_ids = TOP_IDS[-N_TOP_IDS:-1]

    # Load ids and make x3d files
    if os.path.exists(IMAGE):
        with h5py.File(IMAGE, 'r') as df:
            full_shape = df[df.keys()[0]].shape

    # Load stl (and cached x3d) to make x3dom html
    ThreeD.create_website(STLFOLDER, X3DFOLDER, top_ids, *full_shape, **www_keys)
    # Link full image stack and create cube sides
    sides(X3DFOLDER, IMAGE, IMGS)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'out': 'output web directory (default .)',
        'raw': 'input raw h5 volume (default raw.h5)',
        'img': 'input raw img folder (default imgs)',
        'd': 'rank top ids by depth (default 0)',
        'w': 'folder containing js/css (default www)',
        'n': 'make meshes for the top n ids (default 1)',
        'l': 'make meshes for : separated list of ids',
        'V': 'Original voxel physical z size over xy size  (default 10.0)',
        'R': 'Number of downsamplings in z:xy of raw img data (default 0:3)',
        'I': 'Number of downsamplings in z:xy of ID mesh data (default 0:3)',
        'runs': 'The number of runs for all the ids (1)',
        'trial': 'The trial number for this run (0)',
        'help': 'Make an hdf5 file into html meshes!'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('raw', default='raw.h5', help=help['raw'])
    parser.add_argument('img', default='imgs', help=help['img'])
    parser.add_argument('out', default='.', nargs='?', help=help['out'])
    parser.add_argument('-n','--number', type=int, default=1, help=help['n'])
    parser.add_argument('-l','--list', default='', help=help['l'])    
    parser.add_argument('-t','--trial', type=int, default=0, help=help['trial'])
    parser.add_argument('--runs', '-r', default=1, type=int, help=help['runs'])
    parser.add_argument('-d','--deep',type=int, default=0, help=help['d'])
    parser.add_argument('-w','--www', default='www', help=help['w'])
    parser.add_argument('-V','--Vratio', default=10.0, type=float, help=help['V'])
    parser.add_argument('-R','--Rratio', default='0:3', help=help['R'])
    parser.add_argument('-I','--Iratio', default='0:3', help=help['I'])

    # attain all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

