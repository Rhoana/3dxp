import os, h5py
import numpy as np
from threed import ThreeD

HOME = os.path.expanduser('~')
DATA = HOME + '/2017/data/seg_100x4x4/stitched_seg.h5'
ROOTDIR = HOME + '/2017/winter/3dxp1338/X3DOM/seg_100x4x4/'
STLFOLDER = ROOTDIR + 'stl'
X3DFOLDER = ROOTDIR + 'x3d'
ALL_IDS = np.loadtxt(os.path.join(ROOTDIR,'out.txt'),dtype=np.uint32)[-3:-1]
INDEX = 'one.html'
TILESIZE = 256
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
