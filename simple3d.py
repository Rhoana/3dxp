import os, h5py
import numpy as np
import sys, argparse
from threed import ThreeD



def main(_args):

    args = parseArgv(_args)
    # expand all system paths
    realpath = lambda pathy: os.path.realpath(os.path.expanduser(pathy))

    N_TOP_IDS = args['n'] + 1
    ROOTDIR = realpath(args['out'])
    DATA = realpath(args['hd5'])
    STLFOLDER = os.path.join(ROOTDIR ,'stl')
    X3DFOLDER = os.path.join(ROOTDIR , 'x3d')
    ALL_IDS = np.loadtxt(os.path.join(ROOTDIR,'out.txt'),dtype=np.uint32)[-N_TOP_IDS:-1]
    TILESIZE = args['s']
    INDEX = args['o']
    SIZES = []

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

def toArgv(args, **flags):
    keyvals = flags.items()
    all_tokens = range(2*len(keyvals))
    endash = lambda fkey: '-'+fkey if len(fkey) == 1 else '--'+fkey
    enflag = lambda kv,fl: str(kv[fl]) if fl else endash(str(kv[fl]))
    kargv = [enflag(keyvals[i//2],i%2) for i in all_tokens]
    return ['main'] + list(map(str,args)) + kargv

def parseArgv(argv):
    sys.argv = argv

    help = {
        'hd5': 'input hd5 file (default hd5)',
        'out': 'output web directory (default www)',
        'o': 'output filename (default index.html)',
        's': 'load h5 in s*s*s chunks (default 256)',
        'n': 'make meshes for the top n ids (default 1)',
        'help': 'Make an hdf5 file into html meshes!'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('hd5', default='hd5', nargs='?', help=help['hd5'])
    parser.add_argument('out', default='www', nargs='?', help=help['out'])
    parser.add_argument('-s', type=int, default=256, help=help['s'])
    parser.add_argument('-n', type=int, default=1, help=help['n'])
    parser.add_argument('-o', default='index.html', help=help['o'])

    # attain all arguments
    return vars(parser.parse_args())

def start(_args, **_flags):
    main(toArgv(_args,**_flags))

if __name__ == "__main__":
    main(sys.argv)

