import sys, argparse
from toArgv import toArgv
import numpy as np
import os, h5py

def sort(counts):
    keysort = np.argsort(counts).astype(np.uint32)
    return [keysort, counts[keysort]]

def start(_argv):
    args = parseArgv(_argv)

    DATA = args['hd5']
    TILESIZE = args['s']
    COUNTPATH = args['out']
    COUNTS = np.array([],dtype=np.uint32)

    if os.path.exists(COUNTPATH):
        COUNTS = np.loadtxt(COUNTPATH,dtype=np.uint32)
        return sort(COUNTS)

    with h5py.File(DATA, 'r') as df:
        vol = df[df.keys()[0]]
        ntiles = np.array(vol.shape)//TILESIZE

        subvols = zip(*np.where(np.ones(ntiles[1:])))
        subdepths = np.arange(ntiles[0])
        z_base = 1./ntiles[0]
        y_base = z_base/ntiles[1]
        x_base = y_base/ntiles[2]

        def even_count(old_c, new_c):
            diff_count = len(new_c) - len(old_c)
            if diff_count > 0:
                old_c = np.r_[old_c, np.zeros(diff_count, dtype=old_c.dtype)]
            if diff_count < 0:
                new_c = np.r_[new_c, np.zeros(-diff_count, dtype=new_c.dtype)]
            return old_c, new_c

        for z in subdepths:
            z_count = np.array([],dtype=np.bool)
            for y,x in subvols:

                zo,ze = np.array([z,z+1])*TILESIZE
                yo,ye = np.array([y,y+1])*TILESIZE
                xo,xe = np.array([x,x+1])*TILESIZE
                in_block = np.unique(vol[zo:ze, yo:ye, xo:xe])
                new_count = np.zeros(max(in_block)+1, dtype=np.bool)
                new_count[in_block] = True

                z_count, new_count = even_count(z_count, new_count)
                z_count = np.logical_or(z_count, new_count)

                z_done = z*z_base + y*y_base + x*x_base
                print("%.1f%% done with counting" % (100*z_done) )

            COUNTS, z_count = even_count(COUNTS, z_count)
            COUNTS = COUNTS + z_count.astype(np.uint32)

        np.savetxt(COUNTPATH, COUNTS, fmt='%i')
        return sort(COUNTS)

def parseArgv(argv):
    sys.argv = argv

    help = {
        's': 'load h5 in s*s*s chunks (default 256)',
        'out': 'output count text file (defalt deep_count.txt)',
        'hd5': 'input segmentation hd5 file (default in.h5)',
        'help': 'Find deepest IDs in segmented volume'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('hd5', default='in.h5', nargs='?', help=help['hd5'])
    parser.add_argument('out', default='deep_count.txt', nargs='?', help=help['out'])
    parser.add_argument('-s', type=int, default=256, help=help['s'])

    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    start(sys.argv)


