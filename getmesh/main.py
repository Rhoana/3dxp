import os, h5py
import numpy as np
import sys, argparse
from threed import ThreeD
from scripts import toArgv
from scripts import biggest

def start(_argv):

    args = parseArgv(_argv)
    # expand all system paths
    realpath = lambda pathy: os.path.realpath(os.path.expanduser(pathy))

    SIZES = []
    INDEX = args['o']
    TILESIZE = args['s']
    N_TOP_IDS = args['n'] + 1
    DATA = realpath(args['hd5'])
    ROOTDIR = realpath(args['out'])
    STLFOLDER = os.path.join(ROOTDIR, 'stl')
    X3DFOLDER = os.path.join(ROOTDIR, 'x3d')
    COUNTPATH = os.path.join(ROOTDIR, 'count.txt')
    ALL_IDS = biggest(DATA,COUNTPATH,s=TILESIZE)[-N_TOP_IDS:-1]

    with h5py.File(DATA, 'r') as df:
        SIZES = df[df.keys()[0]].shape
        ntiles = np.array(SIZES)//TILESIZE
        z_base = 1./ntiles[0]
        y_base = z_base/ntiles[1]
        x_base = y_base/ntiles[2]

    subvols = zip(*np.where(np.ones(ntiles)))

    for z,y,x in subvols:
        ThreeD.run(DATA, z, y, x, STLFOLDER, TILESIZE, ALL_IDS)

        z_done = z*z_base + y*y_base + x*x_base
        print("%.1f%% done with stl" % (100*z_done) )

    DIMZ,DIMY,DIMX = SIZES
    ThreeD.create_website(STLFOLDER, X3DFOLDER, ALL_IDS, INDEX, DIMX, DIMY, DIMZ)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'hd5': 'input hd5 file (default in.h5)',
        'out': 'output web directory (default www)',
        'o': 'output filename (default index.html)',
        's': 'load h5 in s*s*s chunks (default 256)',
        'n': 'make meshes for the top n ids (default 1)',
        'help': 'Make an hdf5 file into html meshes!'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('hd5', default='in.h5', nargs='?', help=help['hd5'])
    parser.add_argument('out', default='www', nargs='?', help=help['out'])
    parser.add_argument('-s', type=int, default=256, help=help['s'])
    parser.add_argument('-n', type=int, default=1, help=help['n'])
    parser.add_argument('-o', default='index.html', help=help['o'])

    # attain all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

