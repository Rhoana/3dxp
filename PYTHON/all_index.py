import glob
import os, h5py
import numpy as np
import sys, argparse
from threed import ThreeD

def start(_argv):

    args = parseArgv(_argv)
    # expand all system paths
    homepath = lambda pathy: os.path.expanduser(pathy)
    realpath = lambda pathy: os.path.realpath(homepath(pathy))
    sharepath = lambda share,pathy: os.path.join(share, homepath(pathy))

    INDEX = args['index']
    ROOTOUT = realpath(args['out'])
    X3DFOLDER = sharepath(ROOTOUT, 'x3d')
    # Join only specific indexes
    LIST = []
    if args['list'] != '':
        # If list is range, actualize it
        if '-' in args['list']:
            LIST = [int(v) for v in args['list'].split('-')]
            LIST = range(*LIST)
        else:
            LIST = [int(v) for v in args['list'].split(':')]

    # Load stl (and cached x3d) to make x3dom html
    ThreeD.merge_website(X3DFOLDER, INDEX, LIST)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'out': 'output web directory (default .)',
        'f': 'output filename (default index.html)',
        'help': 'Make an hdf5 file into html meshes!',
        'l': 'make meshes for : separated list of ids',
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('out', default='.', nargs='?', help=help['out'])
    parser.add_argument('-f','--index', default='index.html', help=help['f'])
    parser.add_argument('-l','--list', default='', help=help['l'])    

    # attain all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

