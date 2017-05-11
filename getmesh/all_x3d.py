import glob
import os, h5py
import numpy as np
import sys, argparse
from threed import ThreeD
from scripts import biggest
from scripts import deepest
from scripts import sides

def start(_argv):

    args = parseArgv(_argv)
    # expand all system paths
    homepath = lambda pathy: os.path.expanduser(pathy)
    realpath = lambda pathy: os.path.realpath(homepath(pathy))
    sharepath = lambda share,pathy: os.path.join(share, homepath(pathy))

    WHICH_ID = args['top']
    TOP_DEEP = args['deep']
    N_TOP_IDS = args['number'] + 1
    WWW = realpath(args['www'])
    PNGS = realpath(args['png'])
    IMAGE = realpath(args['raw'])
    ROOTOUT = realpath(args['out'])
    STLFOLDER = sharepath(ROOTOUT, 'stl')
    X3DFOLDER = sharepath(ROOTOUT, 'x3d')


    #
    # IF A LIST OF IDS IS PASSED
    #
    if args['list'] != '':
        LIST = [int(v) for v in args['list'].split(',')]

        # Load ids and make x3d files
        if os.path.exists(IMAGE):
            with h5py.File(IMAGE, 'r') as df:
                full_shape = df[df.keys()[0]].shape

        # Run conversion on only one particular ID
        if WHICH_ID >= 0:
            LIST = [LIST[WHICH_ID]]

        # Load stl (and cached x3d) to make x3dom html
        ThreeD.create_website(STLFOLDER, X3DFOLDER, LIST, *full_shape, www=WWW)
        # Link full image stack and create cube sides
        sides(X3DFOLDER, IMAGE, PNGS)

        return



        

    # Count the biggest and the deepest ids 
    BIG_IDS, BIG_COUNTS = biggest('', sharepath(ROOTOUT, 'spread_count.txt'), 1)
    DEEP_IDS, DEEP_COUNTS = deepest('', sharepath(ROOTOUT, 'deep_count.txt'), 1)
    # Get the id numbers to use to generate meshes
    top_ids = [BIG_IDS, DEEP_IDS][TOP_DEEP][-N_TOP_IDS:-1]

    # Load ids and make x3d files
    if os.path.exists(IMAGE):
        with h5py.File(IMAGE, 'r') as df:
            full_shape = df[df.keys()[0]].shape

    # Run conversion on only one particular ID
    if WHICH_ID >= 0:
        top_ids = [top_ids[WHICH_ID]]
        INDEX = '{}_{}'.format(top_ids[0], INDEX)

    # Load stl (and cached x3d) to make x3dom html
    ThreeD.create_website(STLFOLDER, X3DFOLDER, top_ids, INDEX, *full_shape, www=WWW)
    # Link full image stack and create cube sides
    sides(X3DFOLDER, IMAGE, PNGS)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'out': 'output web directory (default .)',
        'raw': 'input raw h5 volume (default raw.h5)',
        'png': 'input raw png folder (default pngs)',
        'd': 'rank top ids by depth (default 0)',
        'w': 'folder containing js/css (default www)',
        'n': 'make meshes for the top n ids (default 1)',
        'l': 'make meshes for specific ids',        
        't': 'make for only the top id (default make all)',
        'help': 'Make an hdf5 file into html meshes!'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('raw', default='raw.h5', help=help['raw'])
    parser.add_argument('png', default='pngs', help=help['png'])
    parser.add_argument('out', default='.', nargs='?', help=help['out'])
    parser.add_argument('-n','--number', type=int, default=1, help=help['n'])
    parser.add_argument('-l','--list', default='', help=help['l'])    
    parser.add_argument('-t','--top', type=int, default=-1, help=help['t'])
    parser.add_argument('-d','--deep',type=int, default=0, help=help['d'])
    parser.add_argument('-w','--www', default='www', help=help['w'])

    # attain all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

