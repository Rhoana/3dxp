import glob
import os, h5py
import numpy as np
import sys, argparse
from threed import ThreeD
from scripts import biggest
from scripts import deepest
from scripts import highest
from scripts import widest


def start(_argv):

    args = parseArgv(_argv)
    # expand all system paths
    homepath = lambda pathy: os.path.expanduser(pathy)
    realpath = lambda pathy: os.path.realpath(homepath(pathy))
    sharepath = lambda share,pathy: os.path.join(share, homepath(pathy))

    BLOCK = args['block']
    TRIAL = args['trial']
    TOP_TYPE = args['deep']
    N_TOP_IDS = args['number'] + 1
    DATA = realpath(args['ids'])
    ROOTOUT = realpath(args['out'])
    STLFOLDER = sharepath(ROOTOUT, 'stl')
    ORDER = ['zyx', 'xyz'][args['xyz']]

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

        print args['list']

        # Load ids and make stl files
        if not os.path.exists(DATA):
            print 'Empty: {}'.format(DATA)
            return

        with h5py.File(DATA, 'r') as df:
            vol = df[df.keys()[0]]
            full_shape = np.array(vol.shape)
            # Get number of blocks and block size
            block_size = np.uint32(np.ceil(full_shape/BLOCK))
            ntiles = np.uint32([BLOCK]*3)


        # Get all possible tile offsets
        subvols = zip(*np.where(np.ones(ntiles)))

        z,y,x = subvols[TRIAL]

        ThreeD.run(DATA, z, y, x, STLFOLDER, block_size, LIST, ORDER)

        print('All done with stl block {},{},{}'.format(z,y,x))

        return

    # Count the biggest and the deepest ids 
    BIG_IDS, BIG_COUNTS = biggest(DATA, sharepath(ROOTOUT, 'spread_count.txt'), BLOCK)
    if TOP_TYPE == 0:
        TOP_IDS = BIG_IDS
    elif TOP_TYPE == 1:
        TOP_IDS = deepest(DATA, sharepath(ROOTOUT, 'deep_count.txt'), BLOCK)[0]
    elif TOP_TYPE == 2:
        TOP_IDS = highest(DATA, sharepath(ROOTOUT, 'high_count.txt'), BLOCK)[0]
    elif TOP_TYPE == 3:
        TOP_IDS = widest(DATA, sharepath(ROOTOUT, 'wide_count.txt'), BLOCK)[0]
    # Get the id numbers to use to generate meshes
    top_ids = TOP_IDS[-N_TOP_IDS:-1]
    # No matter what, get the total block counts for each ID
    big_ids = [np.where(BIG_IDS == tid)[0][0] for tid in top_ids]
    top_counts = BIG_COUNTS[big_ids]

    # Load ids and make stl files
    if os.path.exists(DATA):

        with h5py.File(DATA, 'r') as df:
            vol = df[df.keys()[0]]
            full_shape = np.array(vol.shape)
            # Get number of blocks and block size
            block_size = np.uint32(np.ceil(full_shape/BLOCK))
            ntiles = np.uint32([BLOCK]*3)

        # Get all possible tile offsets
        subvols = zip(*np.where(np.ones(ntiles)))

        # Only search volume for ids that need more stl files
        re_path = [os.path.join(STLFOLDER,str(intid),'*') for intid in top_ids]

        z,y,x = subvols[TRIAL]
        # Check for existing stl files
        found_counts = [len(glob.glob(re_file)) for re_file in re_path]
        top_stl_ids = top_ids[top_counts>found_counts]
        if len(top_stl_ids):
            ThreeD.run(DATA, z, y, x, STLFOLDER, block_size, top_stl_ids, [], ORDER)

        print('All done with stl block {},{},{}'.format(z,y,x))

def parseArgv(argv):
    sys.argv = argv

    help = {
        'ids': 'input hd5 id volume (default in.h5)',
        'out': 'output web directory (default .)',
        'd': 'rank top ids by depth (default 0)',
        'b': 'Number of blocks in each dimension (default 10)',
        't': 'Which of the b*b*b tiles to generate (default 0)',
        'n': 'make meshes for the top n ids (default 1)',
        'l': 'make meshes for : separated list of ids',
        'xyz': 'Store meshes with xyz coordinates (default zyx)!',
        'help': 'Make an hdf5 file into stl meshes!'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('ids', help=help['ids'])
    parser.add_argument('out', help=help['out'])
    parser.add_argument('--xyz', action='store_true', help=help['xyz'])
    parser.add_argument('-d','--deep',type=int, default=0, help=help['d'])
    parser.add_argument('-t','--trial', type=int, default=0, help=help['t'])
    parser.add_argument('-b','--block', type=int, default=1, help=help['b'])
    parser.add_argument('-n','--number', type=int, default=1, help=help['n'])
    parser.add_argument('-l','--list', default='', help=help['l'])

    # Handle unknown arguments (for compatibility)
    return vars(parser.parse_known_args()[0])

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

