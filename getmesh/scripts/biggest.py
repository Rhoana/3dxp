import sys, argparse
from toArgv import toArgv
from mahotas.histogram import fullhistogram
import numpy as np
import os, h5py

def start(_argv):
    args = parseArgv(_argv)

    DATA = args['hd5']
    TILESIZE = args['s']
    COUNTPATH = args['out']
    COUNTS = np.zeros(1)

    if os.path.exists(COUNTPATH):
        return np.loadtxt(COUNTPATH,dtype=np.uint32)

    with h5py.File(DATA, 'r') as df:
        vol = df[df.keys()[0]]
        sizes = vol.shape
        ntiles = np.array(sizes)//TILESIZE

        subvols = zip(*np.where(np.ones(ntiles)))
        z_base = 1./ntiles[0]
        y_base = z_base/ntiles[1]
        x_base = y_base/ntiles[2]

        for z,y,x in subvols:
            new_count = fullhistogram(vol[z:(512+z), y:(512+y), x:(512+x)])
            diff_count = len(new_count) - len(COUNTS)
            if diff_count > 0:
               COUNTS = np.r_[COUNTS, np.zeros(diff_count)]
            if diff_count < 0:
               new_count = np.r_[new_count, np.zeros(-diff_count)]

            COUNTS = COUNTS + new_count

            z_done = z*z_base + y*y_base + x*x_base
            print("%.1f%% done with counting" % (100*z_done) )

        topIDs = np.argsort(COUNTS).astype(np.uint32)
        np.savetxt(COUNTPATH, topIDs, fmt='%i')
        return topIDs

def parseArgv(argv):
    sys.argv = argv

    help = {
        's': 'load h5 in s*s*s chunks (default 256)',
        'out': 'output count text file (defalt count.txt)',
        'hd5': 'input segmentation hd5 file (default in.h5)',
        'help': 'Find biggest IDs in segmented volume'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('hd5', default='in.h5', nargs='?', help=help['hd5'])
    parser.add_argument('out', default='count.txt', nargs='?', help=help['out'])
    parser.add_argument('-s', type=int, default=256, help=help['s'])

    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    start(sys.argv)


