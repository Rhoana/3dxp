import glob
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
    TOP_DEEP = args['deep']
    N_TOP_IDS = args['number'] + 1
    ROOTOUT = realpath(args['out'])
    ROOTIN = realpath(args['root'])
    WWW = realpath(args['www'])
    STLFOLDER = sharepath(ROOTOUT, 'stl')
    X3DFOLDER = sharepath(ROOTOUT, 'x3d')
    DATA = sharepath(ROOTIN, args['ids'])
    PNGS = sharepath(ROOTIN, args['png'])
    IMAGE = sharepath(ROOTIN, args['raw'])
    # Count most spread or deep ids 
    BIG_IDS, BIG_COUNTS = biggest(DATA, sharepath(ROOTOUT,'spread_count.tx'), s=TILESIZE)
    DEEP_IDS, DEEP_COUNTS = deepest(DATA, sharepath(ROOTOUT,'deep_count.tx'), s=TILESIZE)
    top_ids = [BIG_IDS, DEEP_IDS][TOP_DEEP][-N_TOP_IDS:-1]
    big_ids = [np.where(BIG_IDS == tid)[0][0] for tid in top_ids]
    top_counts = BIG_COUNTS[big_ids]

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

        # Only search volume for ids that need more stl files
        re_path = [os.path.join(STLFOLDER,str(intid)+'_*') for intid in top_ids]

        for z,y,x in subvols:
            found_counts = [len(glob.glob(re_file)) for re_file in re_path]
            top_stl_ids = top_ids[top_counts>found_counts]
            if len(top_stl_ids):
                ThreeD.run(DATA, z, y, x, STLFOLDER, TILESIZE, top_stl_ids)

            z_done = z*z_base + y*y_base + x*x_base
            print("%.1f%% done with stl" % (100*z_done) )

    # Load stl (and cached x3d) to make x3dom html
    ThreeD.create_website(STLFOLDER, X3DFOLDER, top_ids, INDEX, *sizes, www=WWW)
    # Link full image stack and create cube sides
    sides(X3DFOLDER, IMAGE, PNGS)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'deep': 'rank top ids by depth (default 0)',
        'ids': 'input hd5 id volume (default in.h5)',
        'out': 'output web directory (default .)',
        'raw': 'input raw h5 volume (default raw.h5)',
        'png': 'input raw png folder (default pngs)',
        'R': 'root of both hd5 volumes (default .)',
        'f': 'output filename (default index.html)',
        's': 'load h5 in s*s*s chunks (default 256)',
        'n': 'make meshes for the top n ids (default 1)',
        'w': 'folder containing js/css (default www)',
        'help': 'Make an hdf5 file into html meshes!'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('ids', default='in.h5', help=help['ids'])
    parser.add_argument('raw', default='raw.h5', help=help['raw'])
    parser.add_argument('png', default='pngs', help=help['png'])
    parser.add_argument('out', default='.', nargs='?', help=help['out'])
    parser.add_argument('-f','--index', default='index.html', help=help['f'])
    parser.add_argument('-D','--deep',type=int, default=0, help=help['deep'])
    parser.add_argument('-s','--size', type=int, default=256, help=help['s'])
    parser.add_argument('-n','--number',type=int, default=1, help=help['n'])
    parser.add_argument('-w','--www', default='www', help=help['w'])
    parser.add_argument('-R','--root', default='.', help=help['R'])

    # attain all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

