import os, h5py
import numpy as np
import sys, argparse
from threed import ThreeD
from scripts import *

def start(_argv):

    args = parseArgv(_argv)
    # expand all system paths
    homepath = lambda pathy: os.path.expanduser(pathy)
    realpath = lambda pathy: os.path.realpath(homepath(pathy))
    sharepath = lambda share,pathy: os.path.join(share, homepath(pathy))

    INDEX = args['index']
    TILESIZE = args['size']
    N_TOP_IDS = args['number'] + 1
    ROOTOUT = realpath(args['out'])
    ROOTIN = realpath(args['root'])
    STLFOLDER = sharepath(ROOTOUT, 'stl')
    X3DFOLDER = sharepath(ROOTOUT, 'x3d')
    DATA = sharepath(ROOTIN, args['ids'])
    IMAGE = sharepath(ROOTIN, args['raw'])
    COUNTPATH = sharepath(ROOTOUT, 'count.txt')
    ALL_IDS = biggest(DATA,COUNTPATH,s=TILESIZE)[-N_TOP_IDS:-1]
    #sides(rel)

    # Load ids and make stl files
    if os.path.exists(DATA):
        with h5py.File(DATA, 'r') as df:
            sizes = df[df.keys()[0]].shape
            ntiles = np.array(sizes)//TILESIZE

        # Get percent ranges
        z_base = 1./ntiles[0]
        y_base = z_base/ntiles[1]
        x_base = y_base/ntiles[2]

        # Get all possible tile offsets
        subvols = zip(*np.where(np.ones(ntiles)))

        for z,y,x in subvols:
            ThreeD.run(DATA, z, y, x, STLFOLDER, TILESIZE, ALL_IDS)

            z_done = z*z_base + y*y_base + x*x_base
            print("%.1f%% done with stl" % (100*z_done) )

    # Load stl (and cached x3d) to make x3dom html
    ThreeD.create_website(STLFOLDER, X3DFOLDER, ALL_IDS, INDEX, *sizes)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'ids': 'input hd5 id volume (default in.h5)',
        'out': 'output web directory (default www)',
        'raw': 'input raw h5 volume (default raw.h5)',
        'R': 'root of both hd5 volumes (default .)',
        'o': 'output filename (default index.html)',
        's': 'load h5 in s*s*s chunks (default 256)',
        'n': 'make meshes for the top n ids (default 1)',
        'help': 'Make an hdf5 file into html meshes!'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('out', default='www', help=help['out'])
    parser.add_argument('ids', default='in.h5', nargs='?', help=help['ids'])
    parser.add_argument('raw', default='raw.h5', nargs='?', help=help['raw'])
    parser.add_argument('-o','--index', default='index.html', help=help['o'])

    parser.add_argument('-s','--size', type=int, default=256, help=help['s'])
    parser.add_argument('-n','--number',type=int, default=1, help=help['n'])

    parser.add_argument('-R','--root', default='.', help=help['R'])

    # attain all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

