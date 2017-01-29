import os, h5py
import numpy as np
from mahotas.histogram import fullhistogram

HOME = os.path.expanduser('~')
DATA = HOME + '/2017/data/seg_100x4x4/stitched_seg.h5'
ROOTDIR = HOME + '/2017/winter/3dxp1338/X3DOM/seg_100x4x4'
N_IDS = 50
INDEX = 'one.html'
TILESIZE = 256
COUNTS = np.zeros(1)

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
        print("%.1f%% done" % (100*z_done) )

    topIDs = np.argsort(COUNTS)[-N_IDS:-1].astype(np.uint32)
    np.savetxt(os.path.join(ROOTDIR,'out.txt'), topIDs, fmt='%i', delimiter=',')
