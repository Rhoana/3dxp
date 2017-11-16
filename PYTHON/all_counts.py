import glob
import os, h5py
import numpy as np
import sys, argparse
from threed import ThreeD
from scripts import biggest
from scripts import deepest
from scripts import highest
from scripts import widest

from conversion import common

def start(_argv):

    args = parseArgv(_argv)
    # expand all system paths
    homepath = lambda pathy: os.path.expanduser(pathy)
    realpath = lambda pathy: os.path.realpath(homepath(pathy))
    sharepath = lambda share,pathy: os.path.join(share, homepath(pathy))

    BLOCK = args['block']
    SAVE_DEEP = args['deep']
    ROOTOUT = realpath(args['out'])
    DATA = realpath(args['ids'])
    # Make sure output path exists
    common.make_path(ROOTOUT)
    # Count most spread or deep ids 
    if SAVE_DEEP == 1:
        deepest(DATA, sharepath(ROOTOUT,'deep_count.txt'), BLOCK)
    elif SAVE_DEEP == 2:
        highest(DATA, sharepath(ROOTOUT,'high_count.txt'), BLOCK)
    elif SAVE_DEEP == 3:
        widest(DATA, sharepath(ROOTOUT,'wide_count.txt'), BLOCK)
    else:
        biggest(DATA, sharepath(ROOTOUT,'spread_count.txt'), BLOCK)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'ids': 'input hd5 id volume (default in.h5)',
        'out': 'output text list directory (default .)',
        'b': 'Number of blocks in each dimension (default 10)',
        'help': 'Save the deepest or the biggest cells',
        'd': 'save top ids by depth (default 0)',
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('-b','--block', type=int, default=10, help=help['b'])
    parser.add_argument('-d','--deep',type=int, default=0, help=help['d'])
    parser.add_argument('ids', help=help['ids'])
    parser.add_argument('out', help=help['out'])

    # attain all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

